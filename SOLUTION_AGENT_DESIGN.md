# Workshop Agent Design: Making Assumptions Visible

## Purpose

The system demonstrates that weak source guidance can produce plausible but assumption-heavy leadership text, and that structured specialist review improves outcomes.

## Agent responsibilities

| Agent | Primary responsibility | Review lens / contribution |
|---|---|---|
| Baseline Drafting Agent | Produce the first promotion recommendation or job description from legacy guidance. | Creates the realistic starting point where hidden assumptions may appear without explicit intent. |
| Company Culture Reviewer | Assess whether the draft reinforces healthy team culture. | Flags hero culture, blame orientation, excessive individualism, vague values, weak collaboration, and language that devalues frontline/offshore roles. |
| Inclusion & Bias Reviewer | Detect bias and exclusion risks in wording and criteria. | Flags gendered language, coded leadership stereotypes, availability assumptions, native-speaker assumptions, vague culture-fit language, and unsupported personality judgments. |
| Equity Reviewer | Evaluate uneven impact across groups. | Identifies criteria that may disadvantage remote/offshore workers, caregivers, disabled workers, non-native English speakers, junior staff, and those outside informal networks. |
| Safety Culture Reviewer | Evaluate operational and psychological safety framing. | Flags blame-first language, pressure to continue unsafe work, missing stop-work authority, weak escalation/learning loops, and unsafe incentives. |
| Offshore Reality Reviewer | Ground the text in offshore operational constraints. | Checks for missing treatment of fatigue, shift handovers, permit-to-work, emergencies, connectivity limits, hierarchy, and frontline execution realities. |
| Plain Language Reviewer | Improve accessibility and clarity of communication. | Flags jargon, corporate fluff, long or ambiguous sentences, unexplained acronyms, and unclear actions. |
| Text Improvement Agent | Rewrite the draft using all reviewer findings while preserving business intent. | Converts findings into concrete language and criteria that improve inclusion, equity, safety culture, and clarity. |
| Evaluation Agent | Compare baseline and improved versions using consistent scoring. | Reports before/after performance across inclusion, equity, safety culture, offshore realism, and clarity, including remaining risks. |

## Conceptual interaction flow

1. Baseline Drafting Agent creates the initial text from legacy guidance.
2. Reviewer agents independently inspect the same baseline draft from different lenses.
3. Text Improvement Agent consolidates reviewer findings and rewrites the text.
4. Evaluation Agent compares baseline vs improved text and explains score movement and residual risks.

## Workshop takeaway

Improvement comes from separation of responsibility, explicit review lenses, and revision authority.  
The system works because assumptions are surfaced by structured critique and corrected through deliberate rewriting, not because agents are styled as personas.

