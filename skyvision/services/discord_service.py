from datetime import UTC, datetime
from typing import Any

import discord

from skyvision.models import Direction, OptionContract, Signal


class DiscordAlertFormatter:
    @staticmethod
    def alert_embed(
        signal: Signal, contract: OptionContract | None, projections: list | None = None
    ) -> discord.Embed:
        color = (
            discord.Color.green() if signal.direction == Direction.BULLISH else discord.Color.red()
        )
        embed = discord.Embed(
            title=f"SkyVision {signal.direction.upper()} {signal.symbol}",
            color=color,
            timestamp=datetime.now(UTC),
        )
        embed.add_field(
            name="Setup",
            value=f"Score: {signal.score} ({signal.grade})\nRSI 1m/5m: {signal.rsi_1m}/{signal.rsi_5m}\nVWAP: {signal.vwap_status}\nRVOL: {signal.rvol}\nVolume: {signal.volume_status}",
            inline=False,
        )
        s = signal.structure
        embed.add_field(
            name="Market Structure",
            value=f"Trend: {s.trend}\nBOS: {s.bos}\nMSS: {s.mss}\nHH/HL/LH/LL: {s.higher_high}/{s.higher_low}/{s.lower_high}/{s.lower_low}",
            inline=False,
        )
        if contract:
            embed.add_field(
                name="Selected Contract",
                value=f"{contract.symbol}\nBid/Ask/Mid: {contract.bid}/{contract.ask}/{contract.mid}\nOI/Vol: {contract.open_interest}/{contract.volume}\nDelta/Gamma/Theta/Vega/IV: {contract.delta}/{contract.gamma}/{contract.theta}/{contract.vega}/{contract.implied_volatility}",
                inline=False,
            )
        embed.add_field(
            name="Trade Plan",
            value=f"Entry: {signal.entry}\nTargets: {', '.join(map(str, signal.targets))}\nInvalidation: {signal.invalidation}",
            inline=False,
        )
        if projections:
            embed.add_field(
                name="Black-Scholes Projections",
                value="\n".join(
                    f"+{p.move_pct:.2%}: underlying {p.underlying_price}, option {p.option_value}"
                    for p in projections
                ),
                inline=False,
            )
        return embed

    @staticmethod
    def embed_from_payload(payload: dict[str, Any]) -> discord.Embed:
        sig = payload["signal"]
        color = discord.Color.green() if sig["direction"] == "bullish" else discord.Color.red()
        embed = discord.Embed(
            title=f"SkyVision {sig['direction'].upper()} {sig['symbol']}",
            color=color,
            timestamp=datetime.now(UTC),
        )
        embed.add_field(
            name="Setup",
            value=f"Score: {sig['score']} ({sig['grade']})\nRSI 1m/5m: {sig['rsi_1m']}/{sig['rsi_5m']}\nVWAP: {sig['vwap_status']}\nRVOL: {sig['rvol']}\nVolume: {sig['volume_status']}",
            inline=False,
        )
        st = sig["structure"]
        embed.add_field(
            name="Market Structure",
            value=f"Trend: {st['trend']}\nBOS: {st['bos']}\nMSS: {st['mss']}\nHH/HL/LH/LL: {st['higher_high']}/{st['higher_low']}/{st['lower_high']}/{st['lower_low']}",
            inline=False,
        )
        contract = payload.get("contract")
        if contract:
            mid = round((contract["bid"] + contract["ask"]) / 2, 4)
            embed.add_field(
                name="Selected Contract",
                value=f"{contract['symbol']}\nBid/Ask/Mid: {contract['bid']}/{contract['ask']}/{mid}\nOI/Vol: {contract['open_interest']}/{contract['volume']}\nDelta/Gamma/Theta/Vega/IV: {contract['delta']}/{contract.get('gamma')}/{contract.get('theta')}/{contract.get('vega')}/{contract.get('implied_volatility')}",
                inline=False,
            )
        embed.add_field(
            name="Trade Plan",
            value=f"Entry: {sig['entry']}\nTargets: {', '.join(map(str, sig['targets']))}\nInvalidation: {sig['invalidation']}",
            inline=False,
        )
        projections = payload.get("projections") or []
        if projections:
            embed.add_field(
                name="Black-Scholes Projections",
                value="\n".join(
                    f"+{p['move_pct']:.2%}: underlying {p['underlying_price']}, option {p['option_value']}"
                    for p in projections
                ),
                inline=False,
            )
        return embed
