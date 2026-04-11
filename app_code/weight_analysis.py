"""
AI 전문직 배상책임보험 — 업무 위험 가중치 산출
출처:
  1. Charlotin DB (n=1,171건) — 문서 유형별 금전제재율 기반
  2. Stanford RegLab, Magesh et al. (2024), arXiv:2405.20362 — 논리 근거 보완
  3. 대한변호사협회 (2025) — 직군 가중치 보완
"""

import pandas as pd

# ── 설정 ──────────────────────────────────────────────────────
import os
CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/ai 할루시네이션 법률 판례 전용 db.csv")
W_MIN, W_MAX = 0.5, 1.4   # 가중치 범위
THRESHOLD    = 50          # 신뢰도 기준 표본 수

# ── 데이터 로드 ───────────────────────────────────────────────
df        = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
lawyer_df = df[df["Party(ies)"].str.contains("Lawyer", na=False)].copy()
prose_df  = df[df["Party(ies)"].str.contains("Pro Se", na=False)].copy()

# ── 문서 유형 키워드 분류 ─────────────────────────────────────
DOC_CATEGORIES = {
    "소장·준비서면": ["brief", "complaint", "motion", "pleading", "memorandum", "filing"],
    "법률의견서":    ["opinion letter", "legal opinion", "opinion"],
    "계약서":        ["contract", "agreement", "clause"],
    "판례·리서치":   ["research", "cited case", "case law", "citation"],
    "증거·제출서류": ["exhibit", "submission", "evidence"],
}

# ── 문서 유형별 금전제재율 산출 ──────────────────────────────
base      = lawyer_df[lawyer_df["Hallucination Items"].notna()]
doc_stats = {}

for cat, kws in DOC_CATEGORIES.items():
    matched = base[base["Hallucination Items"].apply(
        lambda x: any(kw.lower() in x.lower() for kw in kws)
    )]
    n   = len(matched)
    mon = len(matched[matched["Monetary Penalty"].notna() & (matched["Monetary Penalty"] != "")])
    doc_stats[cat] = {"n": n, "mon_rate": mon / n * 100 if n else 0}

# ── 정규화 (금전제재율 → 가중치 범위 변환) ───────────────────
rates        = {c: v["mon_rate"] for c, v in doc_stats.items()}
min_r, max_r = min(rates.values()), max(rates.values())

def normalize(r):
    return round(W_MIN + (r - min_r) / (max_r - min_r) * (W_MAX - W_MIN), 2)

data_w = {c: normalize(r) for c, r in rates.items()}

# ── 논리 기반 가중치 (외부 제출 여부 + 전문직 검토 개입도) ──
# 근거: Stanford RegLab (2024) — 법률 리서치 할루시네이션율 17~34%
logic_w = {
    "소장·준비서면": 1.40,
    "법률의견서":    1.30,
    "계약서":        1.10,
    "판례·리서치":   0.80,
    "증거·제출서류": 1.20,
}

# ── 신뢰도 보정 가중 평균 ─────────────────────────────────────
# n >= 50: 데이터 70% + 논리 30%
# n <  50: 데이터 30% + 논리 70% (소표본 보정)
final_cat_w = {}
for cat in DOC_CATEGORIES:
    n     = doc_stats[cat]["n"]
    alpha = 0.7 if n >= THRESHOLD else 0.3
    final_cat_w[cat] = round(alpha * data_w[cat] + (1 - alpha) * logic_w[cat], 2)

# ── 업무별 가중치 매핑 ────────────────────────────────────────
TASK_MAP = {
    "판례·법령 검색 후 소장·준비서면에 직접 인용": "소장·준비서면",
    "법률의견서 작성":                              "법률의견서",
    "계약서 조항 작성":                             "계약서",
    "계약서 검토 및 리스크 포인트 추출":            "계약서",
    "판례·판결문 요약 및 리서치":                   "판례·리서치",
    "문서 초안 작성 (전면 재검토 전제)":            "판례·리서치",
    "의뢰인 상담 내용 정리":                        None,
    "자료 정리·번역·기일 관리":                     None,
}
FIXED = {"의뢰인 상담 내용 정리": 0.60, "자료 정리·번역·기일 관리": 0.50}

task_final = {
    task: (FIXED[task] if cat is None else final_cat_w[cat])
    for task, cat in TASK_MAP.items()
}

# ── 결과 출력 ─────────────────────────────────────────────────
print("=" * 60)
print("문서 유형별 제재율 분석 (Charlotin DB, Lawyer n=446)")
print("=" * 60)
for cat, v in doc_stats.items():
    trust = "신뢰" if v["n"] >= THRESHOLD else "소표본"
    print(f"  {cat:<16} n={v['n']:>4}건 [{trust}]  금전제재율 {v['mon_rate']:5.1f}%  → 데이터 가중치 {data_w[cat]}")

print()
print("=" * 60)
print("최종 가중치 (신뢰도 보정 적용)")
print("=" * 60)
print("\n[직군 가중치]")
print("  변호사 1.30  — 금전제재율 30.3%, 징계율 20.4% (Charlotin DB n=446)")
print("  변리사 1.20  — 특허 청구범위 오류 시 권리 범위 변동")
print("  법무사 1.10  — 등기·서류 중심, 법원 직접 제출 빈도 낮음")
print("  기타   1.00  — 기준값")

print("\n[업무 위험 가중치]")
for task, w in task_final.items():
    cat = TASK_MAP[task]
    if cat is None:
        note = "비법률 업무 고정값"
    else:
        n     = doc_stats[cat]["n"]
        alpha = 0.7 if n >= THRESHOLD else 0.3
        note  = f"{cat} | 제재율 {doc_stats[cat]['mon_rate']:.1f}% | n={n} | 데이터{int(alpha*100)}%+논리{int((1-alpha)*100)}%"
    print(f"  {w}  {task:<42} ({note})")