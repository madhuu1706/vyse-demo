"""SPIKE — deterministic outlier scoring. Pure functions, fully unit-testable.

score = eng_ratio * velocity * retention

- eng_ratio : total engagement vs the account's rolling average
- velocity  : how fast engagement accrued (needs >= 2 metric snapshots)
- retention : depth signal (saves + shares relative to views)
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Snapshot:
    captured_at: datetime
    likes: int = 0
    comments: int = 0
    shares: int = 0
    views: int = 0
    saves: int = 0


def outlier_score(
    metrics: dict, account_avg_eng: float | None, snapshots: list[Snapshot]
) -> dict:
    eng = sum(int(metrics.get(k, 0) or 0) for k in ("likes", "comments", "shares", "saves"))
    avg = float(account_avg_eng) if account_avg_eng else 0.0
    eng_ratio = (eng / avg) if avg > 0 else 1.0

    # velocity: engagement gained per hour, normalised by account average
    velocity = 1.0
    if len(snapshots) >= 2:
        a, b = snapshots[0], snapshots[-1]
        hours = max((b.captured_at - a.captured_at).total_seconds() / 3600, 1.0)
        delta = (b.likes + b.comments) - (a.likes + a.comments)
        velocity = 1.0 + min(delta / hours / max(avg, 1.0), 5.0)

    # retention proxy: deep engagement relative to reach
    views = int(metrics.get("views", 0) or 0)
    retention = 1.0
    if views > 0:
        deep = int(metrics.get("saves", 0) or 0) + int(metrics.get("shares", 0) or 0)
        retention = 1.0 + min(deep / views * 20, 4.0)

    score = eng_ratio * velocity * retention

    if score >= 3 and velocity >= 2:
        otype = "viral"
    elif score >= 2 and velocity < 1.3:
        otype = "evergreen"
    elif eng_ratio < 1.2 and velocity >= 2:
        otype = "sleeper"
    else:
        otype = "none"

    return {
        "score": round(score, 3),
        "outlier_type": otype,
        "components": {
            "eng_ratio": round(eng_ratio, 3),
            "velocity": round(velocity, 3),
            "retention": round(retention, 3),
        },
    }
