# Benchmark results

## synthetic

| System | Recall | Precision | F1 | Leak rate (docs) |
|---|---|---|---|---|
| rules | 38.7% | 100.0% | 55.8% | 100.0% |
| apertus | 57.7% | 99.9% | 73.2% | 96.3% |
| schild | 78.5% | 99.9% | 88.0% | 81.3% |

| Type | rules | apertus | schild |
|---|---|---|---|
| ADDRESS | 0.0% | 90.0% | 90.0% |
| AHV | 100.0% | 99.2% | 100.0% |
| CRIMINAL | 0.0% | 65.0% | 65.0% |
| DOB | 100.0% | 58.3% | 100.0% |
| EMAIL | 100.0% | 15.8% | 100.0% |
| ETHNICITY | 0.0% | 35.0% | 35.0% |
| HEALTH | 0.0% | 100.0% | 100.0% |
| IBAN | 100.0% | 55.0% | 100.0% |
| PERSON | 0.0% | 52.2% | 52.2% |
| PHONE | 100.0% | 13.3% | 100.0% |
| RELIGION | 0.0% | 100.0% | 100.0% |
| SOCIAL | 0.0% | 5.0% | 5.0% |

| Language | rules | apertus | schild |
|---|---|---|---|
| de | 38.7% | 59.1% | 80.9% |
| en | 38.7% | 50.5% | 75.1% |
| fr | 38.7% | 59.8% | 77.8% |
| it | 38.7% | 61.5% | 80.4% |

Apertus calls: 300 documents, 0 failures, 15 hallucinated entities, median latency 1.339 s, p90 1.767 s.

## hard

| System | Recall | Precision | F1 | Leak rate (docs) |
|---|---|---|---|---|
| rules | 27.3% | 100.0% | 42.9% | 100.0% |
| apertus | 63.6% | 100.0% | 77.8% | 80.0% |
| schild | 81.8% | 100.0% | 90.0% | 50.0% |

| Type | rules | apertus | schild |
|---|---|---|---|
| ADDRESS | 0.0% | 50.0% | 50.0% |
| AHV | 100.0% | 66.7% | 100.0% |
| CRIMINAL | 0.0% | 75.0% | 75.0% |
| DOB | 100.0% | 66.7% | 100.0% |
| EMAIL | 100.0% | 0.0% | 100.0% |
| ETHNICITY | 0.0% | 50.0% | 50.0% |
| HEALTH | 0.0% | 83.3% | 83.3% |
| IBAN | 100.0% | 25.0% | 100.0% |
| PERSON | 0.0% | 87.5% | 87.5% |
| PHONE | 100.0% | 25.0% | 100.0% |
| RELIGION | 0.0% | 50.0% | 50.0% |
| SOCIAL | 0.0% | 50.0% | 50.0% |

| Language | rules | apertus | schild |
|---|---|---|---|
| de | 22.2% | 50.0% | 72.2% |
| en | 26.7% | 53.3% | 73.3% |
| fr | 29.4% | 76.5% | 88.2% |
| it | 31.2% | 75.0% | 93.8% |

Apertus calls: 20 documents, 0 failures, 1 hallucinated entities, median latency 0.976 s, p90 1.048 s.
