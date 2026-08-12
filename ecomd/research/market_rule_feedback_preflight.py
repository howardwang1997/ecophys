"""Generated-data utilities for the annual market-rule feedback RD preflight."""

from __future__ import annotations

import hashlib
import io
import math
import warnings
from collections.abc import Mapping, Sequence
from contextlib import redirect_stdout
from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy.stats import binomtest, norm

FloatArray = NDArray[np.float64]
IntArray = NDArray[np.int64]

_RTS11_PRICE_BOUNDS = np.asarray(
    [0.0, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0, 200.0, 500.0,
     1000.0, 2000.0, 5000.0, 10000.0, 20000.0, 50000.0],
    dtype=np.float64,
)
_RTS11_TICKS = np.asarray(
    [
        [0.0005, 0.0002, 0.0001, 0.0001, 0.0001, 0.0001],
        [0.001, 0.0005, 0.0002, 0.0001, 0.0001, 0.0001],
        [0.002, 0.001, 0.0005, 0.0002, 0.0001, 0.0001],
        [0.005, 0.002, 0.001, 0.0005, 0.0002, 0.0001],
        [0.01, 0.005, 0.002, 0.001, 0.0005, 0.0002],
        [0.02, 0.01, 0.005, 0.002, 0.001, 0.0005],
        [0.05, 0.02, 0.01, 0.005, 0.002, 0.001],
        [0.1, 0.05, 0.02, 0.01, 0.005, 0.002],
        [0.2, 0.1, 0.05, 0.02, 0.01, 0.005],
        [0.5, 0.2, 0.1, 0.05, 0.02, 0.01],
        [1.0, 0.5, 0.2, 0.1, 0.05, 0.02],
        [2.0, 1.0, 0.5, 0.2, 0.1, 0.05],
        [5.0, 2.0, 1.0, 0.5, 0.2, 0.1],
        [10.0, 5.0, 2.0, 1.0, 0.5, 0.2],
        [20.0, 10.0, 5.0, 2.0, 1.0, 0.5],
        [50.0, 20.0, 10.0, 5.0, 2.0, 1.0],
        [100.0, 50.0, 20.0, 10.0, 5.0, 2.0],
        [200.0, 100.0, 50.0, 20.0, 10.0, 5.0],
        [500.0, 200.0, 100.0, 50.0, 20.0, 10.0],
    ],
    dtype=np.float64,
)
_CUTOFF_TO_COLUMNS = {10.0: (0, 1), 80.0: (1, 2), 600.0: (2, 3), 2000.0: (3, 4), 9000.0: (4, 5)}


class FrozenSpecificationError(RuntimeError):
    """Signal that the installed estimator cannot execute the frozen contract."""


@dataclass(frozen=True)
class GeneratedPanel:
    """One generated RD panel and its design metadata."""

    x: FloatArray
    y: FloatArray
    year: IntArray
    cluster: IntArray | None
    true_tau: float
    known_year_effect: FloatArray


@dataclass(frozen=True)
class RDEstimate:
    """Audit-safe extraction from the official rdrobust output."""

    estimate: float
    p_value: float
    ci_low: float
    ci_high: float
    conventional_estimate: float
    conventional_p_value: float
    conventional_ci_low: float
    conventional_ci_high: float
    bandwidth_left: float
    bandwidth_right: float
    n_left: int
    n_right: int
    n_effective_left: int
    n_effective_right: int
    mass_points_left: int
    mass_points_right: int
    vce: str

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-safe representation."""

        return {
            "estimate": self.estimate,
            "p_value": self.p_value,
            "ci_low": self.ci_low,
            "ci_high": self.ci_high,
            "conventional_estimate": self.conventional_estimate,
            "conventional_p_value": self.conventional_p_value,
            "conventional_ci_low": self.conventional_ci_low,
            "conventional_ci_high": self.conventional_ci_high,
            "bandwidth_left": self.bandwidth_left,
            "bandwidth_right": self.bandwidth_right,
            "n_left": self.n_left,
            "n_right": self.n_right,
            "n_effective_left": self.n_effective_left,
            "n_effective_right": self.n_effective_right,
            "mass_points_left": self.mass_points_left,
            "mass_points_right": self.mass_points_right,
            "vce": self.vce,
        }


@dataclass(frozen=True)
class OracleInterval:
    """Fixed-design local-linear interval with a known curvature bias bound."""

    estimate: float
    ci_low: float
    ci_high: float
    standard_error: float
    bias_bound: float
    mass_points_left: int
    mass_points_right: int

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-safe representation."""

        return {
            "estimate": self.estimate,
            "ci_low": self.ci_low,
            "ci_high": self.ci_high,
            "standard_error": self.standard_error,
            "bias_bound": self.bias_bound,
            "mass_points_left": self.mass_points_left,
            "mass_points_right": self.mass_points_right,
        }


def _finite_float(value: object, *, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be numeric")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _integer(value: object, *, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")
    return value


def _mapping(payload: Mapping[str, object], key: str) -> Mapping[str, object]:
    value = payload.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"{key} must be a mapping")
    return value


def _number_sequence(payload: Mapping[str, object], key: str) -> tuple[float, ...]:
    value = payload.get(key)
    if not isinstance(value, list):
        raise ValueError(f"{key} must be a list")
    return tuple(_finite_float(item, name=key) for item in value)


def canonical_stream_label(
    *,
    seed: int,
    scenario: str,
    cutoff: float,
    sigma: float,
    replicate: int,
    float_format: str,
) -> str:
    """Return the frozen text label used to derive an order-independent stream."""

    if not scenario or "|" in scenario:
        raise ValueError("scenario must be non-empty and cannot contain '|'")
    if replicate < 0:
        raise ValueError("replicate must be nonnegative")
    return "|".join(
        [str(seed), scenario, format(float(cutoff), float_format), format(float(sigma), float_format), str(replicate)]
    )


def rng_for_stream(
    *,
    seed: int,
    scenario: str,
    cutoff: float,
    sigma: float,
    replicate: int,
    float_format: str,
) -> np.random.Generator:
    """Build the exact preregistered NumPy random stream."""

    label = canonical_stream_label(
        seed=seed,
        scenario=scenario,
        cutoff=cutoff,
        sigma=sigma,
        replicate=replicate,
        float_format=float_format,
    )
    digest = hashlib.sha256(label.encode("utf-8")).digest()
    entropy = [int.from_bytes(digest[offset : offset + 4], "big") for offset in range(0, 16, 4)]
    return np.random.default_rng(np.random.SeedSequence(entropy))


def year_covariates(year: IntArray) -> FloatArray:
    """Construct five no-intercept indicators for six frozen input years."""

    values = np.asarray(year, dtype=np.int64)
    levels = np.unique(values)
    if levels.size != 6:
        raise ValueError("year must contain exactly six levels")
    covariates: FloatArray = (values[:, None] == levels[None, 1:]).astype(np.float64)
    return covariates


def _round_running_variable(x_raw: FloatArray, cutoff: float, increment: float) -> FloatArray:
    levels = cutoff * np.exp(x_raw)
    rounded = np.round(levels / increment) * increment
    if np.any(rounded <= 0.0):
        raise ValueError("rounding produced nonpositive ADNT")
    return np.log(rounded / cutoff).astype(np.float64)


def generate_panel(
    config: Mapping[str, object],
    scenario: Mapping[str, object],
    *,
    cutoff: float,
    sigma: float,
    replicate: int,
) -> GeneratedPanel:
    """Generate one frozen null or effect panel without reading external data."""

    scenario_name = scenario.get("name")
    mode = scenario.get("mode")
    if not isinstance(scenario_name, str) or not isinstance(mode, str):
        raise ValueError("scenario name and mode must be strings")
    if not math.isfinite(cutoff) or cutoff <= 0.0:
        raise ValueError("cutoff must be finite and positive")
    if not math.isfinite(sigma) or sigma <= 0.0:
        raise ValueError("sigma must be finite and positive")
    if replicate < 0:
        raise ValueError("replicate must be nonnegative")
    seed = _integer(config.get("seed"), name="seed")
    float_format = config.get("seed_float_format")
    if not isinstance(float_format, str):
        raise ValueError("seed_float_format must be a string")
    rng = rng_for_stream(
        seed=seed,
        scenario=scenario_name,
        cutoff=cutoff,
        sigma=sigma,
        replicate=replicate,
        float_format=float_format,
    )
    years_raw = config.get("years")
    if not isinstance(years_raw, list) or any(isinstance(year, bool) or not isinstance(year, int) for year in years_raw):
        raise ValueError("years must contain integers")
    years = np.asarray(years_raw, dtype=np.int64)
    n_per_year = _integer(config.get("n_candidates_per_year"), name="n_candidates_per_year")
    year = np.repeat(years, n_per_year)
    year_index = np.repeat(np.arange(years.size, dtype=np.int64), n_per_year)
    year_effects = np.asarray(_number_sequence(config, "year_effects"), dtype=np.float64)
    if year_effects.size != years.size:
        raise ValueError("year_effects must match years")
    known_year_effect = year_effects[year_index]
    support = _number_sequence(config, "ratio_support")
    if len(support) != 2 or not 0.0 < support[0] < 1.0 < support[1]:
        raise ValueError("ratio_support must straddle one")

    cluster: IntArray | None = None
    if mode == "clustered":
        cluster_count = _integer(config.get("cluster_count"), name="cluster_count")
        repeats = _integer(config.get("cluster_repeats"), name="cluster_repeats")
        if cluster_count != n_per_year or repeats != years.size:
            raise ValueError("cluster_count and cluster_repeats must match the balanced panel")
        cluster = np.tile(np.arange(cluster_count, dtype=np.int64), repeats)
        intercept_sigma = _finite_float(
            config.get("cluster_random_intercept_sigma"), name="cluster_random_intercept_sigma"
        )
        random_intercepts = rng.normal(0.0, intercept_sigma, cluster_count)
        cluster_component = random_intercepts[cluster]
    else:
        cluster_component = np.zeros(year.size, dtype=np.float64)

    if mode == "regression_to_mean":
        rtm = _mapping(config, "regression_to_mean")
        latent_support = _number_sequence(rtm, "latent_log_support")
        if len(latent_support) != 2 or latent_support[0] >= latent_support[1]:
            raise ValueError("latent_log_support must have two ordered bounds")
        baseline_sigma = _finite_float(rtm.get("baseline_measurement_sigma"), name="baseline_measurement_sigma")
        lower, upper = math.log(support[0]), math.log(support[1])
        accepted_latent: list[FloatArray] = []
        accepted_x: list[FloatArray] = []
        accepted = 0
        while accepted < year.size:
            batch = max(64, year.size - accepted)
            latent_batch = rng.uniform(latent_support[0], latent_support[1], batch)
            x_batch = latent_batch + rng.normal(0.0, baseline_sigma, batch)
            keep = (x_batch >= lower) & (x_batch <= upper)
            accepted_latent.append(latent_batch[keep])
            accepted_x.append(x_batch[keep])
            accepted += int(np.count_nonzero(keep))
        latent = np.concatenate(accepted_latent)[: year.size]
        x_raw = np.concatenate(accepted_x)[: year.size]
        if scenario.get("rounded") is True:
            x = _round_running_variable(
                x_raw,
                cutoff,
                _finite_float(config.get("rounding_increment"), name="rounding_increment"),
            )
        else:
            x = x_raw
        persistence = _finite_float(rtm.get("persistence"), name="persistence")
        followup_sigma = _finite_float(rtm.get("followup_noise_sigma"), name="followup_noise_sigma")
        y = known_year_effect + persistence * latent + rng.normal(0.0, followup_sigma, year.size)
        true_tau = 0.0
    else:
        ratio = rng.uniform(support[0], support[1], year.size)
        x_raw = np.log(ratio)
        if scenario.get("rounded") is True:
            x = _round_running_variable(
                x_raw,
                cutoff,
                _finite_float(config.get("rounding_increment"), name="rounding_increment"),
            )
        else:
            x = x_raw.astype(np.float64)
        slope = _finite_float(config.get("base_slope"), name="base_slope")
        quadratic = _finite_float(
            scenario.get("quadratic", config.get("base_quadratic")), name="quadratic"
        )
        true_tau = _finite_float(scenario.get("tau", 0.0), name="tau")
        if mode == "mixed_exposure":
            fractions = np.asarray(_number_sequence(config, "mixed_exposure_fractions"), dtype=np.float64)
            if fractions.size != years.size:
                raise ValueError("mixed_exposure_fractions must match years")
            tau_by_year = (true_tau / float(np.mean(fractions))) * fractions
            treatment_effect = tau_by_year[year_index] * (x >= 0.0)
        else:
            treatment_effect = np.asarray(true_tau * (x >= 0.0), dtype=np.float64)
        y = (
            slope * x
            + quadratic * x**2
            + known_year_effect
            + treatment_effect
            + cluster_component
            + rng.normal(0.0, sigma, year.size)
        )

    if mode == "mcar_attrition":
        probability = _finite_float(config.get("mcar_attrition_probability"), name="mcar_attrition_probability")
        keep = rng.random(year.size) >= probability
        x, y, year, known_year_effect = x[keep], y[keep], year[keep], known_year_effect[keep]

    return GeneratedPanel(
        x=np.asarray(x, dtype=np.float64),
        y=np.asarray(y, dtype=np.float64),
        year=np.asarray(year, dtype=np.int64),
        cluster=cluster,
        true_tau=true_tau,
        known_year_effect=np.asarray(known_year_effect, dtype=np.float64),
    )


def fit_rdrobust(panel: GeneratedPanel, estimator: Mapping[str, object], minimum_mass_points: int) -> RDEstimate:
    """Fit and strictly verify the preregistered official rdrobust specification."""

    from rdrobust import rdrobust

    unique_left = np.unique(panel.x[panel.x < 0.0]).size
    unique_right = np.unique(panel.x[panel.x >= 0.0]).size
    if min(unique_left, unique_right) < minimum_mass_points:
        raise ValueError("insufficient distinct running-variable mass points")
    vce_key = "clustered_vce" if panel.cluster is not None else "independent_vce"
    vce = estimator.get(vce_key)
    if not isinstance(vce, str):
        raise ValueError(f"{vce_key} must be a string")
    kernel = estimator.get("kernel")
    bandwidth_selection = estimator.get("bandwidth_selection")
    mass_points = estimator.get("mass_points")
    if not all(isinstance(value, str) for value in [kernel, bandwidth_selection, mass_points]):
        raise ValueError("estimator string options are malformed")
    confidence = _finite_float(estimator.get("confidence_level"), name="confidence_level")
    captured_stdout = io.StringIO()
    with warnings.catch_warnings(record=True) as caught_warnings, redirect_stdout(captured_stdout):
        warnings.simplefilter("always")
        result: Any = rdrobust(
            y=panel.y,
            x=panel.x,
            c=_finite_float(estimator.get("cutoff"), name="cutoff"),
            p=_integer(estimator.get("polynomial_order"), name="polynomial_order"),
            q=_integer(estimator.get("bias_order"), name="bias_order"),
            covs=year_covariates(panel.year),
            kernel=kernel,
            bwselect=bandwidth_selection,
            vce=vce,
            cluster=panel.cluster,
            level=100.0 * confidence,
            masspoints=mass_points,
            bwcheck=minimum_mass_points,
        )
    output_lines = [line.strip() for line in captured_stdout.getvalue().splitlines() if line.strip()]
    if any(line != "Mass points detected in the running variable." for line in output_lines):
        raise FrozenSpecificationError(f"unexpected rdrobust output: {output_lines}")
    if caught_warnings:
        messages = [str(item.message) for item in caught_warnings]
        raise FrozenSpecificationError(f"rdrobust emitted warnings: {messages}")
    expected_kernel = "Triangular"
    expected_vce = vce.upper()
    if (
        result.kernel != expected_kernel
        or result.vce != expected_vce
        or result.bwselect != bandwidth_selection
        or result.masspoints != mass_points
        or not math.isclose(float(result.level), 100.0 * confidence)
    ):
        raise FrozenSpecificationError("rdrobust silently changed a frozen estimator option")
    values = [
        float(result.coef.loc["Bias-Corrected", "Coeff"]),
        float(result.pv.loc["Robust", "P>|z|"]),
        float(result.ci.loc["Robust", "CI Lower"]),
        float(result.ci.loc["Robust", "CI Upper"]),
        float(result.coef.loc["Conventional", "Coeff"]),
        float(result.pv.loc["Conventional", "P>|z|"]),
        float(result.ci.loc["Conventional", "CI Lower"]),
        float(result.ci.loc["Conventional", "CI Upper"]),
        float(result.bws.loc["h", "left"]),
        float(result.bws.loc["h", "right"]),
    ]
    if not np.isfinite(values).all():
        raise FrozenSpecificationError("rdrobust returned non-finite gated output")
    return RDEstimate(
        estimate=values[0],
        p_value=values[1],
        ci_low=values[2],
        ci_high=values[3],
        conventional_estimate=values[4],
        conventional_p_value=values[5],
        conventional_ci_low=values[6],
        conventional_ci_high=values[7],
        bandwidth_left=values[8],
        bandwidth_right=values[9],
        n_left=int(result.N[0]),
        n_right=int(result.N[1]),
        n_effective_left=int(result.N_h[0]),
        n_effective_right=int(result.N_h[1]),
        mass_points_left=int(result.M[0]),
        mass_points_right=int(result.M[1]),
        vce=result.vce,
    )


def _local_linear_weights(x: FloatArray, *, bandwidth: float, side: str) -> tuple[FloatArray, IntArray]:
    if side == "left":
        selected = np.flatnonzero((x < 0.0) & (x >= -bandwidth))
    elif side == "right":
        selected = np.flatnonzero((x >= 0.0) & (x <= bandwidth))
    else:
        raise ValueError("side must be left or right")
    local_x = x[selected]
    weights = 1.0 - np.abs(local_x) / bandwidth
    design = np.column_stack([np.ones(local_x.size, dtype=np.float64), local_x])
    gram = design.T @ (weights[:, None] * design)
    if selected.size < 2 or np.linalg.matrix_rank(gram) != 2:
        raise ValueError(f"singular {side} local-linear design")
    intercept_weights = np.asarray([1.0, 0.0]) @ np.linalg.solve(gram, design.T * weights)
    return np.asarray(intercept_weights, dtype=np.float64), selected.astype(np.int64)


def bias_bound_oracle(
    panel: GeneratedPanel,
    *,
    bandwidth: float,
    curvature_bound: float,
    sigma: float,
    confidence_level: float,
    minimum_mass_points: int,
) -> OracleInterval:
    """Construct the preregistered independent-Gaussian fixed-design interval."""

    if panel.cluster is not None:
        raise ValueError("oracle is restricted to independent cases")
    if bandwidth <= 0.0 or curvature_bound < 0.0 or sigma <= 0.0:
        raise ValueError("oracle bandwidth/smoothness/noise parameters are invalid")
    adjusted_y = panel.y - panel.known_year_effect
    left_weights, left_index = _local_linear_weights(panel.x, bandwidth=bandwidth, side="left")
    right_weights, right_index = _local_linear_weights(panel.x, bandwidth=bandwidth, side="right")
    mass_left = np.unique(panel.x[left_index]).size
    mass_right = np.unique(panel.x[right_index]).size
    if min(mass_left, mass_right) < minimum_mass_points:
        raise ValueError("insufficient distinct mass points for oracle")
    combined_weights = np.zeros(panel.x.size, dtype=np.float64)
    combined_weights[right_index] = right_weights
    combined_weights[left_index] = -left_weights
    estimate = float(combined_weights @ adjusted_y)
    standard_error = sigma * float(np.sqrt(np.sum(combined_weights**2)))
    bias_bound = 0.5 * curvature_bound * float(np.sum(np.abs(combined_weights) * panel.x**2))
    quantile = float(norm.ppf(0.5 + confidence_level / 2.0))
    radius = quantile * standard_error + bias_bound
    return OracleInterval(
        estimate=estimate,
        ci_low=estimate - radius,
        ci_high=estimate + radius,
        standard_error=standard_error,
        bias_bound=bias_bound,
        mass_points_left=mass_left,
        mass_points_right=mass_right,
    )


def wilson_interval(successes: int, total: int, confidence_level: float) -> tuple[float, float]:
    """Return a two-sided Wilson binomial interval."""

    if successes < 0 or total <= 0 or successes > total:
        raise ValueError("Wilson interval requires 0 <= successes <= total and total > 0")
    z_value = float(norm.ppf(0.5 + confidence_level / 2.0))
    probability = successes / total
    denominator = 1.0 + z_value**2 / total
    centre = (probability + z_value**2 / (2.0 * total)) / denominator
    radius = z_value / denominator * math.sqrt(
        probability * (1.0 - probability) / total + z_value**2 / (4.0 * total**2)
    )
    return centre - radius, centre + radius


def sorting_detected(
    rng: np.random.Generator,
    *,
    sample_size: int,
    bandwidth: float,
    right_probability: float,
    alpha: float,
) -> tuple[bool, float, FloatArray]:
    """Run the frozen exact-binomial side-balance diagnostic."""

    sign_right = rng.random(sample_size) < right_probability
    magnitude = rng.uniform(0.0, bandwidth, sample_size)
    x = np.where(sign_right, magnitude, -magnitude).astype(np.float64)
    p_value = float(binomtest(int(np.count_nonzero(sign_right)), sample_size, p=0.5).pvalue)
    return p_value < alpha, p_value, x


def differential_attrition_detected(
    rng: np.random.Generator,
    *,
    sample_size: int,
    base_probability: float,
    right_side_increment: float,
    positive_shock_increment: float,
    alpha: float,
) -> tuple[bool, float]:
    """Run the frozen two-sided difference-in-proportions attrition diagnostic."""

    right = rng.random(sample_size) < 0.5
    shock = rng.normal(0.0, 1.0, sample_size)
    loss_probability = np.clip(
        base_probability + right_side_increment * right + positive_shock_increment * (shock > 0.0),
        0.0,
        1.0,
    )
    lost = rng.random(sample_size) < loss_probability
    n_right = int(np.count_nonzero(right))
    n_left = sample_size - n_right
    lost_right = int(np.count_nonzero(lost & right))
    lost_left = int(np.count_nonzero(lost & ~right))
    pooled = (lost_right + lost_left) / sample_size
    standard_error = math.sqrt(pooled * (1.0 - pooled) * (1.0 / n_right + 1.0 / n_left))
    if standard_error == 0.0:
        p_value = 1.0 if lost_right / n_right == lost_left / n_left else 0.0
    else:
        statistic = (lost_right / n_right - lost_left / n_left) / standard_error
        p_value = float(2.0 * norm.cdf(-abs(statistic)))
    return p_value < alpha, p_value


def distinct_mass_points_by_side(x: Sequence[float], *, bandwidth: float) -> tuple[int, int]:
    """Count distinct running-variable values within a symmetric bandwidth."""

    values = np.asarray(x, dtype=np.float64)
    left = np.unique(values[(values < 0.0) & (values >= -bandwidth)]).size
    right = np.unique(values[(values >= 0.0) & (values <= bandwidth)]).size
    return int(left), int(right)


def shared_rule_reason(cutoff: float, shared_cutoffs: Sequence[float]) -> str | None:
    """Return the deterministic coincident-rule refusal reason, when present."""

    return "COINCIDENT_RTS28_REPORTING_BOUNDARY" if float(cutoff) in {float(value) for value in shared_cutoffs} else None


def statutory_tick(price: float, liquidity_band: int) -> float:
    """Return the RTS 11 minimum tick for a positive price and band 1 through 6."""

    if not math.isfinite(price) or price < 0.0:
        raise ValueError("price must be finite and nonnegative")
    if isinstance(liquidity_band, bool) or not isinstance(liquidity_band, int) or liquidity_band not in range(1, 7):
        raise ValueError("liquidity_band must be an integer from 1 to 6")
    row = int(np.searchsorted(_RTS11_PRICE_BOUNDS, price, side="right") - 1)
    return float(_RTS11_TICKS[row, liquidity_band - 1])


def tick_first_stage(cutoff: float, price: float) -> tuple[bool, float, float]:
    """Evaluate whether adjacent statutory bands differ at a cutoff-price pair."""

    columns = _CUTOFF_TO_COLUMNS.get(float(cutoff))
    if columns is None:
        raise ValueError("cutoff is not a statutory RTS 11 ADNT boundary")
    left_tick = statutory_tick(price, columns[0] + 1)
    right_tick = statutory_tick(price, columns[1] + 1)
    return not math.isclose(left_tick, right_tick, rel_tol=0.0, abs_tol=0.0), left_tick, right_tick
