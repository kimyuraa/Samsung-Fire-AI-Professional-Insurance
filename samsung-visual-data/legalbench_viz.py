import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import numpy as np
import os

# Save outputs next to this script file
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def out(filename):
    return os.path.join(OUTPUT_DIR, filename)

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False

# error_risk = 1 - accuracy  (higher = more likely AI error)
RAW = {
    "Contract Review\n(CUAD)": [
        ("Affiliate License (Licensee)",   1-0.9242),
        ("Affiliate License (Licensor)",   1-0.9659),
        ("Anti-Assignment",                1-0.8669),
        ("Audit Rights",                   1-0.9265),
        ("Cap on Liability",               1-0.9390),
        ("Change of Control",              1-0.8462),
        ("Competitive Restriction Exc.",   1-0.8636),
        ("Covenant Not to Sue",            1-0.9351),
        ("Effective Date",                 1-0.9534),
        ("Exclusivity",                    1-0.9278),
        ("Expiration Date",                1-0.7557),
        ("Governing Law",                  1-0.9886),
        ("Insurance",                      1-0.9602),
        ("IP Ownership Assignment",        1-0.9132),
        ("Irrevocable/Perpetual License",  1-0.9355),
        ("Joint IP Ownership",             1-0.9375),
        ("License Grant",                  1-0.9355),
        ("Liquidated Damages",             1-0.9364),
        ("Minimum Commitment",             1-0.8575),
        ("Most Favored Nation",            1-0.8750),
        ("No-Solicit of Customers",        1-0.9643),
        ("No-Solicit of Employees",        1-0.9789),
        ("Non-Compete",                    1-0.9389),
        ("Non-Disparagement",              1-0.9000),
        ("Non-Transferable License",       1-0.8561),
        ("Notice Period to Terminate",     1-0.9640),
        ("Post-Termination Services",      1-0.9493),
        ("Price Restrictions",             1-1.0000),
        ("Renewal Term",                   1-0.9560),
        ("Revenue/Profit Sharing",         1-0.9483),
        ("ROFR / ROFO / ROFN",             1-0.8667),
        ("Source Code Escrow",             1-0.8136),
        ("Termination for Convenience",    1-0.9651),
        ("Third Party Beneficiary",        1-0.8824),
        ("Uncapped Liability",             1-0.5918),
        ("Unlimited License",              1-0.9783),
        ("Volume Restriction",             1-0.8354),
        ("Warranty Duration",              1-0.8406),
    ],
    "NDA Classification\n(ContractNLI)": [
        ("Confidentiality of Agreement",          1-0.9268),
        ("Explicit Identification",               1-0.8807),
        ("Inclusion of Verbal Information",       1-0.8832),
        ("Limited Use",                           1-0.9279),
        ("No Licensing",                          1-0.9259),
        ("Notice on Compelled Disclosure",        1-0.9859),
        ("Permissible Acquirement of Similar",    1-0.9663),
        ("Permissible Copy",                      1-0.9080),
        ("Permissible Dev. of Similar Info",      1-0.9559),
        ("Permissible Post-Agreement Possession", 1-0.9459),
        ("Return of Confidential Info",           1-0.8939),
        ("Sharing with Employees",                1-0.9647),
        ("Sharing with Third Parties",            1-0.9167),
        ("Survival of Obligations",               1-0.9363),
    ],
    "M&A Contract Analysis\n(MAUD)": [
        ("MAE Carveout Application",              1-0.4783),
        ("Fundamental R&W Bringdown Std",         1-0.2343),
        ("Capitalization R&W Bringdown Std",      1-0.0497),
        ("General R&W Bringdown Timing",          1-0.7182),
        ("Additional Matching Rights (COR)",      1-0.5316),
        ("Buyer Consent (Neg. Interim Cov.)",     1-0.1222),
        ("Buyer Consent (Ordinary Course)",       1-0.9116),
        ("Change in Law (Disp. Impact)",          1-0.8586),
        ("GAAP Changes (Disp. Impact)",           1-0.3980),
        ("COR - Intervening Event Response",      1-0.8700),
        ("COR - Fiduciary Determination Only",    1-0.1500),
        ("COR Standard (Intervening Event)",      1-0.2857),
        ("COR Standard (Superior Offer)",         1-0.3300),
        ("Knowledge Requirement in Definition",   1-0.4762),
        ("Definition Includes Asset Deals",       1-0.0753),
        ("Definition Includes Stock Deals",       1-0.0541),
        ("Fiduciary Exception Board Std",         1-0.1173),
        ("No-Shop Fiduciary Exception Trigger",   1-0.9218),
        ("Financial POV Sole Consideration",      1-0.8750),
        ("FLS (MAE) Standard",                    1-0.8182),
        ("General Econ. Cond. (Disp. Impact)",    1-0.1939),
        ("Incl. Consistent w/ Past Practice",     1-0.9282),
        ("Initial Matching Period (COR)",         1-0.6013),
        ("Initial Matching Period (FTR)",         1-0.7727),
        ("Intervening Event After Signing",       1-0.7279),
        ("Knowledge Definition",                  1-0.5629),
        ("Non-D&O No-Shop Breach Liability",      1-0.5000),
        ("Ordinary Course Efforts Standard",      1-0.6409),
        ("Pandemic (Disp. Impact Modifier)",      1-0.6020),
        ("Pandemic Gov. Response Reference",      1-0.8061),
        ("Relational Language (MAE) Applies To",  1-0.6889),
        ("Specific Performance",                  1-0.9045),
        ("Tail Period Length",                    1-0.1173),
        ("Type of Consideration",                 1-0.6570),
    ],
    "Legal Issue Classification\n(LearnedHands)": [
        ("Benefits & Social Services",  1-0.8254),
        ("Business",                    1-0.5747),
        ("Consumer",                    1-0.7541),
        ("Courts",                      1-0.5389),
        ("Crime",                       1-0.7544),
        ("Divorce",                     1-0.7651),
        ("Domestic Violence",           1-0.7126),
        ("Education",                   1-0.9107),
        ("Employment",                  1-0.8462),
        ("Estates",                     1-0.9379),
        ("Family",                      1-0.8980),
        ("Health",                      1-0.8363),
        ("Housing",                     1-0.9346),
        ("Immigration",                 1-0.9925),
        ("Torts",                       1-0.5949),
        ("Traffic",                     1-0.9730),
    ],
    "Privacy Policy Analysis\n(OPP115)": [
        ("Data Retention",              1-0.6477),
        ("Data Security",               1-0.8703),
        ("Do Not Track",                1-0.9636),
        ("First Party Collection/Use",  1-0.8029),
        ("Intl & Specific Audiences",   1-0.9143),
        ("Policy Change",               1-0.7912),
        ("Third Party Sharing",         1-0.7321),
        ("User Access / Edit / Delete", 1-0.8983),
        ("User Choice & Control",       1-0.8435),
    ],
    "Supply Chain Disclosure\n(Supply Chain)": [
        ("Accountability - Best Practice", 1-0.8179),
        ("Audits - Best Practice",         1-0.8338),
        ("Certification - Best Practice",  1-0.7302),
        ("Training - Best Practice",       1-0.8865),
        ("Verification - Best Practice",   1-0.7546),
        ("Accountability - Disclosed",     1-0.7354),
        ("Audits - Disclosed",             1-0.8443),
        ("Certification - Disclosed",      1-0.6323),
        ("Training - Disclosed",           1-0.8074),
        ("Verification - Disclosed",       1-0.7757),
    ],
    "Other Legal Tasks": [
        ("Trademark Classification (Abercrombie)", 1-0.8211),
        ("Tax Court Outcomes",                     1-0.9712),
        ("Citation Prediction (Classification)",   1-0.7130),
        ("Citation Prediction (Open)",             1-0.0189),
        ("Consumer Contracts QA",                  1-0.9747),
        ("Corporate Lobbying",                     1-0.7939),
        ("Definition Classification",              1-0.9499),
        ("Definition Extraction",                  1-0.8806),
        ("Function of Decision Section",           1-0.3106),
        ("Hearsay",                                1-0.7340),
        ("Insurance Policy Interpretation",        1-0.4286),
        ("International Citizenship Questions",    1-0.5517),
        ("J.Crew Blocker Provision",               1-0.9815),
        ("Legal Reasoning Causality",              1-0.8727),
        ("NY Judicial Ethics",                     1-0.7911),
        ("Oral Argument Question Purpose",         1-0.4423),
        ("Overruling",                             1-0.9307),
        ("Personal Jurisdiction",                  1-0.8000),
        ("Privacy Policy Entailment",              1-0.7259),
        ("Privacy Policy QA",                      1-0.6847),
        ("Private Right of Action (PROA)",         1-0.9474),
        ("Statutory Reasoning (SARA)",             1-0.8750),
        ("Case Holding Retrieval (SCALR)",         1-0.7354),
        ("Successor Liability",                    1-0.3151),
        ("Textualism - Dictionaries",              1-1.0000),
        ("Textualism - Plain Meaning",             1-0.8606),
        ("UCC vs Common Law",                      1-0.9574),
        ("Unfair Terms of Service",                1-0.8224),
        ("Telemarketing Sales Rule",               1-0.8298),
    ],
}

CATEGORY_COLORS = {
    "Contract Review\n(CUAD)":                    "#185FA5",
    "NDA Classification\n(ContractNLI)":          "#0F6E56",
    "M&A Contract Analysis\n(MAUD)":              "#993C1D",
    "Legal Issue Classification\n(LearnedHands)": "#534AB7",
    "Privacy Policy Analysis\n(OPP115)":          "#BA7517",
    "Supply Chain Disclosure\n(Supply Chain)":    "#3B6D11",
    "Other Legal Tasks":                          "#5F5E5A",
}

def risk_color(v):
    if v >= 0.40:  return "#E24B4A"
    if v >= 0.20:  return "#EF9F27"
    return "#639922"

# ─────────────────────────────────────────────────────────────
# Fig 1 · Overview – average error risk by category
# ─────────────────────────────────────────────────────────────
avgs = {cat: np.mean([v for _, v in items]) for cat, items in RAW.items()}
sorted_cats = sorted(avgs, key=lambda c: avgs[c], reverse=True)

fig1, ax1 = plt.subplots(figsize=(10, 5))
fig1.patch.set_facecolor('#FAFAFA')
ax1.set_facecolor('#FAFAFA')

cats_disp  = [c.replace('\n', ' ') for c in sorted_cats]
vals       = [avgs[c] * 100 for c in sorted_cats]
bar_colors = [risk_color(avgs[c]) for c in sorted_cats]

bars = ax1.barh(cats_disp, vals, color=bar_colors, height=0.55, zorder=3)
ax1.set_xlim(0, 65)
ax1.set_xlabel('Average Error Risk (%)', fontsize=11)
ax1.set_title('Average AI Error Risk by Legal Task Category\n(LegalBench · Llama-3.1-70B)', fontsize=13, fontweight='bold', pad=14)
ax1.tick_params(axis='y', labelsize=10)
ax1.tick_params(axis='x', labelsize=9)
ax1.xaxis.grid(True, linestyle='--', alpha=0.5, zorder=0)
ax1.set_axisbelow(True)

for bar, val in zip(bars, vals):
    ax1.text(bar.get_width() + 0.8, bar.get_y() + bar.get_height()/2,
             f'{val:.1f}%', va='center', fontsize=9, color='#444')

patches = [
    mpatches.Patch(color='#E24B4A', label='High Risk (>= 40%)'),
    mpatches.Patch(color='#EF9F27', label='Medium Risk (20-40%)'),
    mpatches.Patch(color='#639922', label='Low Risk (< 20%)'),
]
ax1.legend(handles=patches, loc='lower right', fontsize=9, framealpha=0.7)
ax1.text(0.99, -0.09, '* Error Risk = 1 - accuracy',
         transform=ax1.transAxes, ha='right', fontsize=8, color='#888')

plt.tight_layout()
fig1.savefig(out('01_overview_by_category.png'), dpi=150, bbox_inches='tight')
plt.close(fig1)
print("Saved: 01_overview_by_category.png")


# ─────────────────────────────────────────────────────────────
# Fig 2 · Detail subplots – all 7 categories, one chart each
# ─────────────────────────────────────────────────────────────
fig2 = plt.figure(figsize=(22, 46))
fig2.patch.set_facecolor('#FAFAFA')
gs = gridspec.GridSpec(4, 2, figure=fig2, hspace=0.45, wspace=0.35)

axes_positions = [(0,0),(0,1),(1,0),(1,1),(2,0),(2,1),(3,0)]
categories_list = list(RAW.keys())

for idx, (cat, pos) in enumerate(zip(categories_list, axes_positions)):
    ax = fig2.add_subplot(gs[pos])
    ax.set_facecolor('#FAFAFA')

    items  = sorted(RAW[cat], key=lambda x: x[1], reverse=True)
    labels = [lbl for lbl, _ in items]
    values = [v * 100 for _, v in items]
    colors = [risk_color(v/100) for v in values]

    ax.barh(labels, values, color=colors, height=0.65, zorder=3)
    ax.set_xlim(0, 110)
    ax.set_xlabel('Error Risk (%)', fontsize=9)
    title = cat.replace('\n', ' ')
    avg_v = np.mean([v for _, v in RAW[cat]]) * 100
    ax.set_title(f'{title}\n(avg {avg_v:.1f}%)', fontsize=10, fontweight='bold',
                 color=CATEGORY_COLORS[cat], pad=6)
    ax.tick_params(axis='y', labelsize=7.5)
    ax.tick_params(axis='x', labelsize=8)
    ax.xaxis.grid(True, linestyle='--', alpha=0.4, zorder=0)
    ax.set_axisbelow(True)

    for i, (val, lbl) in enumerate(zip(values, labels)):
        ax.text(val + 0.5, i, f'{val:.1f}%', va='center', fontsize=7, color='#444')

    for thresh, lc in [(20, '#639922'), (40, '#E24B4A')]:
        ax.axvline(thresh, color=lc, lw=0.8, ls='--', alpha=0.6, zorder=2)

fig2.add_subplot(gs[3,1]).set_visible(False)

fig2.suptitle('LegalBench: Detailed AI Error Risk by Legal Task Category',
              fontsize=15, fontweight='bold', y=1.002)
fig2.text(0.5, -0.002,
          'Error Risk = 1 - accuracy  |  Reference model: Meta-Llama-3.1-70B-Instruct-Turbo  |  Source: LegalEvalHub',
          ha='center', fontsize=9, color='#888')

plt.savefig(out('02_detail_all_categories.png'), dpi=150, bbox_inches='tight')
plt.close(fig2)
print("Saved: 02_detail_all_categories.png")


# ─────────────────────────────────────────────────────────────
# Fig 3 · Scatter – individual tasks coloured by category
# ─────────────────────────────────────────────────────────────
fig3, ax3 = plt.subplots(figsize=(13, 8))
fig3.patch.set_facecolor('#FAFAFA')
ax3.set_facecolor('#FAFAFA')

all_pts = []
for cat, items in RAW.items():
    col = CATEGORY_COLORS[cat]
    for lbl, v in items:
        all_pts.append((v * 100, col, cat.replace('\n', ' ')))

all_pts.sort(key=lambda x: x[0])
xs = list(range(len(all_pts)))
ys = [p[0] for p in all_pts]
cs = [p[1] for p in all_pts]

ax3.scatter(xs, ys, c=cs, s=55, zorder=3, alpha=0.85)
ax3.axhline(40, color='#E24B4A', lw=1, ls='--', alpha=0.7, label='High Risk Threshold (40%)')
ax3.axhline(20, color='#EF9F27', lw=1, ls='--', alpha=0.7, label='Medium Risk Threshold (20%)')
ax3.fill_between([-1, len(xs)], 40, 100, color='#E24B4A', alpha=0.05)
ax3.fill_between([-1, len(xs)], 20,  40, color='#EF9F27', alpha=0.05)
ax3.fill_between([-1, len(xs)],  0,  20, color='#639922', alpha=0.05)

ax3.set_xlim(-2, len(xs)+1)
ax3.set_ylim(-3, 105)
ax3.set_xlabel('Tasks (sorted by error risk ascending)', fontsize=11)
ax3.set_ylabel('Error Risk (%)', fontsize=11)
ax3.set_title('Error Risk Distribution Across All LegalBench Tasks\n(161 tasks, colored by category)',
              fontsize=13, fontweight='bold', pad=14)
ax3.set_xticks([])
ax3.xaxis.grid(False)
ax3.yaxis.grid(True, linestyle='--', alpha=0.4, zorder=0)
ax3.set_axisbelow(True)

legend_patches = [mpatches.Patch(color=c, label=cat.replace('\n', ' '))
                  for cat, c in CATEGORY_COLORS.items()]
legend_patches += [
    mpatches.Patch(color='white', label=''),
    mpatches.Patch(color='#E24B4A', alpha=0.6, label='High Risk (>=40%)'),
    mpatches.Patch(color='#EF9F27', alpha=0.6, label='Medium Risk (20-40%)'),
    mpatches.Patch(color='#639922', alpha=0.6, label='Low Risk (<20%)'),
]
ax3.legend(handles=legend_patches, loc='upper left', fontsize=8.5, framealpha=0.8, ncol=2)
ax3.text(0.99, -0.08, '* Reference model: Meta-Llama-3.1-70B-Instruct-Turbo  |  Source: LegalEvalHub',
         transform=ax3.transAxes, ha='right', fontsize=8, color='#888')

plt.tight_layout()
fig3.savefig(out('03_scatter_all_tasks.png'), dpi=150, bbox_inches='tight')
plt.close(fig3)
print("Saved: 03_scatter_all_tasks.png")

print("\nDone! 3 files saved.")
