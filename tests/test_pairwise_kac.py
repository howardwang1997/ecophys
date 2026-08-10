from __future__ import annotations

import pytest
import torch

from ecomd.models.potentials import PairwisePotential, StochasticPairwisePotential


@pytest.mark.parametrize("kac_normalize", [False, True])
def test_full_neighbour_stochastic_energy_matches_dense(
    kac_normalize: bool,
) -> None:
    torch.manual_seed(41)
    dense = PairwisePotential(d=3, hidden=7, kac_normalize=kac_normalize).double()
    sampled = StochasticPairwisePotential(
        d=3,
        hidden=7,
        k_random=50,
        kac_normalize=kac_normalize,
    ).double()
    assert sampled.net is not None
    sampled.net.load_state_dict(dense.net.state_dict())
    dense_state = torch.randn(6, 3, dtype=torch.float64, requires_grad=True)
    sampled_state = dense_state.detach().clone().requires_grad_(True)
    dense_energy = dense(dense_state)
    sampled_energy = sampled(sampled_state)

    torch.testing.assert_close(
        sampled_energy,
        dense_energy,
        rtol=1e-13,
        atol=1e-13,
    )
    dense_force = -torch.autograd.grad(dense_energy, dense_state)[0]
    sampled_force = -torch.autograd.grad(sampled_energy, sampled_state)[0]
    torch.testing.assert_close(sampled_force, dense_force, rtol=1e-12, atol=1e-12)


def test_kac_constant_kernel_has_extensive_energy() -> None:
    n_agents = 6
    potential = StochasticPairwisePotential(
        d=2,
        hidden=4,
        k_random=50,
        kac_normalize=True,
    )
    assert potential.net is not None
    with torch.no_grad():
        for parameter in potential.net.parameters():
            parameter.zero_()
        final = potential.net[-1]
        assert isinstance(final, torch.nn.Linear)
        final.bias.fill_(2.0)

    energy = potential(torch.zeros(n_agents, 2))
    assert energy.item() == pytest.approx(float(n_agents))


def test_stochastic_pairwise_rejects_invalid_partner_counts() -> None:
    with pytest.raises(ValueError, match="k_random"):
        StochasticPairwisePotential(d=2, k_random=0)

    potential = StochasticPairwisePotential(d=2, k_random=5)
    with pytest.raises(ValueError, match="at least two"):
        potential(torch.zeros(1, 2))
