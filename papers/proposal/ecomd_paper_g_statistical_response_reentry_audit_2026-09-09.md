# Paper G: finite-window statistics, physical measures and forced response

**PRIVATE / INTERNAL — outcome-blind re-entry audit, not public research evidence.**
Session started 2026-09-09T08:57:02Z; literature cutoff 2026-09-09.
Reading and algebra were interleaved; no prospective forecast is claimed.

**Decision: not_trigger.** The inspected works do not make opposite predictions
under the same state, target and assumptions. Generic statistical-fidelity and
forced-response diagnostics have direct parents. Two elementary control bundles
are retained below; neither is a new learning method or a refutation of the
selected papers. No contribution blocker is removed, and no topic cycle starts.

## 1. Connection and scope

The repository contains stateful stochastic simulation and conservative,
autoregressive PDE learning. This makes statistical fidelity, state observation
and specified physical forcing relevant to Paper G. No historical experimental
outcomes, checkpoint, trajectory array or notebook output was accessed here.
Paper D's original and post-hoc evidence roles remain unchanged.

The related terminal formulations are `paper_g_physical_history_impulse_response`
and `ncs_invariant_calibration_v4`. Their recorded generic-method and sensitivity
prior blockers are not removed by changing the application to chaotic or climate
dynamics. This audit examines a proposed primary-disagreement trigger before
any candidate harvesting. It does not close the whole field of learned dynamics.

## 2. What the primary results actually compare

| Primary work and inspected scope | Target and conditions | Decision consequence |
|---|---|---|
| [Park, Yang and Chandramoorthy, arXiv2411.06311v2](https://arxiv.org/html/2411.06311v2), sections 2–3, Assumption 1, Theorem 1 and Appendix C.7 | Long-run physical measures; the theorem uses strong C1 control along generated orbits and an additional condition on the typicality of shadowing orbits. Unrolling is also compared with Jacobian training. | Neither ordinary held-out Jacobian error nor finite-window reconstruction alone is a universal guarantee. The statistical-fidelity/Jacobian-training program is direct prior art. |
| [Boddupalli and Moehlis, arXiv2608.22112v1](https://arxiv.org/html/2608.22112v1), Appendix C, propositions 7–8 | Mean and variance differences of paired finite trajectories are bounded using their RMSE. | This compares statistics on those same rows. It does not by itself bound an unobserved stationary measure or a forced response. It therefore does not contradict the preceding result. |
| [Falasca, arXiv2506.22552v8](https://arxiv.org/html/2506.22552v8), sections II–III | Stochastic reduced models, complete versus partial state observations, stationary statistics and impulse/forced responses; the triad's dynamics and forcing conventions are specified. | Direct parent for studying forced response beyond unforced statistics and for state/closure controls. A selected full-state success is not a universal theorem about arbitrary sampling or actuation. |

The [official NeurIPS record](https://papers.nips.cc/paper_files/paper/2024/hash/4dc57702c987e1e72f0dd2921edb5ded-Abstract-Conference.html)
confirms Park et al. as NeurIPS 2024 Main Conference work. Technical reading here
is tied to arXiv v2; final conference-body identity is not assumed. For Falasca,
an initial v2 read was superseded for this comparison by the selected v8 sections;
the arXiv submission history identifies v8 as 24 January 2026. No method claim is
based on an unversioned search snippet or a rendered title-page date.

## 3. Control A: paired moments do not settle long-run measures

Let X and Y be m-by-d matrices of paired states, and let

    E = ||X-Y||_F / sqrt(m),
    H = I_m - 11^T/m.

For the vectors of column means, Jensen/Cauchy–Schwarz gives
||mean(X)-mean(Y)||_2 <= E. For column population standard deviations,
s_i(X)=||H X_:i||_2/sqrt(m). The reverse triangle inequality gives

    sum_i |s_i(X)-s_i(Y)|^2
       <= ||H(X-Y)||_F^2/m <= E^2.

Thus even the standard-deviation vector is Lipschitz in the paired data under
this convention, including at zero variance. This elementary observation does
not require a lower variance bound. It is not a novel statistics theorem; its
purpose is to keep the finite-data target explicit. It makes no claim that
minimizing one empirical objective orders every other error monotonically.

To expose the missing time scale, consider two flows on x in [0,1], with epsilon>0:

    true:    x_dot = -epsilon*x,
    learned: x_dot = epsilon*(1-x),
    common initial condition x(0)=0.

Both have a unique globally attracting equilibrium. The true solution is zero;
the other is 1-exp(-epsilon*t). On any fixed window [0,T], their paired error
is at most epsilon*T. Their drift derivatives agree exactly and the uniform
drift difference is epsilon. Nevertheless, the two physical measures are
delta_0 and delta_1, at coordinate Wasserstein-1 distance one.

The family changes epsilon: this is a failure of a **uniform** conclusion without
a relaxation-rate condition, not discontinuity at a fixed positive stability
margin. The relaxation time is 1/epsilon, so a window long enough to resolve it
exposes the discrepancy. Keeping epsilon fixed and taking the drift error to zero
is a different limit. No uniformly hyperbolic theorem is refuted by this family.

An exactly conserving embedding uses y=1-x, with y_dot=-x_dot. Both flows preserve
x+y=1 and the nonnegative simplex. Conservation therefore does not remove this
time-scale issue. In the two-dimensional Euclidean state the distances acquire
the corresponding sqrt(2) factor. This is a standard perturbation/relaxation
control, not evidence of a trained model's actual behavior.

## 4. Control B: full sampled path law can leave held forcing ambiguous

This control strengthens the unforced information budget all the way to the
exact full-state sampled Markov kernel. Let gamma,sigma,tau>0, let

    J = [[0,-1],[1,0]],
    A_k = -gamma*I + omega_k*J,
    omega_k = 2*pi*k/tau, k integer,
    dX = A_k X dt + sigma dW.

Every member is a stable, nondegenerate two-dimensional Ornstein–Uhlenbeck
process. At the fixed physical sampling interval tau,

    exp(tau*A_k) = r*I,  r=exp(-gamma*tau),
    Q_tau = sigma^2*(1-r^2)/(2*gamma) * I.

The covariance follows by integrating sigma^2*exp(s*A_k)*exp(s*A_k^T).
Consequently all members have exactly the same sampled transition kernel,
stationary covariance sigma^2/(2*gamma)*I, and every finite-dimensional sampled
path distribution under a common initial law. The sampled mean-map Jacobian is
also r*I for every k. More passive observations at these same times cannot
distinguish the family.

Now apply the **same** physical constant force b*z throughout [0,tau]. Its gain is

    D_k b = integral_0^tau exp(s*A_k)b ds
          = (1-r)*(gamma*I+omega_k*J)/(gamma^2+omega_k^2) * b.

For b=(1,0), the second coordinate has zero mean response at k=0 and a nonzero
response at k!=0. This is not a change of units, sampling clock, state projection,
or force definition: the indistinguishable passive generators differ in their
unresolved rotation frequency. The force distinguishes those generators.

The decisive **null** is a grid-time instantaneous state reset X -> X+b, followed
by autonomous evolution. Its response at every later sampling time is r^j*b for
all k. The example therefore does not overturn the earlier current-time-impulse
control by silently substituting a held force. It also does not claim an alias in
Falasca's chosen triad, whose governing and numerical protocols are supplied.

This is classical matrix-exponential system aliasing; see
[Yue, Thunberg and Goncalves, 2016](https://arxiv.org/abs/1605.06973), whose primary
abstract was inspected for the method collision. The OU calculation above is
self-contained, not attributed to an unread section of that paper. In this
rotation family a valid prior frequency band, additional resolved observation
times, or assigned forcing can remove the alias. Such extra information changes
the identification contract; no general nonlinear recovery guarantee follows.

## 5. Re-entry decision and next decisive requirement

Three distinct targets must stay separate: finite-window paired moments,
long-run physical measures, and responses to specified actions. No matched
opposite prediction survived the primary comparison. The two diagnostic bundles
are elementary parent reductions, not new counterexamples to the selected works.

Future proposals in this family must state their relaxation/typicality conditions,
sampling and continuous-generator assumptions, physical actuator timing, and
the exact target. Improving a forecast loss, adding generic Jacobian supervision,
or demonstrating a standard passive-observation ambiguity does not establish
an independent contribution. A viable new topic still requires a result beyond
these parents and a qualified same-target truth/confirmation contract.

The graph gains the source collisions and reusable controls; previous cycle
records and forecasts remain untouched. No new raw question, F3, probability,
machine card, implementation, simulation, outcome access or GPU work is authorized.
The broader Paper G objective remains active.
