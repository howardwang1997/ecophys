"""M1.4 — Risk module: VaR/ES estimation + backtesting.

Public API:
    var_es_from_paths, kupiec_pof_test, christoffersen_ind_test,
    christoffersen_cc_test, rolling_backtest, print_report
    HistoricalSampler, GARCHSampler, EcoMDSampler
"""

from ecomd.risk.var_backtest import (
    BacktestResult,
    christoffersen_cc_test,
    christoffersen_ind_test,
    kupiec_pof_test,
    print_report,
    rolling_backtest,
    var_es_from_paths,
)
from ecomd.risk.samplers import (
    EcoMDSampler,
    GARCHSampler,
    HistoricalSampler,
)

__all__ = [
    "BacktestResult",
    "EcoMDSampler",
    "GARCHSampler",
    "HistoricalSampler",
    "christoffersen_cc_test",
    "christoffersen_ind_test",
    "kupiec_pof_test",
    "print_report",
    "rolling_backtest",
    "var_es_from_paths",
]
