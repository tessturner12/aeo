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
from pathlib import Path

DB = Path(__file__).resolve().parent / "aeo.db"

TEST_TOPICS         = {"fixed_fee_positioning"}
NEAR_CONTROL_TOPICS = {"general_recommendation", "switching_accountants"}

BASELINE_AFTER_RUNS = {"fixed_fee_positioning": 10, "general_recommendation": 5}  # must match rig.py
DEFAULT_BASELINE_AFTER_RUNS = 3

CANARY_RUNS_TEST_NEAR = 3
CANARY_RUNS_FAR       = 2

PER_CALL_ESTIMATE = {
    "perplexity": 0.01,
    "claude": 0.05,   # standard Sonnet 5 pricing (use 0.035 if before 2026-08-31 intro cutoff)
    "openai": 0.07,   # skewed slightly above the 0.065 average to reflect real variance
}


def runs_for_topic(topic, mode):
    if mode == "canary":
        if topic in TEST_TOPICS or topic in NEAR_CONTROL_TOPICS:
            return CANARY_RUNS_TEST_NEAR
        return CANARY_RUNS_FAR
    return BASELINE_AFTER_RUNS.get(topic, DEFAULT_BASELINE_AFTER_RUNS)


def estimate(mode):
    conn = sqlite3.connect(DB)
    rows = conn.execute(
        "SELECT id, topic FROM questions WHERE is_product = 1"
    ).fetchall()

    total_calls = 0
    total_cost = 0.0
    per_surface_calls = {s: 0 for s in PER_CALL_ESTIMATE}

    for _, topic in rows:
        n = runs_for_topic(topic, mode)
        for surface, per_call in PER_CALL_ESTIMATE.items():
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
