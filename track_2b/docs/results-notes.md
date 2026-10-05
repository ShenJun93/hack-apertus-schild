# Notes on the benchmark runs (2026-10-05/06)

All runs: CSCS endpoint `https://api.inference.cscs.ch/v1`, temperature 0, JSON mode accepted,
0 request failures. Model outputs for every run are cached in `data/llm_outputs.jsonl`, keyed by
model and prompt hash, so every table can be recomputed without calling the model.

| Run | Prompt | Model | Synthetic: Schild recall / leak rate | Hard set: Schild recall / leak rate | Tables |
|---|---|---|---|---|---|
| A | v1 `103d8bda`, one pass | Apertus-v1.5-8B | 75.5% / 82.0% | 71.2% / 70.0% | `results-prompt-v1.md` |
| B | v2 (`prompt-v2.diff`), one pass | Apertus-v1.5-8B | 76.8% / 79.0% | 65.2% / 80.0% | `results-prompt-v2.md` |
| C | v1, one pass | Apertus-v1.5-70B | 83.2% / 66.0% | 75.8% / 70.0% | `results-70b.md` |
| **D (default)** | v1 + sensitive pass | Apertus-v1.5-8B | **78.5% / 81.3%** | **81.8% / 50.0%** | `results.md` (= `results-two-pass.md`) |
| E | v1 + sensitive pass | Apertus-v1.5-70B | 88.1% / 58.7% | 90.9% / 30.0% | `results-70b-two-pass.md` |

Median latency per document on CSCS: A 0.8 s, D 1.3 s, C 1.7 s, E 2.4 s.

## The second pass (runs D and E) is the default

After prompt v2 failed (below), a second, narrow prompt that asks only for the nDSG Art. 5 lit. c
categories was added as a separate call. The rule decided in advance: keep it only if the hard
set (no prompt was written against it) improves. It did, by 10.6 points (71.2% → 81.8%; 7 of 66 entities, intervals overlap), with documents still
leaking falling from 70% to 50%. On the synthetic set CRIMINAL rose from 1.7% to 65.0% and HEALTH
from 90.8% to 100%. Against 70B with one pass the evidence is mixed: level on the hard set (81.8% vs
75.8%, intervals overlap) but clearly behind on the synthetic set (78.5% vs 83.2% recall, 81.3% vs
66.0% leak rate), at about the same latency (synthetic 1.3 s vs 1.7 s, hard 1.0 s vs 0.9 s). Still
weak: SOCIAL (5.0% synthetic) and PERSON (52.2%; see below).

Rules alone protect 38.7% (synthetic) and 27.3% (hard) of entities and leave something in every
document.

## Does Schild beat both single systems?

Yes, in every run and on both sets: rules and Apertus fail on different entity types, so their
union is much stronger than either (run D, synthetic: 38.7% and 57.7% → 78.5%). Precision is
99.8–100% in every run except E on the hard set (95.5%, one span outside the labels): the model
almost never marks text that is not personal data.

## Where it leaked before the second pass (run A, synthetic set)

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
and **lost 6 points on the hard set**, against which no prompt was written: HEALTH fell from 90.8% to
76.7% and ADDRESS from 88.8% to 78.3% on the synthetic set, and CRIMINAL stayed at 1.7%. The longer
prompt seems to dilute an 8B model's attention. Prompt v1 is kept.

## Model size (run C)

Apertus 70B with the same prompt raises Schild's recall by 7.7 points on the synthetic set and 4.6
on the hard set, at about twice the median latency (1.7 s vs 0.8 s per document on CSCS). It still
misses social benefits (0%) and ethnic origin (3.3%).

## Hallucinations

Per run, 8–22 strings on the synthetic set (A 10, B 9, C 8, D 15, E 22) and 0–1 on the hard set
were returned by the model but not found in the text. They are dropped. Whether some are
near-misses of real entities (whitespace or Unicode variants) was not checked.

## Role of the hard set

No prompt was written against the hard set, but it decided two choices: rejecting v2 and keeping
the second prompt. It is a validation set, not an untouched test set, and the default's score on
it is the best of three 8B configurations. 95% Wilson intervals for Schild recall on it: A 59–81%,
B 53–76%, C 64–84%, D 71–89%, E 82–96%.

## Names that leak (run D, synthetic set)

258 of 540 PERSON occurrences leak: 119 of 120 second persons (signing doctor, interviewer), the
writer's own name in 86 of 120 occurrences in bank emails (43 of 60 documents) and 46 of 120 in
insurance emails (23 of 60), and 7 elsewhere.

## Propagation

Since commit "Redact every occurrence of a value once it is known", Schild also redacts every
other occurrence of a found value, ignoring case and spacing. All tables were recomputed with it;
no number changed, because the templates repeat values in exactly the same spelling.

## Local CPU latency (air-gapped setup)

See `local-model.md`: 60 s for one sentence with one prompt on 12 CPU threads, CPU only. The
default sends two prompts. The local quantised model was not benchmarked.
