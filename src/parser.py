# parser.py
import json, os
from pathlib import Path
from dotenv import load_dotenv
from anthropic import Anthropic

# Load independently rather than relying on whoever imports this module
# having already loaded .env first — that assumption broke a real run
# on 2026-08-12 (see rig.py's load_dotenv comment and log.md).
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

PARSE_PROMPT = """You are analysing an AI assistant's answer to a
question about accountants for UK contractors and small limited
companies.

Extract, as JSON only, no other text:

{{
  "brand_mentioned": true/false,
  "brand_position": <int or null>,
  "recommended": true/false,
  "recommendation_rank": <int or null>,
  "competitors_named": [<strings>],
  "sentiment": "positive" | "neutral" | "negative" | null,
  "products_named_at_all": true/false
}}

Rules:
- brand = "{brand}" (an accountancy firm at mightyaccounting.com,
  run by Mark and James). Count it ONLY when referring to this
  specific accountancy firm. Do NOT count the ordinary adjective
  "mighty", nor unrelated companies like "Mighty Networks" or
  "MightyRecruiter".
- brand_position: 1 if it's the first firm named, 2 if second,
  etc. null if absent.
- recommended: true ONLY if the answer actively suggests or endorses
  the brand as a choice — not merely names it. "Mighty Accounting is
  a small UK accountant. However, Gorilla Accounting has more
  experience..." mentions the brand but does NOT recommend it —
  recommended must be false here. A shortlist entry with no negative
  qualifier ("consider Mighty Accounting, Gorilla, or Crunch") counts
  as recommended: true.
- recommendation_rank: 1 if the brand is the first/primary
  recommendation, 2 if second-ranked, etc. null if recommended is
  false.
- competitors_named: every OTHER accountancy firm named, exact
  names (e.g. "Gorilla Accounting", "GoForma", "Crunch",
  "QAccounting", "Caroola", "SJD Accountancy", "Brookson").
- sentiment: how the brand is characterised. null if absent.
- products_named_at_all: false if the answer names no specific
  accountancy firms at all (i.e. it's a purely informational
  answer about IR35, company setup, etc. with no named providers).

ANSWER:
{answer}"""


def parse_answer(answer_text, brand="Mighty Accounting"):
    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",   # cheap; this is easy work
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": PARSE_PROMPT.format(brand=brand, answer=answer_text),
        }],
    )
    raw = msg.content[0].text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"parse_ok": False, "raw": raw}
