# HalluCover — AI Hallucination Professional Liability Insurance for Legal Practitioners

> **Samsung Fire & Marine Insurance × POSTECH × SNU**  
> 2026 Risk Management Competition — *New Risks in AI Era*

---

## Overview

HalluCover is a first-of-its-kind **B2P (Business-to-Professional) insurance product** designed to cover legal practitioners against liability arising from AI hallucination errors.

As generative AI adoption in legal practice nearly doubled year-over-year to **40%**, and Verisk ISO exclusion endorsements (CG 40 47/48 01 26) took effect in January 2026, a critical coverage gap emerged: **no existing insurance product covers AI hallucination-induced legal liability.**

HalluCover closes that gap.

---

## The Problem

| | Evidence |
|---|---|
| Documented hallucination cases | **1,171 cases** (Charlotin DB, 2026) |
| Fabricated citations — most common type | **54.6%** of cases |
| Cases involving legal professionals | **38.6%** |
| Total monetary sanctions | **$1.35M USD** |
| Largest single penalty | **$282,508 USD** |
| AI hallucination rate in legal research | **17–34%** (Stanford RegLab, 2024) |

Real cases include *Schwartz v. Mata Transport* (2023), *Michael Cohen* (2023), and *Morgan & Morgan* (2025) — all involving AI-fabricated legal citations submitted to courts.

---

## Our Solution — Three-Stage AI Pipeline

```
Applicant → NLP Underwriting → Claims Assessment → ML Renewal
```

### ① NLP Underwriting
Data-driven premium calculation using real penalty rates from Charlotin DB:

```
Base Premium × Job Weight × Task Weight × AI Risk Surcharge × Skill Discount
```

| Factor | Range |
|---|---|
| Job weight (Attorney / Patent / Scrivener) | ×1.10 – ×1.30 |
| Task weight (8 task types) | ×0.50 – ×1.40 |
| AI risk surcharge (L1 / L2 / L3) | +0% / +10% / +20% |
| Skill discount (claim-free years) | 0% – 30% |
| **Annual premium range** | **₩215,200 – ₩555,900** |

**Example:** Attorney · Court brief · L3 · 5yr claim-free → **≈ ₩503,000/year**

### ② Claims Assessment
NLP Diff Engine compares AI output vs. final submitted document to identify the error zone:

| Error Zone | Verdict |
|---|---|
| AI Zone — error in unedited AI output | ✓ Full Coverage |
| Hybrid Zone — error spans AI + human edits | ◑ Partial Coverage |
| Expert Zone — error in human-edited section | ✕ Exclusion |

**Track A** (Chrome Extension, WORM log) → AI audit 48h → Full coverage eligible  
**Track B** (Self-submit, manual log) → Human review 5 days → Partial coverage only

### ③ ML Premium Renewal
Six ML features adjust the renewal multiplier annually:

| Feature | Weight |
|---|---|
| Claim history | 30% |
| Compliance rate | 20% |
| AI model grade (LegalBench) | 15% |
| High-risk task ratio | 15% |
| AI proficiency | 10% |
| Usage frequency | 10% |

**Self-reinforcing cycle:** More data → Better pricing → Lower loss ratio

---

## Repository Structure

```
Samsung-Fire-AI-Professional-Insurance/
│
├── README.md
│
├── data/
│   └── ai_hallucination_legal_cases.csv     # Charlotin DB (n=1,171)
│
├── analysis/
│   ├── weight_analysis.py                   # Task weight derivation from penalty rates
│   ├── damage_analysis.py                   # Monetary sanction quantification
│   └── ai_insurance_app.py                  # Interactive premium simulation (CLI)
│
├── visualization/
│   ├── ai_hallucination_viz.py              # Hallucination case dashboard
│   ├── ai_incidents_viz.py                  # AI incident trend (2012–2024)
│   └── legalbench_viz.py                    # LegalBench error risk by task category
│
└── output/
    ├── ai_hallucination_dashboard.png
    ├── ai_incidents_dashboard.png
    ├── damage_analysis_dashboard.png
    ├── 01_overview_by_category.png
    └── 03_scatter_all_tasks.png
```

---

## Key Scripts

### `weight_analysis.py`
Derives task risk weights from monetary penalty rates in Charlotin DB.  
Outputs normalized weights (0.50–1.40) per document type using a confidence-weighted blend of data-driven and logic-based scores.

```bash
python analysis/weight_analysis.py
```

### `damage_analysis.py`
Quantifies monetary and non-monetary sanctions across 1,171 cases.  
Converts multi-currency penalties to USD (2025 FX rates) and generates the damage dashboard.

```bash
python analysis/damage_analysis.py
```

### `ai_insurance_app.py`
Interactive CLI premium simulation system.  
Three modules: Underwriting → Claims Assessment → ML Renewal.

```bash
python analysis/ai_insurance_app.py
```

---

## Data Sources

| Source | Description |
|---|---|
| **Charlotin DB** | 1,171 AI hallucination legal cases (2023–2026) |
| **Stanford RegLab — Magesh et al. (2024)** | arXiv:2405.20362 · hallucination rate 17–34% |
| **LegalBench** | 161 legal benchmark tasks · error risk by category |
| **Thomson Reuters** | 2026 AI in Professional Services Report |
| **Verisk ISO** | CG 35 08 01 26 · CG 40 47/48 01 26 — Gen AI exclusion endorsements |
| **Geneva Association** | Gen AI Risks for Business (2025) |

---

## Coverage Tiers

| Tier | Coverage Limit (per claim / annual) | Deductible | Target |
|---|---|---|---|
| Basic | ₩50M / ₩50M | ₩10M | Low-risk practitioners (L1·L2) |
| **Standard** *(recommended)* | **₩100M / ₩100M** | **₩5M** | General litigation attorneys |
| Premium | ₩200M / ₩200M | ₩3M | High-risk practitioners (L3) |

---

## Team

**HalluCover** — Samsung Fire & Marine Insurance × POSTECH × SNU  
2026 Risk Management Competition · *New Risks in AI Era*

> *AI는 이미 법률 리스크를 만들었다. 보험만이 아직 존재하지 않는다.*  
> *AI has already created legal risk. Only insurance has yet to exist.*
