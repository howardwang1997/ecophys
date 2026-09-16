# Paper G noise cancellation: support remains necessary

PRIVATE / INTERNAL. 2026-09-09 Session34. Goal remains active;this bounded
primary theorem-scope audit is progress,not a new topic or execution authority.

- Akashi et al.arXiv2606.26727v1(June25) Theorem1 and AppendixC were checked
  against original PDF pages7,14,15. Universal representation and iid zero-mean
  innovations do not alone identify dynamics at unvisited rollout states.
  Do not infer that the reported benchmarks fail: some protocols add multiple
  initial conditions and the source recognizes broader state coverage by noise.
- Exact reusable control:Y in[-2,2],f_theta=theta*(1-Y^2),theta=-1/4,0,+1/4;
  iid Rademacher noise,epsilon1,Y0=1. All whole training paths have the same law
  on{-1,+1};epsilon0 gives Y1=0,Y2=theta. Maps and noisy updates remain bounded;
  noiseless continuations enter contracting intervals. No simulation conducted.
- Standard least-squares decomposition retains phi^T(I-Xplus*X)w_star.
  With quadratic features,X*w_theta=0,while f_theta(0)=theta. Averaging noise
  does not remove this unidentified component;query support/excitation needed.
- New-state reset at zero resolves this fixture with noisy labels. Repeated
  sample means have variance1/N,but this is not a lower bound:the known discrete
  noise/parameter supports even allow individual-observation identification.
- Noise2Noise ICML2018 section2 is the verified conditional-mean regression
  parent. The result is a classical support/rank reduction,not a novel theorem
  or restored method/variance-cost contribution. Decision:not_trigger.
- No new cycle,candidate,F3,forecast,card or experiment. History/response and
  invariant-calibration routes remain failed_closed. Seek a substantive theorem
  or target-matched reference capability beyond ordinary labelled augmentation.

Formal:`papers/proposal/ecomd_paper_g_noise_cancellation_support_audit_2026-09-09.md`.
Contract:`research/paper_g/noise_cancellation_support_audit_20260909.yaml`.

Verified 2026-09-09T11:43:01Z: graph293 /edges274 /locators1295;evidence912;
re-entry118 /qualified0;cycles21 /raw133 /cards0 unchanged. Scoped canonical
validation,source/contract/trigger parity,18 existing tests and git diff --check
passed. Search,protocol and forecast bytes unchanged.
Receipt:`logs/private/paper_g_noise_support_20260909_verification.md`.
