import json
import os
from datetime import datetime
from pathlib import Path

from ollama import chat

MODEL = os.getenv("AVENGERS_MODEL", "smtek/Qwen3.8-27B:Q3_K_M")
SESSIONS_DIR = Path("sessions")

AGENTS = {
    "Tony Stark": """
You are Tony Stark on an AI advisory council.
Your specialty is engineering, implementation, automation, software, systems thinking,
cost/benefit tradeoffs, and finding a solution that can actually be built.

Do not merely agree with the user. Work independently.
Call out technical limitations and bad assumptions.
Prefer concrete implementation details over vague advice.
Separate facts from assumptions when uncertainty matters.
""",
    "Bruce Banner": """
You are Bruce Banner on an AI advisory council.
Your specialty is careful analysis, evidence, quantitative reasoning, science,
uncertainty, and checking whether claims are actually supported.

Do not merely agree with the user. Work independently.
Look for missing evidence, edge cases, and alternative explanations.
Be precise about what is known versus inferred.
""",
    "Steve Rogers": """
You are Steve Rogers on an AI advisory council.
Your specialty is practical judgment, reliability, safety, long-term consequences,
human impact, and whether a proposal remains sensible outside ideal conditions.

Do not merely agree with the user. Work independently.
Identify unnecessary complexity, avoidable risk, and plans that sound impressive
but are fragile in real life.
""",
    "Natasha Romanoff": """
You are Natasha Romanoff on an AI advisory council.
Your specialty is adversarial analysis: hidden assumptions, failure modes,
security/privacy concerns, incentives, loopholes, and things the other analysts may miss.

Do not merely agree with the user. Work independently.
Stress-test the question and proposed solutions without being contrarian for its own sake.
""",
}

FURY_SYSTEM = """
You are Nick Fury, director of an AI advisory council called The Avengers.

You receive the user's original question plus independent analyses from several council members.
Your job is NOT to take a majority vote.

Instead:
1. Identify where the council agrees.
2. Resolve disagreements using the strongest reasoning and evidence available.
3. Flag important uncertainty rather than hiding it.
4. Produce one coherent, practical final answer.
5. Preserve useful minority viewpoints when they reveal a real risk or alternative.
6. Do not mention internal chain-of-thought. Summarize reasoning at a useful level.
7. End with concrete next steps when the question calls for action.

Be decisive when the evidence supports it, but do not pretend certainty where none exists.
"""

CRITIC_SYSTEM = """
You are reviewing several independent answers to the same question.
Do not rewrite the whole answer.

For each candidate:
- identify its strongest point,
- identify any factual/logical weakness,
- identify an important omission,
- say what should survive into the final synthesis.

Then note any disagreement that the director must explicitly resolve.
"""


def call_model(system_prompt: str, user_prompt: str, temperature: float = 0.4) -> str:
    response = chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": user_prompt.strip()},
        ],
        options={"temperature": temperature},
    )
    return response.message.content.strip()


def get_independent_answers(question: str) -> dict:
    answers = {}

    print("\nASSEMBLING THE AVENGERS...\n")
    for name, system_prompt in AGENTS.items():
        print(f"[{name}] analyzing...")
        prompt = f"""
Original question:
{question}

Give your independent assessment from your assigned specialty.
Do not reference other council members because you have not seen their answers.
Be concise but substantive.
"""
        answers[name] = call_model(system_prompt, prompt)
        print(f"[{name}] complete.\n")

    return answers


def run_critique_round(question: str, answers: dict) -> dict:
    anonymized = "\n\n".join(
        f"Candidate {i + 1}:\n{text}"
        for i, text in enumerate(answers.values())
    )

    critiques = {}
    print("BEGINNING CROSS-EXAMINATION...\n")

    for name, specialty in AGENTS.items():
        print(f"[{name}] reviewing the council...")
        prompt = f"""
Original question:
{question}

Independent candidate answers:
{anonymized}

Review these answers from your own specialty.
Focus on errors, omissions, disagreements, and what the final director should preserve.
"""
        critiques[name] = call_model(
            specialty + "\n\n" + CRITIC_SYSTEM,
            prompt,
            temperature=0.25,
        )
        print(f"[{name}] review complete.\n")

    return critiques


def fury_synthesis(question: str, answers: dict, critiques: dict | None = None) -> str:
    council_text = "\n\n".join(
        f"### {name}\n{text}"
        for name, text in answers.items()
    )

    critique_text = ""
    if critiques:
        critique_text = "\n\nCROSS-EXAMINATION:\n" + "\n\n".join(
            f"### {name}'s review\n{text}"
            for name, text in critiques.items()
        )

    prompt = f"""
USER'S QUESTION:
{question}

INDEPENDENT COUNCIL ANALYSES:
{council_text}
{critique_text}

Produce the Avengers' final response.
Do not simply concatenate the answers.
Resolve the important disagreements and give the user the strongest synthesized answer.
"""

    return call_model(FURY_SYSTEM, prompt, temperature=0.25)


def save_session(question: str, answers: dict, final_answer: str, critiques=None):
    SESSIONS_DIR.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = SESSIONS_DIR / f"council_{stamp}.json"

    payload = {
        "timestamp": datetime.now().isoformat(),
        "model": MODEL,
        "question": question,
        "answers": answers,
        "critiques": critiques,
        "final_answer": final_answer,
    }

    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def print_banner():
    print(r"""
============================================================
                  THE AVENGERS - AI COUNCIL
============================================================
 Tony Stark       Engineering / Implementation
 Bruce Banner     Evidence / Analysis
 Steve Rogers     Practicality / Risk
 Natasha Romanoff Adversarial Review
 Nick Fury        Final Synthesis
------------------------------------------------------------
 Model: """ + MODEL + "\n")


def main():
    print_banner()

    while True:
        question = input("Ask the Avengers (or type 'exit'): ").strip()

        if not question:
            continue
        if question.lower() in {"exit", "quit"}:
            print("Council dismissed.")
            break

        mode = input("Mode [Enter = standard, D = deep cross-examination]: ").strip().lower()
        deep = mode == "d"

        try:
            answers = get_independent_answers(question)

            critiques = None
            if deep:
                critiques = run_critique_round(question, answers)

            print("[Nick Fury] reviewing the council...\n")
            final_answer = fury_synthesis(question, answers, critiques)

            print("\n" + "=" * 60)
            print("NICK FURY - FINAL BRIEF")
            print("=" * 60 + "\n")
            print(final_answer)
            print()

            saved = save_session(question, answers, final_answer, critiques)
            print(f"[Session saved to {saved}]\n")

        except Exception as exc:
            print("\nThe council hit an error:")
            print(exc)
            print("\nMake sure Ollama is running and the configured model is installed.\n")


if __name__ == "__main__":
    main()
