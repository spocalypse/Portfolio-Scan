"""M2 — Portfolio beta (SPEC §5.5). Pure functions, no I/O, no network.

r_p,t = Σ w_i · r_i,t; β = cov(r_p, r_m) / var(r_m); R² is reported alongside because
a beta with low R² is misleading (the narrative layer must say so, per SPEC — not this
module's job to decide, only to report the number honestly).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class BetaResult:
    beta: float
    r_squared: float


def compute_portfolio_returns(
    weights: Mapping[str, float], returns_by_ticker: Mapping[str, Sequence[float]]
) -> tuple[float, ...]:
    tickers = list(weights.keys())
    w = np.array([weights[t] for t in tickers])
    r = np.array([returns_by_ticker[t] for t in tickers])
    return tuple((w @ r).tolist())


def compute_beta(
    portfolio_returns: Sequence[float], market_returns: Sequence[float]
) -> BetaResult:
    rp = np.asarray(portfolio_returns, dtype=float)
    rm = np.asarray(market_returns, dtype=float)

    covariance = np.cov(rp, rm, ddof=1)[0, 1]
    market_variance = np.var(rm, ddof=1)
    beta = covariance / market_variance

    correlation = np.corrcoef(rp, rm)[0, 1]
    r_squared = correlation**2

    return BetaResult(float(beta), float(r_squared))
