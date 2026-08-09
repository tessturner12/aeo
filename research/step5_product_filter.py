# step5_product_filter.py
#
# Day 2 Step 5 — the product question filter, scripted.
# Run this once you've done Appendix B's Perplexity smoke test (Day 3).
#
# For every question in questions.csv that doesn't already have an
# is_product value, asks it once via Perplexity, then uses a cheap LLM
# call (not regex — see Appendix G's reasoning) to judge whether any
# specific accountancy firm was named in the answer.
#
# Rows already tagged TRUE/FALSE are left untouched, so this picks up
# where the manual spot-check left off. Rows tagged BORDERLINE are
# treated as unresolved and get re-checked here for a real answer.

import os, csv, time, random
import requests
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

CSV_PATH = "questions.csv"
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


def run_filter():
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    fieldnames = list(rows[0].keys())
    to_check = [r for r in rows if not r["is_product"] or r["is_product"] == "BORDERLINE"]

    print(f"{len(rows)} total questions, {len(to_check)} need checking")

    for i, row in enumerate(to_check, 1):
        try:
            answer = ask_perplexity(row["text"])
            result = is_product_question(answer)
            row["is_product"] = "TRUE" if result else "FALSE"
            note = f"scripted Step 5 check, {time.strftime('%Y-%m-%d')}"
            row["notes"] = (row["notes"] + " | " + note).strip(" |") if row["notes"] else note
            print(f"[{i}/{len(to_check)}] {row['id']}: {row['is_product']} — {row['text'][:60]}")
        except Exception as e:
            print(f"[{i}/{len(to_check)}] {row['id']}: ERROR — {e}")
            row["is_product"] = ""

        # save after every row so a crash doesn't lose progress
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        time.sleep(random.uniform(0.5, 1.5))

    kept = sum(1 for r in rows if r["is_product"] == "TRUE")
    deleted = sum(1 for r in rows if r["is_product"] == "FALSE")
    print(f"\nDone. {kept} product questions kept, {deleted} flagged for deletion.")
    print("Review the FALSE rows before deleting — spot-check a handful first.")


if __name__ == "__main__":
    run_filter()
