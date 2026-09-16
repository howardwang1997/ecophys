import numpy as np
import pytest

from ecomd.paper_g.model import Law, State, TabularModel
from ecomd.paper_g.theorem_audit import gate_values, geometric_wait


@pytest.mark.parametrize("q", [2, 4])
def test_closed_gate_matches_independent_no_hedge_oracle(q):
    law = Law(.8, 1, 1)
    horizon = 9
    gate = gate_values(q, law, 0, horizon)
    for access in [0, 1]:
        base = TabularModel(q, access)
        values, _ = base.solve(law, horizon)
        indices = [base.index[State(i, access, access)] for i in range(q+1)]
        np.testing.assert_allclose(gate[:, access*(q+1):(access+1)*(q+1)], values[:, indices], rtol=0, atol=1e-12)


def test_certain_reinstatement_occurs_after_first_round():
    q, law = 2, Law(.8, 1, 1)
    gate = gate_values(q, law, 1, 3)
    base = TabularModel(q, 0)
    p, r = base.kernel(law)
    states = [base.index[State(i, 0, 0)] for i in range(q+1)]
    scores = r[states]+np.einsum('sak,k->sa', p[states][:, :, states], gate[2, q+1:])
    scores[~base.legal[states]] = -np.inf
    np.testing.assert_allclose(gate[3, :q+1], scores.max(axis=1), rtol=0, atol=1e-12)
    assert gate[1, 1] == pytest.approx(2)


@pytest.mark.parametrize("probability", [0., 1e-6, .2, 1.])
def test_geometric_identity(probability):
    assert geometric_wait(20, probability) == pytest.approx(sum((1-probability)**t for t in range(20)))
