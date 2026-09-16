"""Private disposable implementation; scientific execution requires the DX runtime gates."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from itertools import pairwise
from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import solve_ivp

Array = NDArray[np.float64]


@dataclass(frozen=True)
class Dynamics:
    modes: int = 16
    viscosity: float = 0.05
    interval: float = 0.05
    rtol: float = 1e-10
    atol: float = 1e-12

    def rhs(self, time: float, state: Array) -> Array:
        del time
        n = self.modes
        # Orthonormal real coordinates: sqrt(2) cos(kx), sqrt(2) sin(kx).
        positive = (state[:n] - 1j * state[n:]) / np.sqrt(2.0)
        spectrum = np.concatenate((np.conj(positive[::-1]), [0j], positive))
        k = np.arange(-n, n + 1)
        product = np.convolve(spectrum, spectrum)[n : 3 * n + 1]
        derivative = -0.5j * k * product - self.viscosity * k * k * spectrum
        dp = derivative[n + 1 :]
        return np.asarray(np.concatenate((dp.real, -dp.imag)) * np.sqrt(2.0), dtype=np.float64)

    def trajectory(self, state: Array, steps: int) -> Array:
        times = self.interval * np.arange(steps + 1, dtype=np.float64)
        result = solve_ivp(
            self.rhs, (0.0, float(times[-1])), state, method="DOP853",
            t_eval=times, rtol=self.rtol, atol=self.atol,
        )
        if not result.success or result.y.shape != (2 * self.modes, steps + 1):
            raise RuntimeError("reference integration did not complete")
        values = np.asarray(result.y.T, dtype=np.float64)
        if not np.isfinite(values).all():
            raise RuntimeError("reference integration returned a non-finite state")
        return values

    def rk4(self, state: Array, steps: int, dt: float) -> Array:
        substeps = round(self.interval / dt)
        if substeps < 1 or not np.isclose(substeps * dt, self.interval, rtol=0, atol=1e-14):
            raise ValueError("RK4 step must divide the observation interval")
        y = state.copy()
        values = [y.copy()]
        for _ in range(steps):
            for _ in range(substeps):
                a = self.rhs(0, y)
                b = self.rhs(0, y + dt * a / 2)
                c = self.rhs(0, y + dt * b / 2)
                d = self.rhs(0, y + dt * c)
                y = y + dt * (a + 2 * b + 2 * c + d) / 6
            values.append(y.copy())
        return np.asarray(values)


def unit_state(unit_id: str, dynamics: Dynamics) -> Array:
    if not unit_id.startswith("g_response_dx_explore_"):
        raise ValueError("only enumerated exploration namespace is supported")
    seed = int.from_bytes(hashlib.sha256(unit_id.encode()).digest(), "big")
    rng = np.random.Generator(np.random.PCG64(seed))
    y = np.zeros(2 * dynamics.modes)
    coefficients = rng.standard_normal((2, 8)) / np.arange(1, 9)
    y[:8], y[dynamics.modes : dynamics.modes + 8] = coefficients
    return y / np.linalg.norm(y)


def pulse(state: Array, mode: int, amplitude: float) -> Array:
    y = state.copy()
    y[mode - 1] += amplitude
    return y


def observation_indices(modes: int, observed: int) -> NDArray[np.int64]:
    return np.concatenate((np.arange(observed), modes + np.arange(observed)))


def pulse_windows(
    trajectory: Array, index: int, mode: int, amplitude: float, dynamics: Dynamics,
) -> tuple[Array, Array]:
    future = dynamics.trajectory(pulse(trajectory[index], mode, amplitude), 5)
    joined = np.concatenate((trajectory[index - 3 : index], future), axis=0)
    histories = np.stack([joined[j : j + 4] for j in range(5)])
    return histories, future[1:]


def build_examples(
    trajectories: Array, augmented: bool, dynamics: Dynamics,
) -> tuple[Array, Array]:
    pool = [(i, j) for i in range(128) for j in range(3, 35)]
    order = np.random.Generator(np.random.PCG64(301)).permutation(len(pool))
    count = 2000 if augmented else 4000
    histories = [trajectories[pool[p][0], pool[p][1] - 3 : pool[p][1] + 1] for p in order[:count]]
    targets = [trajectories[pool[p][0], pool[p][1] + 1] for p in order[:count]]
    if augmented:
        reset_pool = [(i, j) for i in range(128) for j in range(3, 31)]
        for c, (mode, amplitude) in enumerate(((1, .02), (1, .04), (4, .02), (4, .04))):
            selection = np.random.Generator(np.random.PCG64(310 + c)).permutation(len(reset_pool))[:50]
            for p in selection:
                i, j = reset_pool[p]
                for sign in (-1, 1):
                    h, target = pulse_windows(trajectories[i], j, mode, sign * amplitude, dynamics)
                    histories.extend(h)
                    targets.extend(target)
    h_array, t_array = np.asarray(histories), np.asarray(targets)
    if len(t_array) != 4000:
        raise RuntimeError("training-example accounting mismatch")
    return h_array, t_array


class Network:
    def __init__(self, inputs: int, outputs: int, width: int, seed: int) -> None:
        rng = np.random.Generator(np.random.PCG64(seed))
        dims = (inputs, width, width, outputs)
        self.parameters: list[Array] = []
        for a, b in pairwise(dims):
            self.parameters.extend((rng.standard_normal((a, b)) * np.sqrt(2 / (a + b)), np.zeros(b)))

    def predict(self, x: Array) -> Array:
        w1, b1, w2, b2, w3, b3 = self.parameters
        return np.tanh(np.tanh(x @ w1 + b1) @ w2 + b2) @ w3 + b3

    def loss_gradient(self, x: Array, y: Array) -> tuple[float, list[Array]]:
        w1, b1, w2, b2, w3, b3 = self.parameters
        h1 = np.tanh(x @ w1 + b1)
        h2 = np.tanh(h1 @ w2 + b2)
        residual = h2 @ w3 + b3 - y
        d3 = 2 * residual / residual.size
        d2 = (d3 @ w3.T) * (1 - h2 * h2)
        d1 = (d2 @ w2.T) * (1 - h1 * h1)
        return float(np.mean(residual * residual)), [
            x.T @ d1, d1.sum(axis=0), h1.T @ d2, d2.sum(axis=0), h2.T @ d3, d3.sum(axis=0),
        ]

    def fit(self, x: Array, y: Array, seed: int, epochs: int, batch: int, lr: float) -> dict[str, Any]:
        first = [np.zeros_like(p) for p in self.parameters]
        second = [np.zeros_like(p) for p in self.parameters]
        rng = np.random.Generator(np.random.PCG64(seed))
        step = 0
        for _ in range(epochs):
            order = rng.permutation(len(x))
            for start in range(0, len(x), batch):
                chosen = order[start : start + batch]
                _, gradients = self.loss_gradient(x[chosen], y[chosen])
                step += 1
                for p, m, v, g in zip(self.parameters, first, second, gradients, strict=True):
                    m *= .9
                    m += .1 * g
                    v *= .999
                    v += .001 * g * g
                    p -= lr * (m / (1 - .9 ** step)) / (np.sqrt(v / (1 - .999 ** step)) + 1e-8)
        loss = float(np.mean((self.predict(x) - y) ** 2))
        if not np.isfinite(loss):
            raise RuntimeError("non-finite final training loss")
        return {"epochs": epochs, "updates": step, "final_training_mse": loss}


def rollout(network: Network, history: Array, mean: Array, scale: Array, frames: int) -> Array:
    values: list[Array] = []
    h = history.copy()
    for _ in range(5):
        x = ((h[:, -frames:] - mean) / scale).reshape(len(h), -1)
        y = h[:, -1] + scale * network.predict(x)
        values.append(y)
        h = np.concatenate((h[:, 1:], y[:, None]), axis=1)
    return np.stack(values, axis=1)


def forecast_nrmse(prediction: Array, reference: Array) -> float:
    denominator = float(np.sum(reference * reference))
    if denominator <= 0:
        raise ValueError("zero forecast reference norm")
    return float(np.sqrt(np.sum((prediction - reference) ** 2) / denominator))


def reference_check(groups: dict[str, list[str]], dynamics: Dynamics) -> dict[str, Any]:
    largest = 0.0
    cases = 0
    for group in ("train", "diagnostic", "response"):
        for unit in sorted(groups[group])[:8]:
            trajectory = dynamics.trajectory(unit_state(unit, dynamics), 40)
            starts = [(trajectory[0], 40)]
            starts += [(pulse(trajectory[15], k, sign * a), 5)
                       for k in (1, 4) for a in (.02, .04) for sign in (-1, 1)]
            for start, steps in starts:
                truth = dynamics.trajectory(start, steps)
                for dt in (.00125, .000625):
                    other = dynamics.rk4(start, steps, dt)
                    if not np.isfinite(other).all():
                        raise RuntimeError("non-finite RK4 reference state")
                    error = np.linalg.norm(other - truth, axis=1) / np.maximum(np.linalg.norm(truth, axis=1), 1e-12)
                    if not np.isfinite(error).all():
                        raise RuntimeError("non-finite reference comparison")
                    largest = max(largest, float(error.max()))
                    cases += 1
                    if largest >= 1e-5:
                        raise RuntimeError("reference accuracy screen failed")
    return {"cases": cases, "max_relative_state_disagreement": largest,
            "zero_mode": "excluded_exactly_by_state_representation", "passed": True}
