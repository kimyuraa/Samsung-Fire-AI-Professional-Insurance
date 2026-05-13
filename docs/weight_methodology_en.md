# Premium Weight Derivation Methodology

---

## 1. Job Weight

### Data Source

Charlotin AI Hallucination Case DB (n=1,171) — monetary sanction rate by party type

| Party Type | Cases | Monetary Sanction Rate | Disciplinary Rate |
|---|---|---|---|
| Attorney (Lawyer) | 446 | 30.3% | 20.4% |
| Pro Se (Non-professional) | 696 | 8.5% | 0.3% |

Attorney monetary sanction rate (30.3%) is 3.6x higher than Pro Se (8.5%) → basis for attorney job weight of 1.30

### Final Job Weights

| Job Type | Weight | Rationale |
|---|---|---|
| Attorney | 1.30 | 30.3% monetary sanction rate / direct court filing, AI errors directly affect case outcomes |
| Patent Attorney | 1.20 | Patent claim errors alter rights scope; post-correction process is complex and irreversible |
| Legal Scrivener | 1.10 | Registration & document-centric; lower frequency of direct court submissions |
| Other | 1.00 | Baseline |

---

## 2. Task Risk Weight

### Methodology

Two evidence sources combined via reliability-adjusted weighted average:

- **Data-driven**: Charlotin DB Hallucination Items keyword classification → monetary sanction rate by document type → normalized to 0.50–1.40 range
- **Logic-driven**: External submission likelihood + degree of professional review (Stanford RegLab, Magesh et al., 2024)
- **Reliability correction**: n≥50 → 70% data + 30% logic / n<50 → 30% data + 70% logic

> **Limitation**: Charlotin DB lacks a task-type column; keyword-based classification used as approximation. Acknowledged in literature as an "unexplored benchmark challenge" (Magesh et al., 2024).

### Document Type Analysis Results

| Document Type | n | Reliability | Sanction Rate | Data Weight |
|---|---|---|---|---|
| Legal Opinion | 92 | ✅ Reliable | 44.6% | 1.40 |
| Court Brief / Motion | 184 | ✅ Reliable | 38.0% | 1.13 |
| Evidence / Submission | 74 | ✅ Reliable | 37.8% | 1.12 |
| Case Research | 412 | ✅ Reliable | 30.6% | 0.81 |
| Contract | 13 | ⚠️ Small Sample | 23.1% | 0.50 |

### Final Task Risk Weights

| Task | Weight | Derivation |
|---|---|---|
| Legal opinion drafting | **1.37** | Sanction rate 44.6% (n=92) × 70% + Logic 1.30 × 30% |
| Court brief with case citations | **1.21** | Sanction rate 38.0% (n=184) × 70% + Logic 1.40 × 30% |
| Contract clause drafting | **0.92** | Sanction rate 23.1% (n=13, small) × 30% + Logic 1.10 × 70% |
| Contract review & risk extraction | **0.92** | Same category as contract drafting |
| Case law research & summarization | **0.81** | Sanction rate 30.6% (n=412) × 70% + Logic 0.80 × 30% |
| Document drafting (full review assumed) | **0.81** | Same category as case research |
| Client consultation notes | **0.60** | Fixed — no external submission, indirect harm only |
| Admin / translation / scheduling | **0.50** | Fixed — non-legal task, negligible error impact |

---

## 3. Task Weight Aggregation Formula (Anti-Adverse-Selection Design)

### Formula

```
Final Task Weight = max(selected task weights)
                 + 0.10 × (no. of high-risk tasks − 1)
                 + 0.02 × (no. of low-risk tasks)
```

| Category | Criterion | Add-on |
|---|---|---|
| High-risk task | Weight ≥ 1.0 | +0.10 × (count − 1) |
| Low-risk task | Weight < 1.0 | +0.02 × count |

### Design Rationale

- **Adverse selection prevention**: Adding low-risk tasks does NOT reduce the premium — each adds +0.02
- **High-risk concentration**: More high-risk tasks = proportionally higher premium
- **Primary task anchoring**: The riskiest task (max) sets the baseline, preserving task profile integrity

### Scenario Examples

| Scenario | Calculation | Final Weight |
|---|---|---|
| Legal opinion only (1 task) | max(1.37) + 0 + 0 | 1.37 |
| 2 high-risk tasks (opinion + brief) | max(1.37) + 0.10×1 + 0 | 1.47 |
| Adverse selection attempt: 1 high + 7 low | max(1.37) + 0 + 0.02×7 | 1.51 (increases) |
| 3 low-risk tasks only | max(0.92) + 0 + 0.02×3 | 0.98 |

---

## 4. References

1. **Charlotin DB** — Charlotin, D. (2026). AI Hallucination Cases Database. Project data (`data/ai hallucination legal case db.csv`, n=1,171)
2. **Stanford RegLab** — Magesh, V. et al. (2024). Hallucination-Free? Assessing the Reliability of Leading AI Legal Research Tools. https://arxiv.org/abs/2405.20362
3. **Korean Bar Association** (2025). 2025 Attorney Professional Liability Insurance Renewal Guide. https://www.koreanbar.or.kr
