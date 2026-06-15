from datetime import datetime, timedelta, timezone

from vyse_api.scoring import Snapshot, outlier_score

T0 = datetime(2025, 1, 1, tzinfo=timezone.utc)


def test_baseline_no_data_is_neutral():
    r = outlier_score({"likes": 10}, account_avg_eng=None, snapshots=[])
    assert r["outlier_type"] == "none"
    assert r["components"]["eng_ratio"] == 1.0


def test_viral_high_ratio_and_velocity():
    snaps = [
        Snapshot(captured_at=T0, likes=100, comments=10),
        Snapshot(captured_at=T0 + timedelta(hours=2), likes=5000, comments=900),
    ]
    r = outlier_score(
        {"likes": 5000, "comments": 900, "shares": 400, "saves": 600, "views": 20000},
        account_avg_eng=800,
        snapshots=snaps,
    )
    assert r["score"] > 3
    assert r["outlier_type"] == "viral"


def test_evergreen_steady_high_engagement():
    snaps = [
        Snapshot(captured_at=T0, likes=2000, comments=100),
        Snapshot(captured_at=T0 + timedelta(hours=48), likes=2100, comments=110),
    ]
    r = outlier_score(
        {"likes": 2100, "comments": 110, "views": 50000},
        account_avg_eng=900,
        snapshots=snaps,
    )
    assert r["components"]["velocity"] < 1.3
    assert r["outlier_type"] in ("evergreen", "none")


def test_retention_capped():
    r = outlier_score(
        {"likes": 100, "saves": 100000, "shares": 100000, "views": 1000},
        account_avg_eng=100,
        snapshots=[],
    )
    assert r["components"]["retention"] <= 5.0


def test_missing_metrics_safe():
    r = outlier_score({}, account_avg_eng=0, snapshots=[])
    assert isinstance(r["score"], float)
