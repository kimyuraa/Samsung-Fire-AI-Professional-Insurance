import os, sys, pathlib, re, warnings
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

warnings.filterwarnings("ignore")

# 한글 폰트
for p in ["C:/Windows/Fonts/malgun.ttf","C:/Windows/Fonts/gulim.ttc"]:
    if os.path.exists(p):
        fp = fm.FontProperties(fname=p)
        plt.rcParams["font.family"] = fp.get_name()
        plt.rcParams["axes.unicode_minus"] = False
        break

PALETTE = {"blue":"#5B8DEF","green":"#2ECC71","orange":"#F39C12",
           "red":"#E74C3C","purple":"#9B59B6","teal":"#1ABC9C"}

# CSV 자동 탐색
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
csv_path = next(
    (f for f in SCRIPT_DIR.iterdir()
     if f.suffix.lower()==".csv" and ("hallucination" in f.name.lower() or "할루" in f.name)),
    None
)
if csv_path is None:
    print(f"CSV 파일을 찾을 수 없습니다. 이 파일과 같은 폴더에 CSV를 두세요.\n폴더: {SCRIPT_DIR}")
    sys.exit(1)

# 인코딩 자동 감지
df = None
for enc in ("utf-8-sig","utf-8","cp949"):
    try:
        df = pd.read_csv(csv_path, encoding=enc)
        print(f"로딩 완료 ({enc}): {len(df):,}건")
        break
    except Exception:
        continue
if df is None:
    print("CSV를 열 수 없습니다.")
    sys.exit(1)

df["Date"] = pd.to_datetime(df["Date"])
df["YearMonth"] = df["Date"].dt.to_period("M")

def simplify_party(p):
    p = str(p)
    if "Pro Se" in p: return "Pro Se 소송인"
    if any(x in p for x in ["Lawyer","Paralegal","Federal Defender"]): return "변호사/법조인"
    return "판사/전문가/기타"

df["Party_Simple"] = df["Party(ies)"].apply(simplify_party)
monthly = df.groupby("YearMonth").size().reset_index(name="count")
monthly["ym"] = monthly["YearMonth"].astype(str)
top_countries = df["State(s)"].value_counts().head(8)

for col, kw in [("has_fab","Fabricated"),("has_mis","Misrepresented"),("has_fq","False Quotes")]:
    df[col] = df["Hallucination Items"].apply(lambda x: bool(re.search(kw, str(x))))

hall = {
    "조작\n(Fabricated)":      df["has_fab"].sum(),
    "왜곡\n(Misrepresented)":  df["has_mis"].sum(),
    "허위인용\n(False Quotes)": df["has_fq"].sum()
}

omap = {"warning":"경고","order to show cause":"시정명령","show cause order":"시정명령",
        "monetary sanction":"금전 제재","admonishment":"훈계","bar referral":"변호사 징계 회부",
        "adverse costs order":"비용 명령","costs order":"비용 명령","case dismissed":"소각하",
        "application dismissed":"신청 기각","brief struck":"서면 기각"}
df["ol"] = df["Outcome"].str.strip().str.lower().map(
    lambda x: next((v for k,v in omap.items() if k in str(x)), str(x).title()))
top_out = df["ol"].value_counts().head(10)

exclude = {"implied","unidentified",""}
df["ai"] = df["AI Tool"].str.strip().str.lower()
top_tools = df[~df["ai"].isin(exclude)]["ai"].str.split(",").explode().str.strip().value_counts().head(8)

cmap = {"USA":"미국","Canada":"캐나다","Australia":"호주","UK":"영국",
        "Israel":"이스라엘","France":"프랑스","Brazil":"브라질","Argentina":"아르헨티나"}

# ── 차트 레이아웃 ──────────────────────────────────────────────────────────────
# 각 서브플롯을 독립적으로 크게 만들어 글씨 겹침 방지
fig = plt.figure(figsize=(22, 28))
fig.suptitle(
    f"AI 할루시네이션 법률 판례 데이터베이스 시각화\n"
    f"{len(df):,}건  |  {df['Date'].min().strftime('%Y.%m')} ~ {df['Date'].max().strftime('%Y.%m')}",
    fontsize=18, fontweight="bold", y=0.99
)

# hspace/wspace 넉넉히
gs = fig.add_gridspec(4, 2, hspace=0.65, wspace=0.45,
                      top=0.96, bottom=0.04, left=0.08, right=0.97)

plt.rcParams.update({
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "axes.titlepad": 14,
})

# ── (1) 도넛: 당사자 유형 ──────────────────────────────────────────────────────
ax1 = fig.add_subplot(gs[0, 0])
pc = df["Party_Simple"].value_counts()
wedges, texts, autotexts = ax1.pie(
    pc, labels=pc.index, autopct="%1.1f%%",
    colors=[PALETTE["blue"], PALETTE["green"], PALETTE["orange"]],
    startangle=90,
    wedgeprops={"width": 0.55, "edgecolor": "white", "linewidth": 2},
    textprops={"fontsize": 11},
    pctdistance=0.75,
    labeldistance=1.15,
)
for at in autotexts:
    at.set_fontsize(10)
    at.set_fontweight("bold")
ax1.set_title("당사자 유형", fontsize=13, fontweight="bold")

# ── (2) 가로 막대: 국가별 ──────────────────────────────────────────────────────
ax2 = fig.add_subplot(gs[0, 1])
lkr = [cmap.get(c, c) for c in top_countries.index]
b2 = ax2.barh(lkr[::-1], top_countries.values[::-1],
              color=PALETTE["blue"], edgecolor="none", height=0.55)
for b in b2:
    ax2.text(b.get_width() + 8, b.get_y() + b.get_height() / 2,
             f"{int(b.get_width()):,}", va="center", fontsize=10)
ax2.set_xlabel("판례 수", fontsize=10, labelpad=8)
ax2.tick_params(axis="y", labelsize=11)
ax2.tick_params(axis="x", labelsize=10)
ax2.set_title("국가별 판례 수 (상위 8개국)", fontsize=13, fontweight="bold")
ax2.grid(axis="y", alpha=0)
ax2.set_xlim(0, top_countries.values.max() * 1.2)

# ── (3) 막대: 할루시네이션 유형 ────────────────────────────────────────────────
ax3 = fig.add_subplot(gs[1, 0])
hk = list(hall.keys())
hv = list(hall.values())
b3 = ax3.bar(hk, hv,
             color=[PALETTE["red"], PALETTE["orange"], PALETTE["purple"]],
             edgecolor="none", width=0.45)
for b in b3:
    ax3.text(b.get_x() + b.get_width() / 2, b.get_height() + 12,
             f"{int(b.get_height()):,}", ha="center", fontsize=11, fontweight="bold")
ax3.set_ylabel("케이스 수", fontsize=10, labelpad=8)
ax3.tick_params(axis="x", labelsize=11)
ax3.tick_params(axis="y", labelsize=10)
ax3.set_title("할루시네이션 유형별 케이스 수", fontsize=13, fontweight="bold")
ax3.set_ylim(0, max(hv) * 1.18)

# ── (4) 가로 막대: 결과 유형 ────────────────────────────────────────────────────
ax4 = fig.add_subplot(gs[1, 1])
b4 = ax4.barh(top_out.index[::-1], top_out.values[::-1],
              color=PALETTE["green"], edgecolor="none", height=0.6)
for b in b4:
    ax4.text(b.get_width() + 3, b.get_y() + b.get_height() / 2,
             f"{int(b.get_width()):,}", va="center", fontsize=10)
ax4.set_xlabel("건수", fontsize=10, labelpad=8)
ax4.tick_params(axis="y", labelsize=10)
ax4.tick_params(axis="x", labelsize=10)
ax4.set_title("주요 결과(Outcome) 유형 (상위 10개)", fontsize=13, fontweight="bold")
ax4.grid(axis="y", alpha=0)
ax4.set_xlim(0, top_out.values.max() * 1.2)

# ── (5) 라인: 월별 추이 ────────────────────────────────────────────────────────
ax5 = fig.add_subplot(gs[2, :])
ax5.plot(monthly["ym"], monthly["count"],
         color=PALETTE["blue"], linewidth=2.5,
         marker="o", markersize=5, markerfacecolor="white", markeredgewidth=2)
ax5.fill_between(monthly["ym"], monthly["count"], alpha=0.12, color=PALETTE["blue"])
ax5.set_ylabel("판례 수", fontsize=10, labelpad=8)
ax5.set_title("월별 판례 건수 추이", fontsize=13, fontweight="bold")
te = max(1, len(monthly) // 14)
ax5.set_xticks(range(0, len(monthly), te))
ax5.set_xticklabels(
    [monthly["ym"].iloc[i] for i in range(0, len(monthly), te)],
    rotation=40, ha="right", fontsize=10
)
ax5.tick_params(axis="y", labelsize=10)
pi = monthly["count"].idxmax()
ax5.annotate(
    f"최고 {monthly['count'].iloc[pi]}건\n({monthly['ym'].iloc[pi]})",
    xy=(pi, monthly["count"].iloc[pi]),
    xytext=(max(pi - 6, 0), monthly["count"].iloc[pi] + 10),
    fontsize=9, color="#555",
    arrowprops=dict(arrowstyle="->", color="#aaa", lw=1.2)
)

# ── (6) 막대: AI 도구 ──────────────────────────────────────────────────────────
ax6 = fig.add_subplot(gs[3, :])
tc = [PALETTE["red"], PALETTE["blue"], PALETTE["purple"], PALETTE["teal"],
      PALETTE["orange"], PALETTE["orange"], PALETTE["green"], PALETTE["blue"]]
b6 = ax6.bar(top_tools.index, top_tools.values,
             color=tc[:len(top_tools)], edgecolor="none", width=0.5)
for b in b6:
    ax6.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.8,
             str(int(b.get_height())), ha="center", fontsize=11, fontweight="bold")
ax6.set_ylabel("건수", fontsize=10, labelpad=8)
ax6.set_title("명시된 AI 도구 순위 (Implied/Unidentified 제외)", fontsize=13, fontweight="bold")
ax6.set_xticklabels([t.title() for t in top_tools.index], fontsize=11)
ax6.tick_params(axis="y", labelsize=10)
ax6.set_ylim(0, top_tools.values[0] * 1.22)

# ── 저장 ───────────────────────────────────────────────────────────────────────
out = SCRIPT_DIR / "ai_hallucination_dashboard.png"
plt.savefig(out, bbox_inches="tight", dpi=150)
print(f"저장 완료: {out}")
plt.show()
