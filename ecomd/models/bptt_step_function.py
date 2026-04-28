"""Custom torch.autograd.Function wrapping a single EcoMD simulator step.

Motivation
----------
The standard ``rollout_chunk`` calls ``sim.step()`` chunk_steps times with
``create_graph=True`` for force computation. This pins each step's V-graph
through the resulting f_cons.grad_fn chain, which propagates forward
through s_next → next-step's input → next-step's f_cons → ...

Net effect: peak memory ≈ chunk_steps × per_step_V_graph regardless of
whether ``torch.utils.checkpoint`` is used at the chunk level — because
the standard checkpoint API can't release V-graphs that escape via output
tensors' grad_fn chains under ``create_graph=True``.

This module's :class:`EcoMDStepFunction` implements a per-step custom
autograd.Function that:

1. **Forward**: runs the step in ``no_grad`` (no autograd graph kept). Saves
   tensor inputs + RNG state in ``ctx`` for backward. The Function's outputs
   are *opaque* to the outer autograd graph — the chain from one step to
   the next is mediated by the Function nodes, NOT by V-graph chains.

2. **Backward**: locally restores RNG, re-runs ``sim.step()`` ONCE with
   ``create_graph=True`` to build a fresh per-step V-graph. Propagates
   upstream gradients via ``torch.autograd.backward(outputs, grad_tensors=...)``,
   which automatically populates ``.grad`` of the input tensors and of all
   ``sim.parameters()`` (since they were used in the local forward pass).
   After backward, the local graph is released.

3. **Memory**: peak memory at backward time ≈ ONE step's V-graph (~3.5 GB
   at N=10K stochastic_mlp), regardless of chunk_steps. No accumulation
   across steps because each step's local graph is built and dropped
   independently.

4. **Compute**: forward uses no_grad, so it's actually faster than the
   default path (no graph construction). Backward runs forward once more
   per step to build the local graph — net compute is ~2× the original
   forward (similar to per-step gradient checkpointing). When chunk_steps
   is large, this is a worthwhile trade for the memory savings.

Constraints
-----------
- Generator state must be deterministic between forward and backward
  (we save ``generator.get_state()`` before forward, restore at backward).
- ``s_prev`` is treated as detached (gradient barrier between iterations
  is the standard truncated-BPTT convention).
- Multi-asset / twopop / regime / Hawkes all work because the Function
  wraps the OPAQUE ``sim.step()`` call — it doesn't care what's inside.
"""

from __future__ import annotations

from typing import Any

import torch
from torch import Tensor

from .price_formation import PriceState


class EcoMDStepFunction(torch.autograd.Function):
    """Wraps one ``sim.step()`` call as an opaque autograd Function.

    Forward output and input layout (positional-only for autograd):
      forward(ctx,
              sim, generator, gen_state_before, step_idx,
              has_hawkes, has_hawkes_long, has_regime,
              s, s_prev,
              lp, llr, vol, hk, hkl,        # PriceState as 5 scalars
              h_reg,                        # regime hidden state (zero placeholder if disabled)
              *params)                      # all sim.parameters() in registration order
      → (s_next, s_prev_next,
         lp_next, llr_next, vol_next, hk_next, hkl_next,
         h_reg_next,
         log_return)

    Note: ``s_prev_next`` is just ``s`` from this step (used by next iter).
    We don't return f_cons / f_diss / states / volumes etc. because they
    are diagnostic — the trainer only differentiates ``log_return`` (and
    indirectly through state continuity).
    """

    @staticmethod
    def forward(
        ctx,
        sim,
        generator,
        gen_state_before,
        step_idx: int,
        has_hawkes: bool,
        has_hawkes_long: bool,
        has_regime: bool,
        has_agent: bool,
        has_global: bool,
        s: Tensor,
        s_prev: Tensor,
        lp: Tensor,
        llr: Tensor,
        vol: Tensor,
        hk: Tensor,
        hkl: Tensor,
        h_reg: Tensor,
        h_agent: Tensor,
        h_global: Tensor,
        *params: Tensor,
    ) -> tuple[Tensor, ...]:
        # Save context for backward (Python objects)
        ctx.sim_ref = sim
        ctx.generator = generator
        ctx.gen_state_before = gen_state_before
        ctx.step_idx = int(step_idx)
        ctx.has_hawkes = bool(has_hawkes)
        ctx.has_hawkes_long = bool(has_hawkes_long)
        ctx.has_regime = bool(has_regime)
        ctx.has_agent = bool(has_agent)
        ctx.has_global = bool(has_global)
        ctx.n_params = len(params)

        # Save tensors for backward
        ctx.save_for_backward(s, s_prev, lp, llr, vol, hk, hkl,
                              h_reg, h_agent, h_global, *params)

        # Run step in no-grad → bounded memory, no autograd tape.
        # Detach inputs first to break any external autograd connections
        # (the input `s` may be the output of a previous Function.apply,
        # carrying a FunctionBackward grad_fn that could trip up the
        # subsequent enable_grad inside conservative_forces).
        with torch.no_grad():
            if generator is not None and gen_state_before is not None:
                generator.set_state(gen_state_before)

            s_in = s.detach()
            s_prev_in = s_prev.detach()
            ps = PriceState.from_tensors(
                (lp.detach(), llr.detach(), vol.detach(),
                 hk.detach(), hkl.detach()),
                step=ctx.step_idx,
                has_hawkes=ctx.has_hawkes,
                has_hawkes_long=ctx.has_hawkes_long,
            )
            h_regime_in = h_reg.detach() if ctx.has_regime else None
            h_agent_in = h_agent.detach() if ctx.has_agent else None
            h_global_in = h_global.detach() if ctx.has_global else None

            (s_next, ps_next, rec,
             h_regime_next, h_agent_next, h_global_next) = sim.step(
                s_in, s_prev_in, ps,
                generator=generator,
                create_graph=False,   # KEY: no V-graph kept beyond this call
                h_regime=h_regime_in,
                h_agent=h_agent_in,
                h_global=h_global_in,
                step_idx=ctx.step_idx,
            )

            ps_t = ps_next.to_tensors()
            zero = torch.zeros((), device=s.device, dtype=s.dtype)
            h_reg_out = h_regime_next if (ctx.has_regime and h_regime_next is not None) else zero
            h_agent_out = h_agent_next if (ctx.has_agent and h_agent_next is not None) else h_agent
            h_global_out = h_global_next if (ctx.has_global and h_global_next is not None) else h_global
            log_return = rec["log_return"].clone()

        # Outputs: clone to ensure they aren't aliased to internal tensors
        return (
            s_next.clone(),
            s.clone(),                # s_prev_next is just s (unchanged)
            ps_t[0].clone(),
            ps_t[1].clone(),
            ps_t[2].clone(),
            ps_t[3].clone(),
            ps_t[4].clone(),
            h_reg_out.clone(),
            h_agent_out.clone(),
            h_global_out.clone(),
            log_return,
        )

    @staticmethod
    def backward(ctx, *grad_outputs):
        # Unpack grads matching forward output order
        (g_s_next, g_s_prev_next, g_lp, g_llr, g_vol, g_hk, g_hkl,
         g_h_reg, g_h_agent, g_h_global, g_log_return) = grad_outputs

        # Restore inputs
        saved = ctx.saved_tensors
        s, s_prev, lp, llr, vol, hk, hkl, h_reg, h_agent, h_global = saved[:10]
        params = list(saved[10:])

        # Re-run forward LOCALLY with create_graph=True so we have a graph to
        # backprop through. This is the only place V-graph is materialised.
        with torch.enable_grad():
            # Restore RNG state — backward must use the same noise as forward
            if ctx.generator is not None and ctx.gen_state_before is not None:
                ctx.generator.set_state(ctx.gen_state_before)

            # Make leaves with requires_grad for inputs we want grad on.
            # State / price / regime tensors are cloned + grad-required.
            # params keep their original identity (they're nn.Parameter),
            # so they're already leaves with requires_grad=True.
            s_l = s.detach().clone().requires_grad_(True)
            s_prev_l = s_prev.detach().clone().requires_grad_(True)
            lp_l = lp.detach().clone().requires_grad_(True)
            llr_l = llr.detach().clone().requires_grad_(True)
            vol_l = vol.detach().clone().requires_grad_(True)
            hk_l = (hk.detach().clone().requires_grad_(True)
                    if ctx.has_hawkes else hk.detach())
            hkl_l = (hkl.detach().clone().requires_grad_(True)
                     if ctx.has_hawkes_long else hkl.detach())
            h_reg_l = (h_reg.detach().clone().requires_grad_(True)
                       if ctx.has_regime else h_reg.detach())
            h_agent_l = (h_agent.detach().clone().requires_grad_(True)
                         if ctx.has_agent else h_agent.detach())
            h_global_l = (h_global.detach().clone().requires_grad_(True)
                          if ctx.has_global else h_global.detach())

            ps_l = PriceState.from_tensors(
                (lp_l, llr_l, vol_l, hk_l, hkl_l),
                step=ctx.step_idx,
                has_hawkes=ctx.has_hawkes,
                has_hawkes_long=ctx.has_hawkes_long,
            )
            h_regime_l = h_reg_l if ctx.has_regime else None
            h_agent_in_l = h_agent_l if ctx.has_agent else None
            h_global_in_l = h_global_l if ctx.has_global else None

            (s_next_l, ps_next_l, rec_l,
             h_regime_next_l, h_agent_next_l, h_global_next_l) = ctx.sim_ref.step(
                s_l, s_prev_l, ps_l,
                generator=ctx.generator,
                create_graph=True,
                h_regime=h_regime_l,
                h_agent=h_agent_in_l,
                h_global=h_global_in_l,
                step_idx=ctx.step_idx,
            )

            ps_t_l = ps_next_l.to_tensors()
            zero = torch.zeros((), device=s.device, dtype=s.dtype)
            h_reg_out_l = (h_regime_next_l if (ctx.has_regime and h_regime_next_l is not None) else zero)
            h_agent_out_l = (h_agent_next_l if (ctx.has_agent and h_agent_next_l is not None) else h_agent_l)
            h_global_out_l = (h_global_next_l if (ctx.has_global and h_global_next_l is not None) else h_global_l)
            log_return_l = rec_l["log_return"]

            outputs = [
                s_next_l, s_l,                          # s_prev_next was s
                ps_t_l[0], ps_t_l[1], ps_t_l[2], ps_t_l[3], ps_t_l[4],
                h_reg_out_l,
                h_agent_out_l,
                h_global_out_l,
                log_return_l,
            ]
            grads = [g_s_next, g_s_prev_next, g_lp, g_llr, g_vol, g_hk, g_hkl,
                     g_h_reg, g_h_agent, g_h_global, g_log_return]

            # Filter out (output, grad) pairs where grad is None or output
            # is a non-grad placeholder (zero h_reg when has_regime=False, etc.)
            valid_outputs = []
            valid_grads = []
            for o, g in zip(outputs, grads):
                if g is None:
                    continue
                if not (isinstance(o, Tensor) and o.requires_grad):
                    continue
                valid_outputs.append(o)
                valid_grads.append(g)

            # Build input list — only include tensors with requires_grad.
            # Placeholder tensors (e.g. hk_l when has_hawkes=False) don't
            # require grad, so torch.autograd.grad would complain.
            # We keep a parallel position list to return zeros for those.
            state_inputs = [
                ("s", s_l),
                ("s_prev", s_prev_l),
                ("lp", lp_l),
                ("llr", llr_l),
                ("vol", vol_l),
                ("hk", hk_l),
                ("hkl", hkl_l),
                ("h_reg", h_reg_l),
                ("h_agent", h_agent_l),
                ("h_global", h_global_l),
            ]
            param_inputs = list(params)  # all nn.Parameters

            # Filter to only requires_grad inputs
            req_grad_inputs = [t for _, t in state_inputs if t.requires_grad] + \
                              [p for p in param_inputs if p.requires_grad]
            req_grad_keys = [n for n, t in state_inputs if t.requires_grad] + \
                            [f"__param_{i}" for i, p in enumerate(param_inputs) if p.requires_grad]

            if valid_outputs and req_grad_inputs:
                grads_subset = torch.autograd.grad(
                    valid_outputs, req_grad_inputs,
                    grad_outputs=valid_grads,
                    retain_graph=False,
                    create_graph=False,
                    allow_unused=True,
                )
                grad_by_key = dict(zip(req_grad_keys, grads_subset))
            else:
                grad_by_key = {}

            # Reconstruct gradients in forward-arg order
            def _g_or_zero(name: str, ref: Tensor) -> Tensor:
                g = grad_by_key.get(name)
                return g if g is not None else torch.zeros_like(ref)

            g_s = _g_or_zero("s", s_l)
            g_s_prev_in = _g_or_zero("s_prev", s_prev_l)
            g_lp_in = _g_or_zero("lp", lp_l)
            g_llr_in = _g_or_zero("llr", llr_l)
            g_vol_in = _g_or_zero("vol", vol_l)
            g_hk_in = _g_or_zero("hk", hk_l)
            g_hkl_in = _g_or_zero("hkl", hkl_l)
            g_h_reg_in = _g_or_zero("h_reg", h_reg_l)
            g_h_agent_in = _g_or_zero("h_agent", h_agent_l)
            g_h_global_in = _g_or_zero("h_global", h_global_l)

            param_grads = []
            for i, p in enumerate(param_inputs):
                if p.requires_grad:
                    g = grad_by_key.get(f"__param_{i}")
                    param_grads.append(g if g is not None else torch.zeros_like(p))
                else:
                    param_grads.append(torch.zeros_like(p))

        # Return gradients matching forward args layout
        return (
            None,            # sim
            None,            # generator
            None,            # gen_state_before
            None,            # step_idx
            None,            # has_hawkes
            None,            # has_hawkes_long
            None,            # has_regime
            None,            # has_agent
            None,            # has_global
            g_s,             # s
            g_s_prev_in,     # s_prev
            g_lp_in,         # lp
            g_llr_in,        # llr
            g_vol_in,        # vol
            g_hk_in,         # hk
            g_hkl_in,        # hkl
            g_h_reg_in,      # h_reg
            g_h_agent_in,    # h_agent
            g_h_global_in,   # h_global
            *param_grads,    # *params
        )


def step_via_function(
    sim,
    s: Tensor,
    s_prev: Tensor,
    price_state: PriceState,
    *,
    generator: torch.Generator | None,
    h_regime: Tensor | None,
    h_agent: Tensor | None,
    h_global: Tensor | None,
    step_idx: int,
) -> tuple[Tensor, Tensor, PriceState, Tensor | None, Tensor | None, Tensor | None, Tensor]:
    """Convenience wrapper that flattens PriceState → tensors, calls
    EcoMDStepFunction, and returns (s_next, s_prev_next, price_state_next,
    h_regime_next, h_agent_next, h_global_next, log_return)."""
    has_hawkes = price_state.hawkes_memory is not None
    has_hawkes_long = price_state.hawkes_memory_long is not None
    has_regime = h_regime is not None
    has_agent = h_agent is not None
    has_global = h_global is not None

    zero_h = torch.zeros((), device=s.device, dtype=s.dtype)
    h_reg_in = h_regime if has_regime else zero_h
    # h_agent placeholder shape must match the real one (N, d_memory) so
    # that grad outputs flow with consistent shapes.
    if has_agent:
        h_agent_in = h_agent
    else:
        d_mem = sim.cfg.agent_memory_d
        h_agent_in = torch.zeros((sim.cfg.n_agents, d_mem), device=s.device, dtype=s.dtype)
    if has_global:
        h_global_in = h_global
    else:
        d_g = sim.cfg.global_state_d
        h_global_in = torch.zeros((d_g,), device=s.device, dtype=s.dtype)

    ps_t = price_state.to_tensors()
    gen_state = (
        generator.get_state().clone() if generator is not None else None
    )

    params = tuple(sim.parameters())

    out = EcoMDStepFunction.apply(
        sim, generator, gen_state, step_idx,
        has_hawkes, has_hawkes_long, has_regime, has_agent, has_global,
        s, s_prev,
        ps_t[0], ps_t[1], ps_t[2], ps_t[3], ps_t[4],
        h_reg_in,
        h_agent_in,
        h_global_in,
        *params,
    )
    (s_next, s_prev_next, lp_n, llr_n, vol_n, hk_n, hkl_n,
     h_reg_n, h_agent_n, h_global_n, log_return) = out

    ps_next = PriceState.from_tensors(
        (lp_n, llr_n, vol_n, hk_n, hkl_n),
        step=step_idx + 1,
        has_hawkes=has_hawkes,
        has_hawkes_long=has_hawkes_long,
    )
    h_regime_next = h_reg_n if has_regime else None
    h_agent_next = h_agent_n if has_agent else None
    h_global_next = h_global_n if has_global else None
    return s_next, s_prev_next, ps_next, h_regime_next, h_agent_next, h_global_next, log_return
