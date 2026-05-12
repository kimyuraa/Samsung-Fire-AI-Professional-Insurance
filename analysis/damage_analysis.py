"""
AI 할루시네이션 법률 판례 - 피해 규모 정량화 분석
사용법: python damage_analysis.py
필요 패키지: pandas, matplotlib
설치: pip install pandas matplotlib
"""
import os, sys, pathlib, re, warnings
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

warnings.filterwarnings("ignore")

# ── 0. 폰트 설정
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.unicode_minus"] = False

PALETTE = {
    "blue":   "#5B8DEF",
    "green":  "#2ECC71",
    "orange": "#F39C12",
    "red":    "#E74C3C",
    "purple": "#9B59B6",
    "teal":   "#1ABC9C",
    "gray":   "#95A5A6",
}

plt.rcParams.update({
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.grid":         True,
    "grid.alpha":        0.25,
    "figure.dpi":        130,
})

# ── 1. 경로 설정
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
DATA_DIR   = SCRIPT_DIR.parent / "data"
OUTPUT_DIR = SCRIPT_DIR.parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# CSV 자동 탐색 → data/ 폴더에서 찾음
csv_path = next(
    (f for f in DATA_DIR.iterdir()
     if f.suffix.lower() == ".csv" and ("hallucination" in f.name.lower() or "할루" in f.name)),
    None
)
if csv_path is None:
    print(f"CSV 파일을 찾을 수 없습니다.\nData folder: {DATA_DIR}")
    sys.exit(1)

# ── 2. 데이터 로딩
df = None
for enc in ("utf-8-sig", "utf-8", "cp949"):
    try:
        df = pd.read_csv(csv_path, encoding=enc)
        print(f"로딩 완료 ({enc}): {len(df):,}건")
        break
    except Exception:
        continue
if df is None:
    print("CSV 파일을 열 수 없습니다.")
    sys.exit(1)

df["Date"] = pd.to_datetime(df["Date"])

# ── 3. 금전 제재 전처리 (환율 적용 → USD 통일)
FX = {
    "USD": 1.00, "CAD": 0.74, "GBP": 1.27, "EUR": 1.08,
    "AUD": 0.65, "ILS": 0.27, "SGD": 0.74, "BRL": 0.20, "ARS": 0.001,
}

def parse_usd(val):
    val = str(val).strip()
    m = re.match(r"([\d.]+)\s*([A-Z]*)", val)
    if not m:
        return None
    amount = float(m.group(1))
    currency = m.group(2).strip() if m.group(2).strip() else "USD"
    rate = FX.get(currency)
    return amount * rate if rate else None

df["penalty_usd"] = df["Monetary Penalty"].apply(
    lambda x: parse_usd(x) if pd.notna(x) else None
)

pen           = df[df["penalty_usd"].notna()].copy()
total_usd     = pen["penalty_usd"].sum()
mean_usd      = pen["penalty_usd"].mean()
median_usd    = pen["penalty_usd"].median()
max_usd       = pen["penalty_usd"].max()
pen_count     = len(pen)
total_count   = len(df)
non_pen_count = total_count - pen_count

print(f"\n{'='*50}")
print(f"전체 판례 수      : {total_count:,}건")
print(f"금전 제재 건수    : {pen_count:,}건 ({pen_count/total_count*100:.1f}%)")
print(f"비금전 제재 건수  : {non_pen_count:,}건 ({non_pen_count/total_count*100:.1f}%)")
print(f"총 금전 제재 금액 : ${total_usd:,.0f} USD")
print(f"평균 제재 금액    : ${mean_usd:,.0f} USD")
print(f"중앙값            : ${median_usd:,.0f} USD")
print(f"최대 제재 금액    : ${max_usd:,.0f} USD")
print(f"{'='*50}\n")

# ── 4. 연도별 집계
pen["Year"] = pen["Date"].dt.year
yearly = pen[pen["Year"] < 2026].groupby("Year").agg(
    count=("penalty_usd", "count"),
    total=("penalty_usd", "sum")
).reset_index()

# ── 5. 제재 금액 구간 분류
def penalty_tier(v):
    if v < 1000:    return "< $1K"
    elif v < 5000:  return "$1K–5K"
    elif v < 10000: return "$5K–10K"
    elif v < 50000: return "$10K–50K"
    else:           return "$50K+"

pen["tier"]  = pen["penalty_usd"].apply(penalty_tier)
tier_order   = ["< $1K", "$1K–5K", "$5K–10K", "$10K–50K", "$50K+"]
tier_counts  = pen["tier"].value_counts().reindex(tier_order).fillna(0)

# ── 6. Outcome 레이블
omap = {
    "warning":               "Warning",
    "order to show cause":   "Show Cause Order",
    "show cause order":      "Show Cause Order",
    "monetary sanction":     "Monetary Sanction",
    "admonishment":          "Admonishment",
    "bar referral":          "Bar Referral",
    "adverse costs order":   "Adverse Costs Order",
    "costs order":           "Costs Order",
    "case dismissed":        "Case Dismissed",
    "application dismissed": "Application Dismissed",
    "brief struck":          "Brief Struck",
}
df["outcome_label"] = df["Outcome"].str.strip().str.lower().map(
    lambda x: next((v for k, v in omap.items() if k in str(x)), str(x).title())
)
top_outcomes = df["outcome_label"].value_counts().head(8)

# ── 7. 시각화
fig = plt.figure(figsize=(24, 28))
fig.suptitle(
    "AI Hallucination Legal Cases — Damage Scale Quantification\n"
    f"Total {total_count:,} cases  |  Total monetary sanctions: ${total_usd/1e6:.2f}M USD",
    fontsize=16, fontweight="bold", y=0.99
)
gs = fig.add_gridspec(3, 2, hspace=0.70, wspace=0.45,
                      top=0.95, bottom=0.05, left=0.09, right=0.97)

ax1 = fig.add_subplot(gs[0, 0])
sizes  = [pen_count, non_pen_count]
labels = [f"Monetary\n({pen_count} cases)", f"Non-Monetary\n({non_pen_count} cases)"]
wedges, texts, autotexts = ax1.pie(
    sizes, labels=labels, autopct="%1.1f%%",
    colors=[PALETTE["red"], PALETTE["gray"]],
    startangle=90,
    wedgeprops={"width": 0.55, "edgecolor": "white", "linewidth": 2},
    textprops={"fontsize": 11},
    pctdistance=0.75, labeldistance=1.2,
)
for at in autotexts:
    at.set_fontsize(10)
    at.set_fontweight("bold")
ax1.set_title("Monetary vs Non-Monetary Sanctions", fontsize=13, fontweight="bold")

ax2 = fig.add_subplot(gs[0, 1])
monetary_keywords = ["Monetary", "Costs"]
bar_colors = [PALETTE["red"] if any(k in i for k in monetary_keywords)
              else PALETTE["blue"] for i in top_outcomes.index[::-1]]
b2 = ax2.barh(top_outcomes.index[::-1], top_outcomes.values[::-1],
              color=bar_colors, edgecolor="none", height=0.55)
for b in b2:
    ax2.text(b.get_width() + 3, b.get_y() + b.get_height() / 2,
             f"{int(b.get_width()):,}", va="center", fontsize=10)
ax2.set_xlabel("Number of Cases", fontsize=10, labelpad=8)
ax2.tick_params(axis="y", labelsize=10)
ax2.set_title("Top 8 Outcome Types", fontsize=13, fontweight="bold")
ax2.grid(axis="y", alpha=0)
ax2.set_xlim(0, top_outcomes.values.max() * 1.25)
patches = [mpatches.Patch(color=PALETTE["red"],  label="Monetary Sanctions"),
           mpatches.Patch(color=PALETTE["blue"], label="Non-Monetary Sanctions")]
ax2.legend(handles=patches, fontsize=9, loc="lower right")

ax3 = fig.add_subplot(gs[1, 0])
tier_colors = [PALETTE["green"], PALETTE["teal"], PALETTE["orange"],
               PALETTE["red"], PALETTE["purple"]]
b3 = ax3.bar(tier_order, tier_counts.values,
             color=tier_colors, edgecolor="none", width=0.5)
for b in b3:
    ax3.text(b.get_x() + b.get_width() / 2, b.get_height() + 1,
             str(int(b.get_height())), ha="center", fontsize=11, fontweight="bold")
ax3.set_ylabel("Number of Cases", fontsize=10, labelpad=8)
ax3.set_title("Penalty Amount Distribution by Tier", fontsize=13, fontweight="bold")
ax3.tick_params(axis="x", labelsize=11)
ax3.tick_params(axis="y", labelsize=10)
ax3.set_ylim(0, tier_counts.max() * 1.2)

ax4 = fig.add_subplot(gs[1, 1])
ax4.axis("off")
stats = [
    ("Total Monetary Sanctions",    f"${total_usd/1e6:.2f}M USD"),
    ("Cases with Monetary Penalty", f"{pen_count:,} / {total_count:,} cases"),
    ("Average Penalty",             f"${mean_usd:,.0f} USD"),
    ("Median Penalty",              f"${median_usd:,.0f} USD"),
    ("Max Single Penalty",          f"${max_usd:,.0f} USD"),
    ("Non-Monetary Sanctions",      f"{non_pen_count:,} cases (warnings, referrals, etc.)"),
]
y = 0.92
for label, value in stats:
    ax4.text(0.05, y, label, fontsize=11, color="#666", transform=ax4.transAxes)
    ax4.text(0.05, y - 0.07, value, fontsize=14, fontweight="bold",
             color=PALETTE["red"] if "Total" in label else "#222",
             transform=ax4.transAxes)
    y -= 0.17
ax4.set_title("Key Statistics", fontsize=13, fontweight="bold")

ax5 = fig.add_subplot(gs[2, :])
x = range(len(yearly))
ax5.bar(x, yearly["total"] / 1000, color=PALETTE["blue"],
        alpha=0.35, edgecolor="none", width=0.6, label="Total Amount ($K)")
ax5_r = ax5.twinx()
ax5_r.plot(x, yearly["count"], color=PALETTE["red"], linewidth=2.5,
           marker="o", markersize=6, markerfacecolor="white",
           markeredgewidth=2, label="Case Count")
ax5_r.tick_params(axis="y", labelsize=10)
ax5_r.set_ylabel("Case Count", fontsize=10, color=PALETTE["red"], labelpad=8)
ax5.set_xticks(x)
ax5.set_xticklabels(yearly["Year"].astype(str), fontsize=11)
ax5.set_ylabel("Total Amount ($K)", fontsize=10, labelpad=8)
ax5.set_title("Yearly Trend: Monetary Sanctions Count & Total Amount",
              fontsize=13, fontweight="bold")
ax5.tick_params(axis="x", labelsize=11)
ax5.tick_params(axis="y", labelsize=10)
lines1, labels1 = ax5.get_legend_handles_labels()
lines2, labels2 = ax5_r.get_legend_handles_labels()
ax5.legend(lines1 + lines2, labels1 + labels2, fontsize=10, loc="upper left")

# ── 8. 저장 → output/ 폴더
out = OUTPUT_DIR / "damage_analysis_dashboard.png"
plt.savefig(out, bbox_inches="tight", dpi=150)
print(f"저장 완료: {out}")
plt.show()