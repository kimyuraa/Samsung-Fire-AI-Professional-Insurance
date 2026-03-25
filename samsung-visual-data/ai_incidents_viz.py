import os, sys, pathlib, warnings
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

warnings.filterwarnings("ignore")

# Font setup
for p in ["C:/Windows/Fonts/malgun.ttf", "C:/Windows/Fonts/gulim.ttc"]:
    if os.path.exists(p):
        fp = fm.FontProperties(fname=p)
        plt.rcParams["font.family"] = fp.get_name()
        plt.rcParams["axes.unicode_minus"] = False
        break

PALETTE = {"blue":"#378ADD","light_blue":"#85B7EB","green":"#2ECC71",
           "red":"#E24B4A","purple":"#9B59B6","gray":"#888780"}

plt.rcParams.update({
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.2,
    "figure.dpi": 130,
})

# Auto-find CSV
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
csv_path = next(
    (f for f in SCRIPT_DIR.iterdir()
     if f.suffix.lower() == ".csv" and "incident" in f.name.lower()),
    None
)
if csv_path is None:
    print(f"CSV file not found.\nFolder: {SCRIPT_DIR}")
    sys.exit(1)

# Load CSV
df = None
for enc in ("utf-8-sig", "utf-8", "cp949"):
    try:
        df = pd.read_csv(csv_path, encoding=enc)
        print(f"Loaded ({enc}): {len(df):,} rows")
        break
    except Exception:
        continue
if df is None:
    print("Cannot open CSV.")
    sys.exit(1)

# Rename long column
col = [c for c in df.columns if "incident" in c.lower() or "artificial" in c.lower()][0]
df = df.rename(columns={col: "incidents"})

years  = df["Year"].tolist()
counts = df["incidents"].tolist()

# Derived series
yoy = [0] + [round((counts[i] - counts[i-1]) / counts[i-1] * 100, 1)
              for i in range(1, len(counts))]
cumulative = list(np.cumsum(counts))

total   = sum(counts)
peak_y  = max(counts)
peak_yr = years[counts.index(peak_y)]
cagr    = (counts[-1] / counts[0]) ** (1 / (years[-1] - years[0])) - 1

print(f"\nTotal incidents : {total:,}")
print(f"Peak year       : {peak_yr} ({peak_y} incidents)")
print(f"CAGR            : {cagr*100:.1f}%")
print(f"Growth (total)  : +{round((counts[-1]/counts[0]-1)*100):,}%")

# ── Layout ────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(20, 20))
gs  = fig.add_gridspec(3, 2, hspace=0.55, wspace=0.38,
                       top=0.95, bottom=0.06, left=0.08, right=0.97)

# ── (1) Line: full trend ──────────────────────────────────────────────────────
ax1 = fig.add_subplot(gs[0, :])
ax1.plot(years, counts, color=PALETTE["blue"], linewidth=2.5,
         marker="o", markersize=7, markerfacecolor="white", markeredgewidth=2.5)
ax1.fill_between(years, counts, alpha=0.10, color=PALETTE["blue"])
for x, y in zip(years, counts):
    ax1.text(x, y + 4, str(y), ha="center", fontsize=9.5, color=PALETTE["blue"], fontweight="bold")
ax1.set_title("Annual Reported AI Incidents & Controversies (2012–2024)",
              fontsize=14, fontweight="bold")
ax1.set_ylabel("Number of Incidents", fontsize=11, labelpad=8)
ax1.set_xticks(years)
ax1.set_xticklabels(years, fontsize=11)
ax1.tick_params(axis="y", labelsize=11)
ax1.set_ylim(0, max(counts) * 1.18)

# ── (2) Bar: year-over-year change ────────────────────────────────────────────
ax2 = fig.add_subplot(gs[1, 0])
colors_yoy = [PALETTE["green"] if v >= 0 else PALETTE["red"] for v in yoy[1:]]
bars2 = ax2.bar(years[1:], yoy[1:], color=colors_yoy, edgecolor="none", width=0.6)
for bar, v in zip(bars2, yoy[1:]):
    offset = 1.5 if v >= 0 else -5
    ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + offset,
             f"{'+' if v >= 0 else ''}{v:.0f}%",
             ha="center", fontsize=9, fontweight="bold",
             color=PALETTE["green"] if v >= 0 else PALETTE["red"])
ax2.axhline(0, color=PALETTE["gray"], linewidth=0.8, linestyle="--")
ax2.set_title("Year-over-Year Change (%)", fontsize=13, fontweight="bold")
ax2.set_ylabel("Change (%)", fontsize=11, labelpad=8)
ax2.set_xticks(years[1:])
ax2.set_xticklabels(years[1:], rotation=40, ha="right", fontsize=10)
ax2.tick_params(axis="y", labelsize=11)

# ── (3) Line: cumulative ──────────────────────────────────────────────────────
ax3 = fig.add_subplot(gs[1, 1])
ax3.plot(years, cumulative, color=PALETTE["purple"], linewidth=2.5,
         marker="o", markersize=6, markerfacecolor="white", markeredgewidth=2)
ax3.fill_between(years, cumulative, alpha=0.10, color=PALETTE["purple"])
ax3.set_title("Cumulative Incidents Over Time", fontsize=13, fontweight="bold")
ax3.set_ylabel("Cumulative Count", fontsize=11, labelpad=8)
ax3.set_xticks(years)
ax3.set_xticklabels(years, rotation=40, ha="right", fontsize=10)
ax3.tick_params(axis="y", labelsize=11)
ax3.set_ylim(0, max(cumulative) * 1.12)

# ── (4) Bar: per-year count ───────────────────────────────────────────────────
ax4 = fig.add_subplot(gs[2, :])
bar_colors = [PALETTE["red"] if y == peak_yr else PALETTE["light_blue"] for y in years]
bars4 = ax4.bar(years, counts, color=bar_colors, edgecolor="none", width=0.65)
for bar, v in zip(bars4, counts):
    ax4.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2,
             str(v), ha="center", fontsize=10, fontweight="bold", color="#555")
ax4.set_title("Incidents per Year — Bar View  (red = peak year)",
              fontsize=13, fontweight="bold")
ax4.set_ylabel("Number of Incidents", fontsize=11, labelpad=8)
ax4.set_xticks(years)
ax4.set_xticklabels(years, fontsize=11)
ax4.tick_params(axis="y", labelsize=11)
ax4.set_ylim(0, max(counts) * 1.18)

# ── Save ──────────────────────────────────────────────────────────────────────
out = SCRIPT_DIR / "ai_incidents_dashboard.png"
plt.savefig(out, bbox_inches="tight", dpi=150)
print(f"\nSaved: {out}")
plt.show()
