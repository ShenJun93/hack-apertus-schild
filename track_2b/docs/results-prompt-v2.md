# Benchmark results

## synthetic

| System | Recall | Precision | F1 | Leak rate (docs) |
|---|---|---|---|---|
| rules | 38.7% | 100.0% | 55.8% | 100.0% |
| apertus | 53.4% | 99.9% | 69.6% | 99.3% |
| schild | 76.8% | 99.9% | 86.8% | 79.0% |

| Type | rules | apertus | schild |
|---|---|---|---|
| ADDRESS | 0.0% | 78.3% | 78.3% |
| AHV | 100.0% | 99.2% | 100.0% |
| CRIMINAL | 0.0% | 1.7% | 1.7% |
| DOB | 100.0% | 35.6% | 100.0% |
| EMAIL | 100.0% | 28.3% | 100.0% |
| ETHNICITY | 0.0% | 31.7% | 31.7% |
| HEALTH | 0.0% | 76.7% | 76.7% |
| IBAN | 100.0% | 45.8% | 100.0% |
| PERSON | 0.0% | 64.3% | 64.3% |
| PHONE | 100.0% | 7.8% | 100.0% |
| RELIGION | 0.0% | 95.0% | 95.0% |
| SOCIAL | 0.0% | 6.7% | 6.7% |

| Language | rules | apertus | schild |
|---|---|---|---|
| de | 38.7% | 56.3% | 80.9% |
| en | 38.7% | 48.2% | 72.9% |
| fr | 38.7% | 55.5% | 75.7% |
| it | 38.7% | 53.8% | 77.6% |

Apertus calls: 300 documents, 0 failures, 9 hallucinated entities, median latency 0.7264999999999999 s, p90 1.049 s.

## hard

| System | Recall | Precision | F1 | Leak rate (docs) |
|---|---|---|---|---|
| rules | 27.3% | 100.0% | 42.9% | 100.0% |
| apertus | 43.9% | 100.0% | 61.1% | 100.0% |
| schild | 65.2% | 100.0% | 78.9% | 80.0% |

| Type | rules | apertus | schild |
|---|---|---|---|
| ADDRESS | 0.0% | 50.0% | 50.0% |
| AHV | 100.0% | 66.7% | 100.0% |
| CRIMINAL | 0.0% | 0.0% | 0.0% |
| DOB | 100.0% | 33.3% | 100.0% |
| EMAIL | 100.0% | 25.0% | 100.0% |
| ETHNICITY | 0.0% | 50.0% | 50.0% |
| HEALTH | 0.0% | 16.7% | 16.7% |
| IBAN | 100.0% | 0.0% | 100.0% |
| PERSON | 0.0% | 83.3% | 83.3% |
| PHONE | 100.0% | 0.0% | 100.0% |
| RELIGION | 0.0% | 0.0% | 0.0% |
| SOCIAL | 0.0% | 25.0% | 25.0% |

| Language | rules | apertus | schild |
|---|---|---|---|
| de | 22.2% | 44.4% | 66.7% |
| en | 26.7% | 40.0% | 60.0% |
| fr | 29.4% | 47.1% | 64.7% |
| it | 31.2% | 43.8% | 68.8% |

Apertus calls: 20 documents, 0 failures, 0 hallucinated entities, median latency 0.498 s, p90 0.571 s.
