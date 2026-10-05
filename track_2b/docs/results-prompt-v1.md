# Benchmark results

## synthetic

| System | Recall | Precision | F1 | Leak rate (docs) |
|---|---|---|---|---|
| rules | 38.7% | 100.0% | 55.8% | 100.0% |
| apertus | 51.3% | 100.0% | 67.8% | 98.7% |
| schild | 75.5% | 100.0% | 86.0% | 82.0% |

| Type | rules | apertus | schild |
|---|---|---|---|
| ADDRESS | 0.0% | 88.8% | 88.8% |
| AHV | 100.0% | 99.2% | 100.0% |
| CRIMINAL | 0.0% | 1.7% | 1.7% |
| DOB | 100.0% | 36.7% | 100.0% |
| EMAIL | 100.0% | 7.5% | 100.0% |
| ETHNICITY | 0.0% | 28.3% | 28.3% |
| HEALTH | 0.0% | 90.8% | 90.8% |
| IBAN | 100.0% | 50.8% | 100.0% |
| PERSON | 0.0% | 52.4% | 52.4% |
| PHONE | 100.0% | 8.3% | 100.0% |
| RELIGION | 0.0% | 100.0% | 100.0% |
| SOCIAL | 0.0% | 1.7% | 1.7% |

| Language | rules | apertus | schild |
|---|---|---|---|
| de | 38.7% | 54.2% | 79.6% |
| en | 38.7% | 41.9% | 69.9% |
| fr | 38.7% | 54.8% | 75.3% |
| it | 38.7% | 54.2% | 77.2% |

Apertus calls: 300 documents, 0 failures, 10 hallucinated entities, median latency 0.7995000000000001 s, p90 1.076 s.

## hard

| System | Recall | Precision | F1 | Leak rate (docs) |
|---|---|---|---|---|
| rules | 27.3% | 100.0% | 42.9% | 100.0% |
| apertus | 48.5% | 100.0% | 65.3% | 100.0% |
| schild | 71.2% | 100.0% | 83.2% | 70.0% |

| Type | rules | apertus | schild |
|---|---|---|---|
| ADDRESS | 0.0% | 75.0% | 75.0% |
| AHV | 100.0% | 66.7% | 100.0% |
| CRIMINAL | 0.0% | 25.0% | 25.0% |
| DOB | 100.0% | 0.0% | 100.0% |
| EMAIL | 100.0% | 0.0% | 100.0% |
| ETHNICITY | 0.0% | 0.0% | 0.0% |
| HEALTH | 0.0% | 33.3% | 33.3% |
| IBAN | 100.0% | 25.0% | 100.0% |
| PERSON | 0.0% | 87.5% | 87.5% |
| PHONE | 100.0% | 0.0% | 100.0% |
| RELIGION | 0.0% | 25.0% | 25.0% |
| SOCIAL | 0.0% | 25.0% | 25.0% |

| Language | rules | apertus | schild |
|---|---|---|---|
| de | 22.2% | 44.4% | 66.7% |
| en | 26.7% | 33.3% | 60.0% |
| fr | 29.4% | 58.8% | 76.5% |
| it | 31.2% | 56.2% | 81.2% |

Apertus calls: 20 documents, 0 failures, 0 hallucinated entities, median latency 0.518 s, p90 0.616 s.
