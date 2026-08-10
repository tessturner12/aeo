# rig.py
import os, sys, json, time, sqlite3, random
from datetime import datetime
from pathlib import Path
import requests
from dotenv import load_dotenv
from anthropic import Anthropic
from openai import OpenAI

from parser import parse_answer

load_dotenv()

BRAND = "Mighty Accounting"
DB    = Path(__file__).resolve().parent / "aeo.db"

MODE = sys.argv[1] if len(sys.argv) > 1 else "baseline"
assert MODE in ("baseline", "canary", "after"), "usage: python rig.py [baseline|canary|after]"

# Verified 2026-08-10 against live Anthropic/OpenAI docs before trusting
# this in an unattended run — see log.md for what changed and why.
CLAUDE_MODEL  = "claude-sonnet-5"     # claude-sonnet-4-5 is a stale/legacy alias
OPENAI_MODEL  = "gpt-5.6-terra"       # gpt-4o-search-preview is deprecated,
                                       # shutdown 2026-07-23 — already past that date

anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
openai_client    = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ---------- RUN ALLOCATION ----------
# Cohort tiers — fixed_fee_positioning is the test cluster (diagnosed Day-1
# gap: Mighty's own hero copy says "£60pm + VAT", not "fixed fee"). Near
# control is semantically close enough to plausibly show intervention
# spillover; far control should stay flat. No holdout tier — see log.md,
# 2026-08-10: an untouched-forever cluster wasn't worth the N it would cost
# on an already question-poor dataset, and the near/far split plus the
# direct cited-URL spillover check (Appendix M) cover what holdout was for.
TEST_TOPICS        = {"fixed_fee_positioning"}
NEAR_CONTROL_TOPICS = {"general_recommendation", "switching_accountants"}
# everything else (tax_efficiency, software_compatibility, ir35_compliance,
# freelancer_agency) is far control.

# Baseline/after: weight toward the two clusters big enough to support a
# real confidence interval. fixed_fee_positioning gets N=10, not just N=5 —
# power.py (Appendix K) run against realistic Day-1-derived baseline rates
# (2-10%) showed N=5 (n=50) only reaches 29-56% power to detect even a
# generous +10pp lift from the planned (weak, cooperation-free) interventions.
# N=10 (n=100) gets that to 52-85% power for +$13 total — see log.md,
# 2026-08-10. general_recommendation stays at N=5 — it's a control
# comparator, not the hypothesis under test, doesn't need the same power.
BASELINE_AFTER_RUNS = {"fixed_fee_positioning": 10, "general_recommendation": 5}
DEFAULT_BASELINE_AFTER_RUNS = 3

# Canary: full coverage, lighter than baseline/after. Test + near-control get
# enough runs to see if a signal recurs; far-control just needs a flatness
# check. Sized to land near $10-13 for the whole canary pass — see log.md.
CANARY_RUNS_TEST_NEAR = 3
CANARY_RUNS_FAR       = 2


def runs_for_topic(topic):
    if MODE == "canary":
        if topic in TEST_TOPICS or topic in NEAR_CONTROL_TOPICS:
            return CANARY_RUNS_TEST_NEAR
        return CANARY_RUNS_FAR
    return BASELINE_AFTER_RUNS.get(topic, DEFAULT_BASELINE_AFTER_RUNS)


# ---------- SURFACES ----------

def ask_perplexity(question):
    r = requests.post(
        "https://api.perplexity.ai/chat/completions",
        headers={"Authorization": f"Bearer {os.getenv('PERPLEXITY_API_KEY')}"},
        json={
            "model": "sonar",
            "messages": [{"role": "user", "content": question}],
            "temperature": 1.0,
        },
        timeout=60,
    )
    r.raise_for_status()
    data = r.json()
    return data["choices"][0]["message"]["content"], data.get("citations", [])


def ask_claude(question):
    """
    Response shapes verified against platform.claude.com/docs (2026-08-10):
    - a `web_search_tool_result` block's `.content` is a LIST of
      `web_search_result` items on success, but a SINGLE error object
      (`web_search_tool_result_error`) on failure — never assume it's
      iterable.
    - citations live on `text` blocks as `.citations`, each item typed
      `web_search_result_location` with a `.url` field.
    - a long-running search turn can end with stop_reason "pause_turn";
      the documented fix is to resend the paused assistant message
      unchanged, not to treat it as a normal answer.
    - `max_uses: 1` caps re-searching within a turn. Each search is billed
      separately ($10/1000) on top of tokens, and web search results are
      the dominant cost driver (~20k input tokens per call uncapped, ~9-12k
      capped) — measured real cost dropped from ~$0.08-0.10/call to
      ~$0.035-0.05/call with this alone. Real, but not free: fewer searches
      can mean thinner citation lists per single answer. N_RUNS repetition
      is the mitigation — multiple independent samples per question matter
      more for this project's SoA-by-topic analysis than exhaustive search
      depth on any one call.
    """
    messages = [{"role": "user", "content": question}]
    text = ""
    urls = []

    for _ in range(3):  # bounded pause_turn resumption
        msg = anthropic_client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=1024,
            tools=[{
                "type": "web_search_20250305",
                "name": "web_search",
                "max_uses": 1,
            }],
            messages=messages,
        )

        for block in msg.content:
            if block.type == "text":
                text += block.text
                for citation in getattr(block, "citations", None) or []:
                    url = getattr(citation, "url", None)
                    if url:
                        urls.append(url)
            elif block.type == "web_search_tool_result":
                content = getattr(block, "content", None)
                if isinstance(content, list):  # error case is a single object, skip it
                    for result in content:
                        url = getattr(result, "url", None)
                        if url:
                            urls.append(url)

        if msg.stop_reason != "pause_turn":
            break
        messages = [
            {"role": "user", "content": question},
            {"role": "assistant", "content": msg.content},
        ]

    return text, list(dict.fromkeys(urls))  # de-duped, order preserved


def ask_openai(question):
    """
    gpt-4o-search-preview + chat.completions is deprecated and past its
    shutdown date. Current path is the Responses API's web_search tool;
    citations arrive as `url_citation` annotations on the message's
    output_text content block. Verified against developers.openai.com
    docs 2026-08-10.

    `search_context_size: "low"` is a real, documented cost lever here —
    but measured across 3 real test calls it did NOT reliably cut tokens
    the way Claude's max_uses did (one call came back higher than the
    unset-parameter baseline; two others came back much lower). OpenAI's
    own docs say it "does not guarantee a specific number of sources" —
    treat this as a mild average-case saving, not a hard cap, and don't
    assume any single call landed cheap.
    """
    resp = openai_client.responses.create(
        model=OPENAI_MODEL,
        tools=[{"type": "web_search", "search_context_size": "low"}],
        input=question,
    )
    urls = []
    for item in getattr(resp, "output", None) or []:
        if getattr(item, "type", None) != "message":
            continue
        for content in getattr(item, "content", None) or []:
            for annotation in getattr(content, "annotations", None) or []:
                if getattr(annotation, "type", None) == "url_citation":
                    url = getattr(annotation, "url", None)
                    if url:
                        urls.append(url)
    return resp.output_text, list(dict.fromkeys(urls))


SURFACES = {
    "perplexity": (ask_perplexity, "sonar"),
    "claude":     (ask_claude,     CLAUDE_MODEL),
    "openai":     (ask_openai,     OPENAI_MODEL),
}


# ---------- MAIN LOOP ----------

def run_cycle():
    conn = sqlite3.connect(DB)
    questions = conn.execute(
        "SELECT id, text, topic FROM questions WHERE is_product = 1"
    ).fetchall()

    total_calls = sum(runs_for_topic(topic) for _, _, topic in questions) * len(SURFACES)
    print(f"[{datetime.now()}] Starting {MODE} cycle: "
          f"{len(questions)} questions x {len(SURFACES)} surfaces, "
          f"weighted runs -> {total_calls} calls")

    for qid, qtext, topic in questions:
        n_runs = runs_for_topic(topic)
        for surface_name, (fn, model) in SURFACES.items():
            for run_index in range(n_runs):
                try:
                    answer, urls = fn(qtext)
                    parsed = (parse_answer(answer, BRAND)
                              if answer else {"brand_mentioned": None})

                    conn.execute("""
                        INSERT INTO runs (
                            question_id, surface, model, run_index, ts,
                            raw_answer, cited_urls, brand_mentioned,
                            brand_position, competitors_named, parse_ok,
                            checkpoint
                        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                    """, (
                        qid, surface_name, model, run_index,
                        datetime.now().isoformat(),
                        answer,
                        json.dumps(urls),
                        parsed.get("brand_mentioned"),
                        parsed.get("brand_position"),
                        json.dumps(parsed.get("competitors_named", [])),
                        parsed.get("parse_ok", True),
                        MODE,
                    ))
                    conn.commit()

                except Exception as e:
                    print(f"  ERROR {qid}/{surface_name}/{run_index}: {e}")
                    conn.execute("""
                        INSERT INTO runs (
                            question_id, surface, model, run_index, ts,
                            raw_answer, parse_ok, error, checkpoint
                        ) VALUES (?,?,?,?,?,?,?,?,?)
                    """, (qid, surface_name, model, run_index,
                          datetime.now().isoformat(), "", 0, str(e), MODE))
                    conn.commit()

                time.sleep(random.uniform(0.5, 1.5))

    conn.close()
    print(f"[{datetime.now()}] {MODE} cycle complete")


if __name__ == "__main__":
    run_cycle()
