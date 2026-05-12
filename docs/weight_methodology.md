# Task Risk Weight Methodology

> This document explains how task risk weights used in HalluCover's NLP underwriting engine were derived from real hallucination case data.

---

## Overview

Task weights (range: **0.50 – 1.40**) reflect the relative risk of AI hallucination errors per legal task type. A higher weight means a greater likelihood of monetary sanction when an AI error occurs in that task.

**Weight formula:**

```
Final Weight = α × Data Weight + (1 - α) × Logic Weight
```

Where **α** is determined by sample size:
- n ≥ 50 cases → α = 0.70 (data-driven 70% + logic 30%)
- n < 50 cases → α = 0.30 (data-driven 30% + logic 70%)

---

## Step 1 — Data Source

**Charlotin DB** (n = 1,171 hallucination cases, 2023–2026)

- Filtered to cases involving **lawyers / legal professionals** (n = 446)
- Each case tagged with: document type, outcome, monetary penalty (if any)

---

## Step 2 — Monetary Penalty Rate per Task

For each document category, we calculated:

```
Penalty Rate = (cases with monetary sanction) / (total cases in category) × 100
```

| Task Category | n (cases) | Monetary Penalty Rate | Confidence |
|---|---|---|---|
| 소장·준비서면 (Court brief) | ≥ 50 | ~30% | High ✅ |
| 법률의견서 (Legal opinion) | ≥ 50 | ~35% | High ✅ |
| 계약서 (Contract) | ≥ 50 | ~20% | High ✅ |
| 판례·리서치 (Case research) | < 50 | ~15% | Low ⚠️ |
| 증거·제출서류 (Evidence) | < 50 | ~25% | Low ⚠️ |

---

## Step 3 — Normalize to Weight Range

Penalty rates are normalized to the **0.50 – 1.40** weight range:

```
Data Weight = W_MIN + (rate - min_rate) / (max_rate - min_rate) × (W_MAX - W_MIN)

W_MIN = 0.50, W_MAX = 1.40
```

---

## Step 4 — Logic-Based Weight (Supplementary)

Grounded in **Stanford RegLab (Magesh et al., 2024)** — hallucination rate 17–34% in legal research tasks.

Logic weights reflect:
- Whether the document is submitted externally to court
- Degree of professional review before submission

| Task Category | Logic Weight | Rationale |
|---|---|---|
| Court brief · citation | 1.40 | Directly filed with court, no second check |
| Legal opinion letter | 1.30 | Client-facing, professional credibility at stake |
| Evidence submission | 1.20 | Court filing, factual accuracy critical |
| Contract drafting | 1.10 | External delivery, legal binding |
| Case research | 0.80 | Internal use, typically reviewed before use |
| Admin / scheduling | 0.50 | Non-legal, minimal liability exposure |

---

## Step 5 — Final Weights (Confidence-Adjusted Blend)

| Task | Final Weight | Data % | Logic % | n |
|---|---|---|---|---|
| Legal opinion letter | **1.37** | 70% | 30% | ≥ 50 |
| Court brief · citation | **1.21** | 70% | 30% | ≥ 50 |
| Evidence submission | **1.20** | 30% | 70% | < 50 |
| Contract drafting | **0.92** | 70% | 30% | ≥ 50 |
| Case research | **0.81** | 30% | 70% | < 50 |
| Admin / scheduling | **0.50** | Fixed | — | — |
| Client consultation | **0.60** | Fixed | — | — |

---

## Job Type Weights

Derived from Charlotin DB disciplinary and monetary sanction rates by party type:

| Job Type | Weight | Basis |
|---|---|---|
| Attorney (변호사) | **×1.30** | Monetary penalty rate 30.3%, disciplinary rate 20.4% |
| Patent attorney (변리사) | **×1.20** | Patent claim errors → rights scope impact |
| Legal scrivener (법무사) | **×1.10** | Registry/document focus, lower court filing frequency |
| Other | **×1.00** | Baseline |

---

## References

| Source | Detail |
|---|---|
| Charlotin DB | 1,171 AI hallucination legal cases (2023–2026) |
| Stanford RegLab — Magesh et al. (2024) | arXiv:2405.20362 · hallucination rate 17–34% in legal research |
| 대한변호사협회 (2025) | Job type weight supplementary basis |

---

## Code

Weights are computed programmatically in:

```
analysis/weight_analysis.py
```

Run to reproduce all weights:

```bash
python analysis/weight_analysis.py
```
