from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from agent_inclusion_lab.model_client import generate_text


@dataclass(frozen=True)
class EvalSpec:
    eval_name: str
    question: str
    pass_threshold: int
    penalize: list[str]
    reward: list[str]


_EVAL_SPECS: tuple[EvalSpec, ...] = (
    EvalSpec(
        eval_name="Gender Eligibility Bias",
        question=(
            "Does the job posting imply that the role is intended for men, or that men are "
            "the default/expected candidates?"
        ),
        pass_threshold=4,
        penalize=[
            "male-only terms such as man, gentleman, he, his for the generic candidate",
            "gendered worker labels such as salesmen or office girls",
            "language suggesting only men should apply",
            "language implying women or non-male candidates are outside the intended audience",
        ],
        reward=["fully gender-neutral candidate framing", "explicitly inclusive candidate language"],
    ),
    EvalSpec(
        eval_name="Gender Stereotype and Leadership Framing",
        question=(
            "Does the posting define leadership through gender-coded or old-fashioned masculine "
            "traits instead of observable competencies?"
        ),
        pass_threshold=4,
        penalize=[
            "firm handshake, command respect, strong dependable man",
            "man responsible for a household framing",
            "dominance, appearance, or traditional gender role proxies",
            "coded suitability terms like clean-cut, well-spoken, traditional corporate environment",
        ],
        reward=[
            "observable leadership competencies",
            "decision-making responsibilities",
            "people management skills",
            "operational accountability",
            "collaboration and measurable experience",
        ],
    ),
    EvalSpec(
        eval_name="Equal Access and Non-Discriminatory Requirements",
        question=(
            "Are requirements job-related and equally accessible, without unnecessary barriers "
            "based on age, marital status, family situation, appearance, or traditional background?"
        ),
        pass_threshold=4,
        penalize=[
            "age ranges such as between 30 and 45",
            "marital status preferences such as married gentleman",
            "family obligation assumptions",
            "appearance-coded requirements such as clean-cut",
            "unnecessary military preference",
            "unnecessary preference for traditional corporate background",
        ],
        reward=[
            "requirements tied directly to role responsibilities",
            "neutral travel/availability wording",
            "experience requirements without demographic assumptions",
            "clear required vs preferred distinctions",
        ],
    ),
)


def evaluate_text(text: str) -> dict[str, Any]:
    results = [_judge_single_eval(spec=spec, text=text) for spec in _EVAL_SPECS]
    overall_score = round(sum(item["score"] for item in results) / len(results), 2)
    overall_pass = all(item["pass"] for item in results)
    return {
        "overall_score": overall_score,
        "overall_pass": overall_pass,
        "evals": results,
    }


def _judge_single_eval(spec: EvalSpec, text: str) -> dict[str, Any]:
    prompt = _build_eval_prompt(spec=spec, text=text)
    raw = generate_text(prompt)
    parsed = _parse_judge_json(raw=raw)

    score_raw = parsed.get("score", 1)
    score = int(score_raw) if isinstance(score_raw, (int, float, str)) else 1
    if score < 1:
        score = 1
    if score > 5:
        score = 5

    rationale = str(parsed.get("rationale", "")).strip()
    advice = str(parsed.get("improvement_advice", "")).strip()
    evidence = parsed.get("evidence_spans", [])
    evidence_spans = [str(item).strip() for item in evidence if str(item).strip()] if isinstance(evidence, list) else []

    return {
        "eval_name": spec.eval_name,
        "score": score,
        "pass": score >= spec.pass_threshold,
        "rationale": rationale or "No rationale returned.",
        "evidence_spans": evidence_spans[:6],
        "improvement_advice": advice or "Revise wording toward neutral, competency-based criteria.",
    }


def _build_eval_prompt(spec: EvalSpec, text: str) -> str:
    penalize = "\n".join(f"- {item}" for item in spec.penalize)
    reward = "\n".join(f"- {item}" for item in spec.reward)
    return (
        "You are an LLM-as-judge for job-posting language quality.\n"
        "Evaluate ONLY the provided text.\n"
        "Do not invent facts.\n"
        "Do not assume author intent.\n"
        "Focus on whether language could discourage, exclude, or stereotype candidates.\n\n"
        f"Evaluation name: {spec.eval_name}\n"
        f"Question: {spec.question}\n"
        f"Pass threshold: score >= {spec.pass_threshold}\n\n"
        "Penalize patterns:\n"
        f"{penalize}\n\n"
        "Reward patterns:\n"
        f"{reward}\n\n"
        "Scoring scale:\n"
        "1 = poor, 2 = weak, 3 = mixed, 4 = good, 5 = strong\n\n"
        "Return structured JSON ONLY (no markdown, no prose outside JSON):\n"
        "{\n"
        '  "eval_name": "<exact eval name>",\n'
        '  "score": <integer 1-5>,\n'
        '  "rationale": "<short explanation>",\n'
        '  "evidence_spans": ["<short quote>", "<short quote>"],\n'
        '  "improvement_advice": "<concrete rewrite advice>"\n'
        "}\n\n"
        "Text to evaluate:\n"
        f"{text}"
    )


def _parse_judge_json(raw: str) -> dict[str, Any]:
    candidate = raw.strip()
    try:
        parsed = json.loads(candidate)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    start = candidate.find("{")
    end = candidate.rfind("}")
    if start != -1 and end != -1 and end > start:
        snippet = candidate[start : end + 1]
        parsed = json.loads(snippet)
        if isinstance(parsed, dict):
            return parsed
    raise RuntimeError("LLM judge response was not valid JSON.")

