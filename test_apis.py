# test_apis.py
import os, requests
from dotenv import load_dotenv

load_dotenv()

def test_perplexity():
    r = requests.post(
        "https://api.perplexity.ai/chat/completions",
        headers={"Authorization": f"Bearer {os.getenv('PERPLEXITY_API_KEY')}"},
        json={
            "model": "sonar",
            "messages": [{"role": "user", "content": "What is 2+2?"}],
        },
        timeout=30,
    )
    print("Perplexity:", r.status_code)
    print(r.json()["choices"][0]["message"]["content"][:200])

if __name__ == "__main__":
    test_perplexity()
