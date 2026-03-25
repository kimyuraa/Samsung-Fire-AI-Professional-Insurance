import os, sys, pathlib, re, warnings
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

warnings.filterwarnings("ignore")

# Korean font (Windows)
for p in ["C:/Windows/Fonts/malgun.ttf","C:/Windows/Fonts/gulim.ttc"]:
    if os.path.exists(p):
        fp = fm.FontProperties(fname=p)
        plt.rcParams["font.family"] = fp.get_name()
        plt.rcParams["axes.unicode_minus"] = False
        break

PALETTE = {"blue":"#5B8DEF","green":"#2ECC71","orange":"#F39C12",
           "red":"#E74C3C","purple":"#9B59B6","teal":"#1ABC9C"}

# Auto-find CSV
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
csv_path = next(
    (f for f in SCRIPT_DIR.iterdir()
     if f.suffix.lower()==".csv" and ("hallucination" in f.name.lower() or "할루" in f.name)),
    None
)
if csv_path is None:
    print(f"CSV file not found. Place the CSV in the same folder as this script.\nFolder: {SCRIPT_DIR}")
    sys.exit(1)

# Auto-detect encoding
df = None
for enc in ("utf-8-sig","utf-8","cp949"):
    try:
        df = pd.read_csv(csv_path, encoding=enc)
        print(f"Loaded ({enc}): {len(df):,} records")
        break
    except Exception:
        continue
if df is None:
    print("Failed to open CSV.")
    sys.exit(1)

df["Date"] = pd.to_datetime(df["Date"])
df["YearMonth"] = df["Date"].dt.to_period("M")

def simplify_party(p):
    p = str(p)
    if "Pro Se" in p: return "Pro Se Litigant"
    if any(x in p for x in ["Lawyer","Paralegal","Federal Defender"]): return "Lawyer / Legal Pro"
    return "Judge / Expert / Other"

df["Party_Simple"] = df["Party(ies)"].apply(simplify_party)
monthly = df.groupby("YearMonth").size().reset_index(name="count")
monthly["ym"] = monthly["YearMonth"].astype(str)
top_countries = df["State(s)"].value_counts().head(8)

for col, kw in [("has_fab","Fabricated"),("has_mis","Misrepresented"),("has_fq","False Quotes")]:
    df[col] = df["Hallucination Items"].apply(lambda x: bool(re.search(kw, str(x))))

hall = {
    "Fabricated":      df["has_fab"].sum(),
    "Misrepresented":  df["has_mis"].sum(),
    "False Quotes":    df["has_fq"].sum()
}

omap = {"warning":"Warning","order to show cause":"Show Cause Order","show cause order":"Show Cause Order",
        "monetary sanction":"Monetary Sanction","admonishment":"Admonishment",
        "bar referral":"Bar Referral","adverse costs order":"Adverse Costs Order",
        "costs order":"Costs Order","case dismissed":"Case Dismissed",
        "application dismissed":"Application Dismissed","brief struck":"Brief Struck"}
df["ol"] = df["Outcome"].str.strip().str.lower().map(
    lambda x: next((v for k,v in omap.items() if k in str(x)), str(x).title()))
top_out = df["ol"].value_counts().head(10)

exclude = {"implied","unidentified",""}
df["ai"] = df["AI Tool"].str.strip().str.lower()
top_tools = df[~df["ai"].isin(exclude)]["ai"].str.split(",").explode().str.strip().value_counts().head(8)

# ── Layout ─────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(24, 32))

gs = fig.add_gridspec(4, 2,
                      hspace=0.75, wspace=0.50,
                      top=0.97, bottom=0.04, left=0.09, right=0.97)

plt.rcParams.update({
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "axes.titlepad": 16,
})

# ── (1) Donut: Party Type ──────────────────────────────────────────────────────
ax1 = fig.add_subplot(gs[0, 0])
pc = df["Party_Simple"].value_counts()
ax1.pie(
    pc, labels=pc.index, autopct="%1.1f%%",
    colors=[PALETTE["blue"], PALETTE["green"], PALETTE["orange"]],
    startangle=90,
    wedgeprops={"width": 0.55, "edgecolor": "white", "linewidth": 2},
    textprops={"fontsize": 12},
    pctdistance=0.75,
    labeldistance=1.2,
)
ax1.set_title("Party Type", fontsize=14, fontweight="bold")

# ── (2) Horizontal bar: Cases by Country ──────────────────────────────────────
ax2 = fig.add_subplot(gs[0, 1])
b2 = ax2.barh(top_countries.index[::-1], top_countries.values[::-1],
              color=PALETTE["blue"], edgecolor="none", height=0.5)
for b in b2:
    ax2.text(b.get_width() + 10, b.get_y() + b.get_height() / 2,
             f"{int(b.get_width()):,}", va="center", fontsize=11)
ax2.set_xlabel("Number of Cases", fontsize=11, labelpad=10)
ax2.tick_params(axis="y", labelsize=12, pad=6)
ax2.tick_params(axis="x", labelsize=11)
ax2.set_title("Cases by Country (Top 8)", fontsize=14, fontweight="bold")
ax2.grid(axis="y", alpha=0)
ax2.set_xlim(0, top_countries.values.max() * 1.25)

# ── (3) Bar: Hallucination Type ───────────────────────────────────────────────
ax3 = fig.add_subplot(gs[1, 0])
hk = list(hall.keys())
hv = list(hall.values())
b3 = ax3.bar(hk, hv,
             color=[PALETTE["red"], PALETTE["orange"], PALETTE["purple"]],
             edgecolor="none", width=0.4)
for b in b3:
    ax3.text(b.get_x() + b.get_width() / 2, b.get_height() + 14,
             f"{int(b.get_height()):,}", ha="center", fontsize=12, fontweight="bold")
ax3.set_ylabel("Number of Cases", fontsize=11, labelpad=10)
ax3.tick_params(axis="x", labelsize=12, pad=8)
ax3.tick_params(axis="y", labelsize=11)
ax3.set_title("Cases by Hallucination Type", fontsize=14, fontweight="bold")
ax3.set_ylim(0, max(hv) * 1.2)

# ── (4) Horizontal bar: Outcome Type ──────────────────────────────────────────
ax4 = fig.add_subplot(gs[1, 1])
b4 = ax4.barh(top_out.index[::-1], top_out.values[::-1],
              color=PALETTE["green"], edgecolor="none", height=0.45)
for b in b4:
    ax4.text(b.get_width() + 4, b.get_y() + b.get_height() / 2,
             f"{int(b.get_width()):,}", va="center", fontsize=10)
ax4.set_xlabel("Count", fontsize=11, labelpad=10)
ax4.tick_params(axis="y", labelsize=11, pad=8)
ax4.tick_params(axis="x", labelsize=10)
ax4.set_title("Top 10 Outcome Types", fontsize=14, fontweight="bold")
ax4.grid(axis="y", alpha=0)
ax4.set_xlim(0, top_out.values.max() * 1.25)
ax4.margins(y=0.08)

# ── (5) Line: Monthly Trend ───────────────────────────────────────────────────
ax5 = fig.add_subplot(gs[2, :])
ax5.plot(monthly["ym"], monthly["count"],
         color=PALETTE["blue"], linewidth=2.5,
         marker="o", markersize=5, markerfacecolor="white", markeredgewidth=2)
ax5.fill_between(monthly["ym"], monthly["count"], alpha=0.12, color=PALETTE["blue"])
ax5.set_ylabel("Number of Cases", fontsize=11, labelpad=10)
ax5.set_title("Monthly Case Count Trend", fontsize=14, fontweight="bold")
te = max(2, len(monthly) // 16)
ax5.set_xticks(range(0, len(monthly), te))
ax5.set_xticklabels(
    [monthly["ym"].iloc[i] for i in range(0, len(monthly), te)],
    rotation=45, ha="right", fontsize=10
)
ax5.tick_params(axis="x", pad=6)
ax5.tick_params(axis="y", labelsize=11)
pi = monthly["count"].idxmax()
ax5.annotate(
    f"Peak: {monthly['count'].iloc[pi]} cases\n({monthly['ym'].iloc[pi]})",
    xy=(pi, monthly["count"].iloc[pi]),
    xytext=(max(pi - 7, 0), monthly["count"].iloc[pi] + 12),
    fontsize=10, color="#555",
    arrowprops=dict(arrowstyle="->", color="#aaa", lw=1.2)
)

# ── (6) Bar: AI Tool Ranking ──────────────────────────────────────────────────
ax6 = fig.add_subplot(gs[3, :])
tc = [PALETTE["red"], PALETTE["blue"], PALETTE["purple"], PALETTE["teal"],
      PALETTE["orange"], PALETTE["orange"], PALETTE["green"], PALETTE["blue"]]
b6 = ax6.bar(range(len(top_tools)), top_tools.values,
             color=tc[:len(top_tools)], edgecolor="none", width=0.45)
for b in b6:
    ax6.text(b.get_x() + b.get_width() / 2, b.get_height() + 1,
             str(int(b.get_height())), ha="center", fontsize=12, fontweight="bold")
ax6.set_ylabel("Count", fontsize=11, labelpad=10)
ax6.set_title("AI Tool Ranking (Excl. Implied / Unidentified)", fontsize=14, fontweight="bold")
ax6.set_xticks(range(len(top_tools)))
ax6.set_xticklabels([t.title() for t in top_tools.index],
                    fontsize=12, rotation=15, ha="right")
ax6.tick_params(axis="x", pad=8)
ax6.tick_params(axis="y", labelsize=11)
ax6.set_ylim(0, top_tools.values[0] * 1.25)

# ── Save ───────────────────────────────────────────────────────────────────────
out = SCRIPT_DIR / "ai_hallucination_dashboard.png"
plt.savefig(out, bbox_inches="tight", dpi=150)
print(f"Saved: {out}")
plt.show()
