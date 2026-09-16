"""Conjugate inference using only the declared learner feedback."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from .model import Action, Feedback, Law


class Belief:
    def __init__(self, prior_success: float = 1.0, prior_failure: float = 1.0) -> None:
        if min(prior_success, prior_failure) <= 0:
            raise ValueError("positive Beta prior required")
        self.counts: NDArray[np.float64] = np.tile([prior_success, prior_failure], (3, 1)).astype(np.float64)

    def update(self, action: Action, feedback: Feedback) -> None:
        self.counts[0, 0 if feedback.customer_buy else 1] += 1
        if feedback.willingness is not None:
            favorable = feedback.willingness == (102 if feedback.customer_buy else 98)
        elif feedback.customer_buy and action.ask == 102:
            favorable = feedback.filled
        elif not feedback.customer_buy and action.bid == 98:
            favorable = feedback.filled
        else:
            return
        row = 1 if feedback.customer_buy else 2
        self.counts[row, 0 if favorable else 1] += 1

    def mean(self) -> Law:
        x = self.counts[:, 0] / self.counts.sum(axis=1)
        return Law(float(x[0]), float(x[1]), float(x[2]))

    def sample(self, rng: np.random.Generator) -> Law:
        x = rng.beta(self.counts[:, 0], self.counts[:, 1])
        return Law(float(x[0]), float(x[1]), float(x[2]))
