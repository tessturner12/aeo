# step5_recheck.py
#
# Re-checks the three clusters that looked unreliable after the first
# Step 5 pass (ir35_compliance, switching_accountants, tax_efficiency)
# with N=3 runs per question and a majority vote, instead of the
# original single-shot check.
#
# Two things this fixes that the original script didn't:
#   1. N=1 -> N=3 majority vote, because the plan's own Day 1 finding
#      is that repeat-asks give different answers - a single draw is
#      not reliable evidence either way.
#   2. Saves every raw Perplexity answer to a log file, so any result
#      that still looks wrong can actually be read, not just trusted.
#
# Only touches rows in the three target clusters. Everything else in
# questions.csv (already-verified rows, general_recommendation,
# fixed_fee_positioning, software_compatibility, new_company_setup,
# freelancer_agency) is left completely untouched.

import os, csv, json, time, random
from collections import Counter
import requests
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

CSV_PATH = "questions.csv"
LOG_PATH = "step5_recheck_log.jsonl"
N_RUNS = 3
TARGET_TOPICS = {"ir35_compliance", "switching_accountants", "tax_efficiency", "fixed_fee_positioning"}

anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

FILTER_PROMPT = """You are checking whether an AI assistant's answer
names any SPECIFIC accountancy firm or accounting company (a proper
noun business name — e.g. "Crunch", "Gorilla Accounting", "Mighty
Accounting"), as opposed to giving purely generic/informational advice
with no named providers.

Rules:
- Software platforms (Xero, FreeAgent, Pandle, QuickBooks) do NOT
  count as accountancy firms on their own.
- Generic advice ("hire a qualified accountant", "look for someone
  ACCA-certified") with no actual named business does NOT count.
- A directory or comparison site listing named firms DOES count.
- If in doubt, answer TRUE only if you could point to an actual firm
  name in the text.

Answer with exactly one word: TRUE or FALSE.

ANSWER TO CHECK:
{answer}"""


def ask_perplexity(question):
    r = requests.post(
        "https://api.perplexity.ai/chat/completions",
        headers={"Authorization": f"Bearer {os.getenv('PERPLEXITY_API_KEY')}"},
        json={
            "model": "sonar",
            "messages": [{"role": "user", "content": question}],
            "temperature": 1.0,  # matches the actual rig - real variance, not suppressed
        },
        timeout=60,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def is_product_question(answer_text):
    msg = anthropic_client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=10,
        messages=[{
            "role": "user",
            "content": FILTER_PROMPT.format(answer=answer_text),
        }],
    )
    raw = msg.content[0].text.strip().upper()
    return "TRUE" in raw


def run_recheck():
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    fieldnames = list(rows[0].keys())

    to_check = [r for r in rows if r["topic"] in TARGET_TOPICS]
    print(f"Rechecking {len(to_check)} questions across {TARGET_TOPICS}, N={N_RUNS} each")

    log_f = open(LOG_PATH, "a", encoding="utf-8")

    for i, row in enumerate(to_check, 1):
        votes = []
        answers = []
        for run in range(N_RUNS):
            try:
                answer = ask_perplexity(row["text"])
                verdict = is_product_question(answer)
                votes.append(verdict)
                answers.append(answer)
            except Exception as e:
                print(f"  run {run+1} error: {e}")
            time.sleep(random.uniform(0.5, 1.5))

        if votes:
            true_count = sum(votes)
            majority = true_count >= (len(votes) / 2)
            row["is_product"] = "TRUE" if majority else "FALSE"
            vote_str = ",".join("T" if v else "F" for v in votes)
            note = f"N={len(votes)} recheck {vote_str} -> {row['is_product']}, {time.strftime('%Y-%m-%d')}"
            row["notes"] = (row["notes"] + " | " + note).strip(" |") if row["notes"] else note
            print(f"[{i}/{len(to_check)}] {row['id']}: votes={vote_str} -> {row['is_product']} — {row['text'][:55]}")
        else:
            print(f"[{i}/{len(to_check)}] {row['id']}: all runs failed, leaving blank")

        log_f.write(json.dumps({
            "id": row["id"], "text": row["text"], "votes": votes, "answers": answers
        }) + "\n")
        log_f.flush()

        # save CSV after every question so a crash doesn't lose progress
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    log_f.close()

    kept = sum(1 for r in to_check if r["is_product"] == "TRUE")
    print(f"\nDone. {kept}/{len(to_check)} kept as product questions after N={N_RUNS} recheck.")
    print(f"Raw answers saved to {LOG_PATH} — worth a quick skim on any result that still looks off.")


if __name__ == "__main__":
    run_recheck()
