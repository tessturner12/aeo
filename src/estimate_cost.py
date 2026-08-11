# estimate_cost.py
#
# Dry-run cost check before spending real money. Run this BEFORE every
# `python rig.py [baseline|canary|after]` call — that's the whole point of
# it existing after the nightly-cron budget scare (see log.md, 2026-08-10).
#
# Per-call estimates below are real measured averages (not guesses) from
# test calls against claude-sonnet-5 with max_uses=1 and gpt-5.6-terra with
# search_context_size="low" — see log.md for the raw numbers. OpenAI in
# particular showed high variance call-to-call (4.5k-42.7k input tokens
# across 3 test calls), so treat this as a central estimate, not a ceiling.
# Re-run a handful of real calls and update these figures periodically —
# don't let them go stale the way the original $0.04 guesses did.
import sys
import sqlite3
import yaml
from pathlib import Path

DB = Path(__file__).resolve().parent / "aeo.db"


def load_config():
    with open(Path(__file__).resolve().parent / "config.yaml") as f:
        return yaml.safe_load(f)


# Derived from config.yaml (added 2026-08-10) — the same file rig.py reads,
# so these two can no longer drift out of sync the way they did before.
_config = load_config()
TEST_TOPICS         = set(_config["test_topics"])
NEAR_CONTROL_TOPICS = set(_config["near_control_topics"])
MATCHED_PAIR_TOPICS = set(_config["matched_pair_topics"])
BASELINE_AFTER_RUNS = _config["baseline_after_runs"]
DEFAULT_BASELINE_AFTER_RUNS = _config["default_baseline_after_runs"]
CANARY_RUNS_TEST_NEAR = _config["canary_runs_test_near"]
CANARY_RUNS_FAR       = _config["canary_runs_far"]
SURFACE_RUN_CAPS      = _config.get("surface_run_caps", {})

PER_CALL_ESTIMATE = {
    "perplexity": 0.01,
    "claude": 0.05,   # standard Sonnet 5 pricing (use 0.035 if before 2026-08-31 intro cutoff)
    "openai": 0.07,   # skewed slightly above the 0.065 average to reflect real variance
}


def runs_for_topic(topic, mode, surface=None):
    if mode == "canary":
        if topic in MATCHED_PAIR_TOPICS:
            n = 0
        elif topic in TEST_TOPICS or topic in NEAR_CONTROL_TOPICS:
            n = CANARY_RUNS_TEST_NEAR
        else:
            n = CANARY_RUNS_FAR
    else:
        n = BASELINE_AFTER_RUNS.get(topic, DEFAULT_BASELINE_AFTER_RUNS)

    cap = SURFACE_RUN_CAPS.get(surface)
    return min(n, cap) if cap is not None else n


def estimate(mode):
    conn = sqlite3.connect(DB)
    rows = conn.execute(
        "SELECT id, topic FROM questions WHERE is_product = 1"
    ).fetchall()

    total_calls = 0
    total_cost = 0.0
    per_surface_calls = {s: 0 for s in PER_CALL_ESTIMATE}

    for _, topic in rows:
        for surface, per_call in PER_CALL_ESTIMATE.items():
            n = runs_for_topic(topic, mode, surface)
            per_surface_calls[surface] += n
            total_calls += n
            total_cost += n * per_call

    print(f"{mode} run: {len(rows)} questions")
    for surface, calls in per_surface_calls.items():
        print(f"  {surface:12s} {calls:4d} calls  ~${calls * PER_CALL_ESTIMATE[surface]:.2f}")
    print(f"  {'TOTAL':12s} {total_calls:4d} calls  ~${total_cost:.2f}")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "baseline"
    if mode == "all":
        for m in ("baseline", "canary", "after"):
            estimate(m)
            print()
    else:
        estimate(mode)
