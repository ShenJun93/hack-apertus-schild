# Notes on the benchmark runs (2026-10-05/06)

All runs: CSCS endpoint `https://api.inference.cscs.ch/v1`, temperature 0, JSON mode accepted,
0 request failures. Model outputs for every run are cached in `data/llm_outputs.jsonl`, keyed by
model and prompt hash, so every table can be recomputed without calling the model.

| Run | Prompt | Model | Synthetic: Schild recall / leak rate | Hard set: Schild recall / leak rate | Tables |
|---|---|---|---|---|---|
| A (main) | v1 `103d8bda` | Apertus-v1.5-8B | 75.5% / 82.0% | 71.2% / 70.0% | `results.md` (= `results-prompt-v1.md`) |
| B | v2 (`prompt-v2.diff`) | Apertus-v1.5-8B | 76.8% / 79.0% | 65.2% / 80.0% | `results-prompt-v2.md` |
| C | v1 `103d8bda` | Apertus-v1.5-70B | 83.2% / 66.0% | 75.8% / 70.0% | `results-70b.md` |

Rules alone protect 38.7% (synthetic) and 27.3% (hard) of entities and leave something in every
document.

## Does Schild beat both single systems?

Yes, in every run and on both sets: rules and Apertus fail on different entity types, so their
union is much stronger than either (run A, synthetic: 38.7% and 51.3% → 75.5%). Precision stays at
99.9–100%: the model almost never marks text that is not personal data.

## Where it leaks (run A, synthetic set)

- **Second person in a document** (author, doctor, interviewer): PERSON recall is 52.4%. In
  `de-hr-000` Apertus returned the employee and the address but not the interviewer
  ("Gesprächsführung: Ladina Schäfer").
- **Offences and social benefits**: CRIMINAL 1.7%, SOCIAL 1.7%. In `de-hr-000` the phrase
  "Strafverfahren wegen Körperverletzung" produced no entity; benefits such as
  "Ergänzungsleistungen" or "Prämienverbilligung" are not seen as personal data.
- **Split addresses**: in `fr-hr-001` the model returned "boulevard Camille Badan 37" and
  "Broquet-la-Ville" separately; the postcode between them leaked.

## Prompt tuning did not generalise (run B)

Prompt v2 added explicit guidance for exactly those failures, with examples deliberately different
from the benchmark's word lists. It gained 1.3 points on the synthetic set it was written against
and **lost 6 points on the hard set**, which was never used for tuning: HEALTH fell from 90.8% to
76.7% and ADDRESS from 88.8% to 78.3% on the synthetic set, and CRIMINAL stayed at 1.7%. The longer
prompt seems to dilute an 8B model's attention. Prompt v1 is kept.

## Model size (run C)

Apertus 70B with the same prompt raises Schild's recall by 7.7 points on the synthetic set and 4.6
on the hard set, at about twice the median latency (1.7 s vs 0.8 s per document on CSCS). It still
misses social benefits (0%) and ethnic origin (3.3%).

## Hallucinations

8–10 entities per 300 documents were reported by the model but not found in the text; they are
dropped and do not affect redaction. None on the hard set.

## Local CPU latency (air-gapped setup)

See `local-model.md`: about 60 s for one sentence on 12 CPU threads, CPU only.
