# Benchmark results

## synthetic

| System | Recall | Precision | F1 | Leak rate (docs) |
|---|---|---|---|---|
| rules | 38.7% | 100.0% | 55.8% | 100.0% |
| apertus | 58.8% | 99.9% | 74.0% | 96.7% |
| schild | 83.2% | 99.9% | 90.8% | 66.0% |

| Type | rules | apertus | schild |
|---|---|---|---|
| ADDRESS | 0.0% | 95.8% | 95.8% |
| AHV | 100.0% | 93.3% | 100.0% |
| CRIMINAL | 0.0% | 30.0% | 30.0% |
| DOB | 100.0% | 37.2% | 100.0% |
| EMAIL | 100.0% | 13.3% | 100.0% |
| ETHNICITY | 0.0% | 3.3% | 3.3% |
| HEALTH | 0.0% | 90.8% | 90.8% |
| IBAN | 100.0% | 43.3% | 100.0% |
| PERSON | 0.0% | 76.3% | 76.3% |
| PHONE | 100.0% | 10.0% | 100.0% |
| RELIGION | 0.0% | 95.0% | 95.0% |
| SOCIAL | 0.0% | 0.0% | 0.0% |

| Language | rules | apertus | schild |
|---|---|---|---|
| de | 38.7% | 61.3% | 84.5% |
| en | 38.7% | 60.4% | 83.0% |
| fr | 38.7% | 55.7% | 83.4% |
| it | 38.7% | 57.6% | 81.9% |

Apertus calls: 300 documents, 0 failures, 8 hallucinated entities, median latency 1.736 s, p90 2.443 s.

## hard

| System | Recall | Precision | F1 | Leak rate (docs) |
|---|---|---|---|---|
| rules | 27.3% | 100.0% | 42.9% | 100.0% |
| apertus | 56.1% | 100.0% | 71.8% | 95.0% |
| schild | 75.8% | 100.0% | 86.2% | 70.0% |

| Type | rules | apertus | schild |
|---|---|---|---|
| ADDRESS | 0.0% | 100.0% | 100.0% |
| AHV | 100.0% | 100.0% | 100.0% |
| CRIMINAL | 0.0% | 25.0% | 25.0% |
| DOB | 100.0% | 66.7% | 100.0% |
| EMAIL | 100.0% | 0.0% | 100.0% |
| ETHNICITY | 0.0% | 0.0% | 0.0% |
| HEALTH | 0.0% | 33.3% | 33.3% |
| IBAN | 100.0% | 0.0% | 100.0% |
| PERSON | 0.0% | 100.0% | 100.0% |
| PHONE | 100.0% | 0.0% | 100.0% |
| RELIGION | 0.0% | 0.0% | 0.0% |
| SOCIAL | 0.0% | 25.0% | 25.0% |

| Language | rules | apertus | schild |
|---|---|---|---|
| de | 22.2% | 61.1% | 77.8% |
| en | 26.7% | 53.3% | 73.3% |
| fr | 29.4% | 58.8% | 76.5% |
| it | 31.2% | 50.0% | 75.0% |

Apertus calls: 20 documents, 0 failures, 0 hallucinated entities, median latency 0.906 s, p90 1.083 s.
