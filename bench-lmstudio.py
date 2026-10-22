"""Benchmark the local LM Studio server (default: qwen-coder on localhost:1234).

Measures, for each case:
  - prompt processing speed (prompt tokens / time to first token)
  - generation speed (tokens per second, as reported by LM Studio)

Usage:
  py bench-lmstudio.py                 # all cases, 3 runs each
  py bench-lmstudio.py --runs 1 --model qwen-coder --url http://localhost:1234
"""
import argparse
import json
import statistics
import urllib.request

FILLER = (
    "def process(items):\n"
    "    result = []\n"
    "    for i, item in enumerate(items):\n"
    "        if item is None:\n"
    "            continue\n"
    "        result.append((i, str(item).strip().lower()))\n"
    "    return result\n\n"
)


def long_prompt(approx_tokens):
    # ~48 tokens per FILLER block (measured with the Qwen tokenizer)
    code = FILLER * max(1, approx_tokens // 48)
    return f"Here is some code:\n\n{code}\nIn one sentence, what does the function do?"


CASES = [
    ("short answer", "Write a Python function that checks if a number is prime.", 2000),
    ("coding task", "Write a Python class implementing an LRU cache with get/put in O(1), "
                    "with type hints, a docstring and three unit tests using unittest.", 6000),
    ("8K-token prompt", long_prompt(8000), 2000),
    ("32K-token prompt", long_prompt(32000), 2000),
]


def run(url, model, prompt, max_tokens):
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.2,
    }).encode()
    req = urllib.request.Request(f"{url}/api/v0/chat/completions", body,
                                 {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=900) as r:
        res = json.load(r)
    s, u = res["stats"], res["usage"]
    ttft = s["time_to_first_token"]
    return {
        "prompt_tokens": u["prompt_tokens"],
        "completion_tokens": u["completion_tokens"],
        "ttft": ttft,
        "prefill_tps": u["prompt_tokens"] / ttft if ttft else 0.0,
        "gen_tps": s["tokens_per_second"],
        "total": ttft + s["generation_time"],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:1234")
    ap.add_argument("--model", default="qwen-coder")
    ap.add_argument("--runs", type=int, default=3)
    a = ap.parse_args()

    print(f"Benchmarking {a.model} at {a.url}, {a.runs} run(s) per case\n")
    run(a.url, a.model, "Say hi.", 50)  # warm-up

    header = f"{'case':<18}{'prompt tok':>11}{'out tok':>9}{'first token':>13}{'read tok/s':>12}{'write tok/s':>13}{'total':>9}"
    print(header)
    print("-" * len(header))
    for name, prompt, max_tokens in CASES:
        # Vary the prompt per run so LM Studio's prompt cache can't skip the work.
        rs = [run(a.url, a.model, f"[run {i}] {prompt}", max_tokens) for i in range(a.runs)]
        med = lambda k: statistics.median(r[k] for r in rs)
        print(f"{name:<18}{med('prompt_tokens'):>11.0f}{med('completion_tokens'):>9.0f}"
              f"{med('ttft'):>12.2f}s{med('prefill_tps'):>12.0f}{med('gen_tps'):>13.1f}{med('total'):>8.1f}s")
    print("\nMedians. 'read tok/s' = prompt processing; 'write tok/s' = generation.")


if __name__ == "__main__":
    main()
