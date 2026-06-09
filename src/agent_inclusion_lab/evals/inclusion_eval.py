from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Any, Sequence

import agent_framework as af

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


class InclusionJudgeEvaluator:
    """Native Agent Framework evaluator provider for bespoke inclusion checks."""

    name = "InclusionJudge"

    async def evaluate(
        self,
        items: Sequence[af.EvalItem],
        *,
        eval_name: str = "Inclusion Eval",
    ) -> af.EvalResults:
        passed = 0
        failed = 0
        item_results: list[af.EvalItemResult] = []
        per_evaluator: dict[str, dict[str, int]] = {
            spec.eval_name: {"passed": 0, "failed": 0, "errored": 0}
            for spec in _EVAL_SPECS
        }

        for index, item in enumerate(items):
            judged = [_judge_single_eval(spec=spec, text=item.response) for spec in _EVAL_SPECS]
            overall_score = round(sum(result["score"] for result in judged) / len(judged), 2)
            overall_pass = all(result["pass"] for result in judged)
            status = "pass" if overall_pass else "fail"
            if overall_pass:
                passed += 1
            else:
                failed += 1

            scores: list[af.EvalScoreResult] = []
            for result in judged:
                metric_name = str(result["eval_name"])
                metric_pass = bool(result["pass"])
                if metric_pass:
                    per_evaluator[metric_name]["passed"] += 1
                else:
                    per_evaluator[metric_name]["failed"] += 1
                scores.append(
                    af.EvalScoreResult(
                        name=metric_name,
                        score=float(result["score"]),
                        passed=metric_pass,
                        sample={
                            "rationale": result["rationale"],
                            "evidence_spans": result["evidence_spans"],
                            "improvement_advice": result["improvement_advice"],
                        },
                    )
                )

            item_results.append(
                af.EvalItemResult(
                    item_id=str(index),
                    status=status,
                    scores=scores,
                    input_text=item.query,
                    output_text=item.response,
                    metadata={
                        "overall_score": overall_score,
                        "overall_pass": overall_pass,
                        "evals": judged,
                    },
                )
            )

        return af.EvalResults(
            provider=self.name,
            eval_id="inclusion-judge-v1",
            run_id=eval_name,
            status="completed",
            result_counts={"passed": passed, "failed": failed, "errored": 0},
            per_evaluator=per_evaluator,
            items=item_results,
            error=None,
        )


def evaluate_text(text: str) -> dict[str, Any]:
    return asyncio.run(evaluate_text_async(text))


async def evaluate_text_async(text: str) -> dict[str, Any]:
    response = af.AgentResponse(
        messages=[af.Message("assistant", [text])],
        agent_id="inclusion.eval.target",
    )
    import warnings

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message=".*\\[EVALS\\].*")
        results = await af.evaluate_agent(
            responses=response,
            queries="Evaluate this job posting text for inclusive language quality.",
            evaluators=InclusionJudgeEvaluator(),
            eval_name="Inclusion Judge",
        )

    if not results:
        raise RuntimeError("No evaluation results were produced.")
    if not results[0].items:
        raise RuntimeError("Evaluation result did not include item-level outputs.")

    item = results[0].items[0]
    metadata = item.metadata or {}
    evals = metadata.get("evals")
    if not isinstance(evals, list):
        raise RuntimeError("Evaluation metadata was missing eval details.")

    parsed_evals: list[dict[str, Any]] = []
    for result in evals:
        parsed_evals.append(
            {
                "eval_name": str(result.get("eval_name", "")),
                "score": int(result.get("score", 1)),
                "pass": bool(result.get("pass", False)),
                "rationale": str(result.get("rationale", "")).strip() or "No rationale returned.",
                "evidence_spans": [
                    str(span).strip()
                    for span in result.get("evidence_spans", [])
                    if str(span).strip()
                ][:6],
                "improvement_advice": (
                    str(result.get("improvement_advice", "")).strip()
                    or "Revise wording toward neutral, competency-based criteria."
                ),
            }
        )

    return {
        "overall_score": float(metadata.get("overall_score", 0.0)),
        "overall_pass": bool(metadata.get("overall_pass", False)),
        "evals": parsed_evals,
    }


def _judge_single_eval(spec: EvalSpec, text: str) -> dict[str, Any]:
    prompt = _build_eval_prompt(spec=spec, text=text)
    parsed = _judge_with_retry(prompt=prompt, attempts=2)
    if parsed is None:
        # Graceful degradation: a single malformed judge response should not abort
        # the whole baseline/reviewed/evals command during a live workshop.
        return {
            "eval_name": spec.eval_name,
            "score": spec.pass_threshold - 1,
            "pass": False,
            "rationale": "Judge response could not be parsed; treated as not passing.",
            "evidence_spans": [],
            "improvement_advice": "Re-run the evaluation; the model returned unparseable output.",
        }

    score_raw = parsed.get("score", 1)
    score = int(score_raw) if isinstance(score_raw, (int, float, str)) else 1
    if score < 1:
        score = 1
    if score > 5:
        score = 5

    rationale = str(parsed.get("rationale", "")).strip()
    advice = str(parsed.get("improvement_advice", "")).strip()
    evidence = parsed.get("evidence_spans", [])
    evidence_spans = (
        [str(item).strip() for item in evidence if str(item).strip()]
        if isinstance(evidence, list)
        else []
    )

    return {
        "eval_name": spec.eval_name,
        "score": score,
        "pass": score >= spec.pass_threshold,
        "rationale": rationale or "No rationale returned.",
        "evidence_spans": evidence_spans[:6],
        "improvement_advice": advice or "Revise wording toward neutral, competency-based criteria.",
    }


def _judge_with_retry(prompt: str, attempts: int) -> dict[str, Any] | None:
    for _ in range(max(1, attempts)):
        try:
            raw = generate_text(prompt)
            return _parse_judge_json(raw=raw)
        except Exception:
            continue
    return None


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
