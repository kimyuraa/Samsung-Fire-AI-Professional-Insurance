"""
AI 할루시네이션 법률 판례 데이터 시각화
사용법: python ai_hallucination_viz.py
필요 패키지: pandas, matplotlib
설치: pip install pandas matplotlib

[주의] CSV 파일을 이 스크립트와 같은 폴더에 두세요.
"""

import os
import sys
import pathlib
import re
import warnings

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

warnings.filterwarnings("ignore")

# ── 0. 한글 폰트 설정 (Windows) ────────────────────────────────────────────────
def set_korean_font():
    candidates = [
        "C:/Windows/Fonts/malgun.ttf",
        "C:/Windows/Fonts/gulim.ttc",
        "C:/Windows/Fonts/batang.ttc",
    ]
    for path in candidates:
        if os.path.exists(path):
            font_prop = fm.FontProperties(fname=path)
            plt.rcParams["font.family"] = font_prop.get_name()
            plt.rcParams["axes.unicode_minus"] = False
            print(f"폰트 설정: {font_prop.get_name()}")
            return
    print("경고: 한글 폰트를 찾지 못했습니다. 한글이 깨질 수 있습니다.")

set_korean_font()

plt.rcParams.update({
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "figure.dpi": 130,
})

PALETTE = {
    "blue":   "#5B8DEF",
    "green":  "#2ECC71",
    "orange": "#F39C12",
    "red":    "#E74C3C",
    "purple": "#9B59B6",
    "teal":   "#1ABC9C",
}

# ── 1. CSV 파일 경로 자동 탐색 ─────────────────────────────────────────────────
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent

def find_csv(directory):
    for f in directory.iterdir():
        name_lower = f.name.lower()
        if f.suffix.lower() == ".csv" and (
            "hallucination" in name_lower or "\ud560\ub8e8" in f.name
        ):
            return f
    return None

csv_path = find_csv(SCRIPT_DIR)

if csv_path is None:
    print("CSV \ud30c\uc77c\uc744 \uc790\ub3d9\uc73c\ub85c \ucc3e\uc9c0 \ubabb\ud588\uc2b5\ub2c8\ub2e4.")
    print(f"\uc2a4\ud06c\ub9bd\ud2b8 \ud3f4\ub354: {SCRIPT_DIR}")
    print("CSV \ud30c\uc77c\uc744 \uac19\uc740 \ud3f4\ub354\uc5d0 \ub123\uace0 \ub2e4\uc2dc \uc2e4\ud589\ud558\uc138\uc694.")
    sys.exit(1)

print(f"CSV \ud30c\uc77c: {csv_path}")

# ── 2. 데이터 로딩 (인코딩 자동 감지) ─────────────────────────────────────────
df = None
for enc in ("utf-8-sig", "utf-8", "cp949"):
    try:
        df = pd.read_csv(csv_path, encoding=enc)
        print(f"\uc778\ucf54\ub529: {enc}  |  \uc804\uccb4 {len(df):,}\uac74")
        break
    except Exception:
        continue

if df is None:
    print("CSV \ud30c\uc77c\uc744 \uc5f4 \uc218 \uc5c6\uc2b5\ub2c8\ub2e4.")
    sys.exit(1)

df["Date"] = pd.to_datetime(df["Date"])
df["YearMonth"] = df["Date"].dt.to_period("M")
print(f"\uae30\uac04: {df['Date'].min().date()} ~ {df['Date'].max().date()}\n")

# ── 3. 전처리 ──────────────────────────────────────────────────────────────────
def simplify_party(p):
    p = str(p)
    if "Pro Se" in p:
        return "Pro Se \uc18c\uc1a1\uc778"
    if "Lawyer" in p or "Paralegal" in p or "Federal Defender" in p:
        return "\ubcc0\ud638\uc0ac/\ubc95\uc870\uc778"
    return "\ud310\uc0ac/\uc804\ubb38\uac00/\uae30\ud0c0"

df["Party_Simple"] = df["Party(ies)"].apply(simplify_party)

monthly = df.groupby("YearMonth").size().reset_index(name="count")
monthly["YearMonth_str"] = monthly["YearMonth"].astype(str)

top_countries = df["State(s)"].value_counts().head(8)

df["has_fabricated"]     = df["Hallucination Items"].apply(lambda x: bool(re.search("Fabricated",     str(x))))
df["has_misrepresented"] = df["Hallucination Items"].apply(lambda x: bool(re.search("Misrepresented", str(x))))
df["has_false_quotes"]   = df["Hallucination Items"].apply(lambda x: bool(re.search("False Quotes",   str(x))))

hall_counts = {
    "\uc870\uc791 (Fabricated)":      df["has_fabricated"].sum(),
    "\uc65c\uace1 (Misrepresented)":  df["has_misrepresented"].sum(),
    "\ud5c8\uc704\uc778\uc6a9 (False Quotes)": df["has_false_quotes"].sum(),
}

outcome_map = {
    "warning":               "\uacbd\uace0 (Warning)",
    "order to show cause":   "\uc2dc\uc815\uba85\ub839",
    "show cause order":      "\uc2dc\uc815\uba85\ub839",
    "monetary sanction":     "\uae08\uc804 \uc81c\uc7ac",
    "admonishment":          "\ud6c8\uacc4",
    "bar referral":          "\ubcc0\ud638\uc0ac \uc9d5\uacc4 \ud68c\ubd80",
    "adverse costs order":   "\ube44\uc6a9 \uba85\ub839",
    "costs order":           "\ube44\uc6a9 \uba85\ub839",
    "case dismissed":        "\uc18c\uac01\ud558",
    "application dismissed": "\uc2e0\uccad \uae30\uac01",
    "brief struck":          "\uc11c\uba74 \uae30\uac01",
}
df["Outcome_label"] = df["Outcome"].str.strip().str.lower().map(
    lambda x: next((v for k, v in outcome_map.items() if k in str(x)), str(x).title())
)
top_outcomes = df["Outcome_label"].value_counts().head(10)

exclude = {"implied", "unidentified", ""}
df["AI_norm"] = df["AI Tool"].str.strip().str.lower()
named_tools = df[~df["AI_norm"].isin(exclude)]["AI_norm"].str.split(",").explode().str.strip()
top_tools = named_tools.value_counts().head(8)

country_labels_map = {
    "USA": "\ubbf8\uad6d", "Canada": "\uce90\ub098\ub2e4", "Australia": "\ud638\uc8fc", "UK": "\uc601\uad6d",
    "Israel": "\uc774\uc2a4\ub77c\uc5d8", "France": "\ud504\ub791\uc2a4", "Brazil": "\ube0c\ub77c\uc9c8", "Argentina": "\uc544\ub974\ud5e8\ud2f0\ub098",
}

# ── 4. 대시보드 그리기 ─────────────────────────────────────────────────────────
fig = plt.figure(figsize=(18, 20))
fig.suptitle(
    f"AI \ud560\ub8e8\uc2dc\ub124\uc774\uc158 \ubc95\ub960 \ud310\ub840 \ub370\uc774\ud130\ubca0\uc774\uc2a4 \uc2dc\uac01\ud654\n"
    f"\uc804\uccb4 {len(df):,}\uac74  |  {df['Date'].min().strftime('%Y.%m')} ~ {df['Date'].max().strftime('%Y.%m')}",
    fontsize=16, fontweight="bold", y=0.98,
)
gs = fig.add_gridspec(4, 2, hspace=0.55, wspace=0.35)

# (1) 도넛: 당사자 유형
ax1 = fig.add_subplot(gs[0, 0])
party_counts = df["Party_Simple"].value_counts()
ax1.pie(
    party_counts,
    labels=party_counts.index,
    autopct="%1.1f%%",
    colors=[PALETTE["blue"], PALETTE["green"], PALETTE["orange"]],
    startangle=90,
    wedgeprops={"width": 0.55, "edgecolor": "white", "linewidth": 1.5},
    textprops={"fontsize": 10},
)
ax1.set_title("\ub2f9\uc0ac\uc790 \uc720\ud615", fontsize=12, fontweight="bold", pad=10)

# (2) 가로 막대: 국가별
ax2 = fig.add_subplot(gs[0, 1])
labels_kr = [country_labels_map.get(c, c) for c in top_countries.index]
bars2 = ax2.barh(labels_kr[::-1], top_countries.values[::-1],
                 color=PALETTE["blue"], edgecolor="none", height=0.6)
for bar in bars2:
    ax2.text(bar.get_width() + 5, bar.get_y() + bar.get_height() / 2,
             f"{int(bar.get_width()):,}", va="center", fontsize=9)
ax2.set_xlabel("\ud310\ub840 \uc218", fontsize=9)
ax2.set_title("\uad6d\uac00\ubcc4 \ud310\ub840 \uc218 (\uc0c1\uc704 8\uac1c\uad6d)", fontsize=12, fontweight="bold")
ax2.grid(axis="y", alpha=0)

# (3) 막대: 할루시네이션 유형
ax3 = fig.add_subplot(gs[1, 0])
h_labels = list(hall_counts.keys())
h_vals   = list(hall_counts.values())
bars3 = ax3.bar(h_labels, h_vals,
                color=[PALETTE["red"], PALETTE["orange"], PALETTE["purple"]],
                edgecolor="none", width=0.5)
for bar in bars3:
    ax3.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 8,
             f"{int(bar.get_height()):,}", ha="center", fontsize=10, fontweight="bold")
ax3.set_ylabel("\ucf00\uc774\uc2a4 \uc218", fontsize=9)
ax3.set_title("\ud560\ub8e8\uc2dc\ub124\uc774\uc158 \uc720\ud615\ubcc4 \ucf00\uc774\uc2a4 \uc218", fontsize=12, fontweight="bold")
ax3.set_ylim(0, max(h_vals) * 1.15)

# (4) 가로 막대: 결과 유형
ax4 = fig.add_subplot(gs[1, 1])
bars4 = ax4.barh(top_outcomes.index[::-1], top_outcomes.values[::-1],
                 color=PALETTE["green"], edgecolor="none", height=0.65)
for bar in bars4:
    ax4.text(bar.get_width() + 2, bar.get_y() + bar.get_height() / 2,
             f"{int(bar.get_width()):,}", va="center", fontsize=9)
ax4.set_xlabel("\uac74\uc218", fontsize=9)
ax4.set_title("\uc8fc\uc694 \uacb0\uacfc(Outcome) \uc720\ud615 (\uc0c1\uc704 10\uac1c)", fontsize=12, fontweight="bold")
ax4.grid(axis="y", alpha=0)

# (5) 라인: 월별 추이
ax5 = fig.add_subplot(gs[2, :])
ax5.plot(monthly["YearMonth_str"], monthly["count"],
         color=PALETTE["blue"], linewidth=2.2,
         marker="o", markersize=4, markerfacecolor="white", markeredgewidth=1.5)
ax5.fill_between(monthly["YearMonth_str"], monthly["count"],
                 alpha=0.12, color=PALETTE["blue"])
ax5.set_ylabel("\ud310\ub840 \uc218", fontsize=9)
ax5.set_title("\uc6d4\ubcc4 \ud310\ub840 \uac74\uc218 \ucd94\uc774", fontsize=12, fontweight="bold")
tick_every = max(1, len(monthly) // 12)
ax5.set_xticks(range(0, len(monthly), tick_every))
ax5.set_xticklabels(
    [monthly["YearMonth_str"].iloc[i] for i in range(0, len(monthly), tick_every)],
    rotation=35, ha="right", fontsize=9,
)
peak_idx = monthly["count"].idxmax()
peak_y   = monthly["count"].iloc[peak_idx]
peak_x   = monthly["YearMonth_str"].iloc[peak_idx]
ax5.annotate(f"\ucd5c\uace0 {peak_y}\uac74\n({peak_x})",
             xy=(peak_idx, peak_y),
             xytext=(max(peak_idx - 5, 0), peak_y + 8),
             fontsize=8.5, color="#555",
             arrowprops=dict(arrowstyle="->", color="#aaa", lw=1.2))

# (6) 막대: AI 도구
ax6 = fig.add_subplot(gs[3, :])
tool_colors = [PALETTE["red"], PALETTE["blue"], PALETTE["purple"], PALETTE["teal"],
               PALETTE["orange"], PALETTE["orange"], PALETTE["green"], PALETTE["blue"]]
bars6 = ax6.bar(top_tools.index, top_tools.values,
                color=tool_colors[:len(top_tools)], edgecolor="none", width=0.55)
for bar in bars6:
    ax6.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
             str(int(bar.get_height())), ha="center", fontsize=10, fontweight="bold")
ax6.set_ylabel("\uac74\uc218", fontsize=9)
ax6.set_title("\uba85\uc2dc\ub41c AI \ub3c4\uad6c \uc21c\uc704 (Implied/Unidentified \uc81c\uc678)", fontsize=12, fontweight="bold")
ax6.set_xticklabels([t.title() for t in top_tools.index], fontsize=10)
ax6.set_ylim(0, top_tools.values[0] * 1.2)

# ── 5. 저장 ────────────────────────────────────────────────────────────────────
out = SCRIPT_DIR / "ai_hallucination_dashboard.png"
plt.savefig(out, bbox_inches="tight", dpi=150)
print(f"\n\uc800\uc7a5 \uc644\ub8cc: {out}")
plt.show()
