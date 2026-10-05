# Benchmark results

## synthetic

| System | Recall | Precision | F1 | Leak rate (docs) |
|---|---|---|---|---|
| rules | 38.7% | 100.0% | 55.8% | 100.0% |
| apertus | 65.2% | 99.8% | 78.9% | 93.0% |
| schild | 88.1% | 99.8% | 93.6% | 58.7% |

| Type | rules | apertus | schild |
|---|---|---|---|
| ADDRESS | 0.0% | 96.2% | 96.2% |
| AHV | 100.0% | 93.3% | 100.0% |
| CRIMINAL | 0.0% | 85.0% | 85.0% |
| DOB | 100.0% | 52.2% | 100.0% |
| EMAIL | 100.0% | 14.2% | 100.0% |
| ETHNICITY | 0.0% | 50.0% | 50.0% |
| HEALTH | 0.0% | 100.0% | 100.0% |
| IBAN | 100.0% | 43.3% | 100.0% |
| PERSON | 0.0% | 76.3% | 76.3% |
| PHONE | 100.0% | 10.6% | 100.0% |
| RELIGION | 0.0% | 100.0% | 100.0% |
| SOCIAL | 0.0% | 25.0% | 25.0% |

| Language | rules | apertus | schild |
|---|---|---|---|
| de | 38.7% | 67.3% | 90.1% |
| en | 38.7% | 70.1% | 90.1% |
| fr | 38.7% | 63.0% | 89.7% |
| it | 38.7% | 60.4% | 82.6% |

Apertus calls: 300 documents, 0 failures, 22 hallucinated entities, median latency 2.4459999999999997 s, p90 3.084 s.

## hard

| System | Recall | Precision | F1 | Leak rate (docs) |
|---|---|---|---|---|
| rules | 27.3% | 100.0% | 42.9% | 100.0% |
| apertus | 71.2% | 95.0% | 81.4% | 75.0% |
| schild | 90.9% | 95.5% | 93.1% | 30.0% |

| Type | rules | apertus | schild |
|---|---|---|---|
| ADDRESS | 0.0% | 100.0% | 100.0% |
| AHV | 100.0% | 100.0% | 100.0% |
| CRIMINAL | 0.0% | 100.0% | 100.0% |
| DOB | 100.0% | 66.7% | 100.0% |
| EMAIL | 100.0% | 0.0% | 100.0% |
| ETHNICITY | 0.0% | 50.0% | 50.0% |
| HEALTH | 0.0% | 83.3% | 83.3% |
| IBAN | 100.0% | 0.0% | 100.0% |
| PERSON | 0.0% | 100.0% | 100.0% |
| PHONE | 100.0% | 0.0% | 100.0% |
| RELIGION | 0.0% | 50.0% | 50.0% |
| SOCIAL | 0.0% | 50.0% | 50.0% |

| Language | rules | apertus | schild |
|---|---|---|---|
| de | 22.2% | 72.2% | 88.9% |
| en | 26.7% | 66.7% | 86.7% |
| fr | 29.4% | 76.5% | 94.1% |
| it | 31.2% | 68.8% | 93.8% |

Apertus calls: 20 documents, 0 failures, 0 hallucinated entities, median latency 1.7825 s, p90 2.36 s.
