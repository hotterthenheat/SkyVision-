from datetime import UTC, datetime, timedelta

from skyvision.models import Direction, OptionContract, Signal, StructureState
from skyvision.services.serialization import json_safe


def test_json_safe_serializes_signal_contract_and_datetimes() -> None:
    structure = StructureState([], [], "uptrend", True, False, True, True, False, False)
    signal = Signal(
        symbol="SPY",
        direction=Direction.BULLISH,
        score=91,
        grade="A+",
        rsi_1m=60,
        rsi_5m=55,
        vwap_status="above VWAP",
        rvol=2.0,
        volume_status="expanding",
        structure=structure,
        entry=500,
        targets=[501, 502],
        invalidation="VWAP lost",
    )
    contract = OptionContract(
        "SPY260101C00500000",
        "SPY",
        datetime.now(UTC) + timedelta(days=7),
        500,
        "call",
        1.0,
        1.1,
        None,
        1000,
        2000,
        0.45,
    )
    payload = json_safe({"signal": signal, "contract": contract})
    assert payload["signal"]["direction"] == "bullish"
    assert isinstance(payload["signal"]["created_at"], str)
    assert isinstance(payload["contract"]["expiration"], str)
