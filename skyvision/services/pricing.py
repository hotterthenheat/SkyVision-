from dataclasses import dataclass
from math import erf, exp, log, sqrt

from skyvision.models import OptionContract


def _norm_cdf(x: float) -> float:
    return (1.0 + erf(x / sqrt(2.0))) / 2.0


def black_scholes(
    spot: float, strike: float, years: float, rate: float, sigma: float, option_type: str
) -> float:
    years = max(years, 1 / 365 / 24)
    sigma = max(sigma, 0.01)
    d1 = (log(spot / strike) + (rate + sigma**2 / 2) * years) / (sigma * sqrt(years))
    d2 = d1 - sigma * sqrt(years)
    if option_type.lower() == "call":
        return spot * _norm_cdf(d1) - strike * exp(-rate * years) * _norm_cdf(d2)
    return strike * exp(-rate * years) * _norm_cdf(-d2) - spot * _norm_cdf(-d1)


@dataclass(frozen=True, slots=True)
class Projection:
    move_pct: float
    underlying_price: float
    option_value: float


def projected_values(
    contract: OptionContract, spot: float, years_to_expiration: float, rate: float
) -> list[Projection]:
    iv = contract.implied_volatility or 0.45
    sign = 1 if contract.option_type.lower() == "call" else -1
    moves = [0.0025, 0.005, 0.0075, 0.01, 0.015, 0.02]
    return [
        Projection(
            m,
            round(spot * (1 + sign * m), 4),
            round(
                black_scholes(
                    spot * (1 + sign * m),
                    contract.strike,
                    years_to_expiration,
                    rate,
                    iv,
                    contract.option_type,
                ),
                4,
            ),
        )
        for m in moves
    ]
