import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import matplotlib.font_manager as fm
import numpy as np
import os

# ── 한글 폰트 설정 ──────────────────────────────────────────
fm.fontManager.__init__()
plt.rcParams['font.family'] = 'NanumGothic'
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['axes.spines.top']   = False
plt.rcParams['axes.spines.right'] = False

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)
def out(f): return os.path.join(OUTPUT_DIR, f)

# ─────────────────────────────────────────────────────────────
# 실제 데이터 (damiencharlotin.com/hallucinations 실시간 집계)
# 총 1,174건
# ─────────────────────────────────────────────────────────────

# ── 피해 유형 (Nature – Category) ────────────────────────────
harm_labels  = ["Fabricated\n(가짜 판례·인용)", "Misrepresented\n(내용 왜곡)", "False Quotes\n(허위 인용구)", "Outdated Advice\n(폐지·번복 법령)"]
harm_values  = [978, 478, 309, 27]
harm_colors  = ["#E24B4A", "#EF9F27", "#534AB7", "#5F5E5A"]
harm_total   = sum(harm_values)  # 1,792  (중복 포함; 건당 복수 유형 가능)
# 실제 케이스 수 기준으로 재계산
harm_pct     = [v / harm_total * 100 for v in harm_values]

# ── 당사자 유형 (Party) ─────────────────────────────────────
# Pro Se Litigant: 696, Lawyer: 447, Judge: 16, Expert: 10,
# Prosecutor: 4, Paralegal: 2, Federal Defender: 1, Arbitrator: 1
# → AI 주도 오류 vs 전문직 과실 구분
#   전문직: Lawyer 447 + Paralegal 2 + Prosecutor 4 + Federal Defender 1 = 454
#   비전문가 자기대리: Pro Se Litigant 696
#   사법·전문가: Judge 16 + Expert 10 + Arbitrator 1 = 27
TOTAL_CASES  = 1177  # 당사자 합계 (696+447+16+10+4+2+1+1)

fault_labels = ["Pro Se Litigant\n(비전문 자기대리)\n59.1%",
                "전문 법조인\n(변호사·검사 등)\n38.6%",
                "판사·전문가·중재인\n2.3%"]
fault_values = [696, 454, 27]
fault_pcts   = [v / TOTAL_CASES * 100 for v in fault_values]
fault_colors = ["#185FA5", "#E24B4A", "#5F5E5A"]

party_detail_labels = ["Pro Se Litigant\n(비전문 자기대리)",
                        "Lawyer (변호사)",
                        "Judge (판사)",
                        "Expert (전문가)",
                        "Prosecutor (검사)",
                        "Paralegal",
                        "Federal Defender",
                        "Arbitrator (중재인)"]
party_detail_values = [696, 447, 16, 10, 4, 2, 1, 1]
party_detail_colors = ["#185FA5","#E24B4A","#BA7517","#0F6E56",
                        "#993C1D","#534AB7","#5F5E5A","#639922"]


# =============================================================
# FIGURE 1 – 피해 유형별 비율  (도넛 + 가로 막대)
# =============================================================
fig1, (ax_donut, ax_bar) = plt.subplots(
    1, 2, figsize=(14, 6), gridspec_kw={"width_ratios": [1, 1.4]})
fig1.patch.set_facecolor('#FAFAFA')

# 도넛
wedges, _, autotexts = ax_donut.pie(
    harm_values, labels=None, colors=harm_colors,
    autopct=lambda p: f'{p:.1f}%',
    pctdistance=0.74, startangle=140,
    wedgeprops=dict(width=0.52, edgecolor='white', linewidth=2),
)
for at in autotexts:
    at.set_fontsize(10); at.set_fontweight('bold'); at.set_color('white')

ax_donut.text(0, 0.10, f'{harm_total:,}', ha='center', va='center',
              fontsize=22, fontweight='bold', color='#2C2C2A')
ax_donut.text(0, -0.16, '(유형 건수 합계)', ha='center', va='center',
              fontsize=9, color='#888')

lg_patches = [
    mpatches.Patch(color=c, label=f'{l.replace(chr(10), " ")}  ({v:,}건, {v/harm_total*100:.1f}%)')
    for c, l, v in zip(harm_colors, harm_labels, harm_values)
]
ax_donut.legend(handles=lg_patches, loc='lower center',
                bbox_to_anchor=(0.5, -0.24), fontsize=9, framealpha=0.8, ncol=2)
ax_donut.set_title('피해 유형별 비율\n(Hallucination Harm Type)', fontsize=13, fontweight='bold', pad=14)

# 가로 막대
ax_bar.set_facecolor('#FAFAFA')
sidx = np.argsort(harm_values)
sl = [harm_labels[i].replace('\n', ' ') for i in sidx]
sv = [harm_values[i] for i in sidx]
sc = [harm_colors[i] for i in sidx]
bars = ax_bar.barh(sl, sv, color=sc, height=0.55, zorder=3)
ax_bar.set_xlabel('케이스 수 (건)', fontsize=10)
ax_bar.set_title('할루시네이션 유형별 케이스 수', fontsize=13, fontweight='bold', pad=14)
ax_bar.xaxis.grid(True, linestyle='--', alpha=0.4, zorder=0)
ax_bar.set_axisbelow(True)
ax_bar.tick_params(axis='y', labelsize=9)
for bar, val in zip(bars, sv):
    ax_bar.text(bar.get_width() + 8, bar.get_y() + bar.get_height()/2,
                f'{val:,}건 ({val/harm_total*100:.1f}%)',
                va='center', fontsize=9, color='#444')
ax_bar.set_xlim(0, max(sv) * 1.30)

fig1.text(0.5, -0.03,
          '출처: Damien Charlotin AI Hallucination Cases DB (damiencharlotin.com/hallucinations)  |  n=1,174건',
          ha='center', fontsize=8, color='#888')
plt.tight_layout()
fig1.savefig(out('07_harm_type_ratio.png'), dpi=150, bbox_inches='tight')
plt.close(fig1)
print("Saved: 07_harm_type_ratio.png")


# =============================================================
# FIGURE 2 – AI 주도 vs 전문직 과실 vs 비전문가
# =============================================================
fig2 = plt.figure(figsize=(16, 6))
fig2.patch.set_facecolor('#FAFAFA')
gs = gridspec.GridSpec(1, 3, figure=fig2, wspace=0.42)

# ── 패널 A: 당사자 유형 도넛 ──
ax_a = fig2.add_subplot(gs[0])
wedges2, _, at2 = ax_a.pie(
    fault_values, labels=None, colors=fault_colors,
    autopct=lambda p: f'{p:.1f}%',
    pctdistance=0.72, startangle=90,
    wedgeprops=dict(width=0.52, edgecolor='white', linewidth=2),
)
for at in at2:
    at.set_fontsize(10); at.set_fontweight('bold'); at.set_color('white')
ax_a.text(0, 0.10, f'{TOTAL_CASES:,}', ha='center', va='center',
          fontsize=20, fontweight='bold', color='#2C2C2A')
ax_a.text(0, -0.14, '총 케이스', ha='center', va='center',
          fontsize=9, color='#888')
lg_f = [mpatches.Patch(color=c, label=l.replace('\n', ' '))
        for c, l in zip(fault_colors, fault_labels)]
ax_a.legend(handles=lg_f, loc='lower center', bbox_to_anchor=(0.5, -0.26),
            fontsize=8.5, framealpha=0.8, ncol=1)
ax_a.set_title('당사자 유형 비율\n(Party Type)', fontsize=11, fontweight='bold', pad=10)

# ── 패널 B: 당사자 상세 가로 막대 ──
ax_b = fig2.add_subplot(gs[1])
ax_b.set_facecolor('#FAFAFA')
b_sidx = np.argsort(party_detail_values)
bl = [party_detail_labels[i].replace('\n', ' ') for i in b_sidx]
bv = [party_detail_values[i] for i in b_sidx]
bc = [party_detail_colors[i] for i in b_sidx]
bars2 = ax_b.barh(bl, bv, color=bc, height=0.6, zorder=3)
ax_b.set_xlabel('케이스 수 (건)', fontsize=10)
ax_b.set_title('당사자별 케이스 수\n(Cases by Party)', fontsize=11, fontweight='bold', pad=10)
ax_b.xaxis.grid(True, linestyle='--', alpha=0.4, zorder=0)
ax_b.set_axisbelow(True)
ax_b.tick_params(axis='y', labelsize=8)
for bar, val in zip(bars2, bv):
    ax_b.text(bar.get_width() + 5, bar.get_y() + bar.get_height()/2,
              f'{val:,}건 ({val/TOTAL_CASES*100:.1f}%)',
              va='center', fontsize=8, color='#444')
ax_b.set_xlim(0, max(bv) * 1.38)

# ── 패널 C: 책임 주체 스택 막대 ──
ax_c = fig2.add_subplot(gs[2])
ax_c.set_facecolor('#FAFAFA')
fault_short = ["Pro Se (비전문 자기대리)", "전문 법조인 (변호사 등)", "판사·전문가·중재인"]
left = 0
for v, c, lbl in zip(fault_pcts, fault_colors, fault_short):
    ax_c.barh(["책임 주체 분류"], [v], left=[left],
              color=c, height=0.45, label=lbl, zorder=3)
    ax_c.text(left + v/2, 0, f'{v:.1f}%',
              ha='center', va='center',
              fontsize=10, fontweight='bold', color='white')
    left += v

ax_c.set_xlim(0, 102)
ax_c.set_xlabel('비율 (%)', fontsize=10)
ax_c.set_title('AI 주도 오류 vs 전문직 과실\n(AI-Led vs Professional Fault)',
               fontsize=11, fontweight='bold', pad=10)
ax_c.set_yticks([])
ax_c.xaxis.grid(True, linestyle='--', alpha=0.4, zorder=0)
ax_c.set_axisbelow(True)
ax_c.legend(loc='lower center', bbox_to_anchor=(0.5, -0.32),
            fontsize=8.5, framealpha=0.8, ncol=1)

fig2.text(0.5, -0.05,
          '출처: Damien Charlotin AI Hallucination Cases DB (damiencharlotin.com/hallucinations)  |  n=1,174건',
          ha='center', fontsize=8, color='#888')
plt.tight_layout()
fig2.savefig(out('08_ai_led_vs_professional_fault.png'), dpi=150, bbox_inches='tight')
plt.close(fig2)
print("Saved: 08_ai_led_vs_professional_fault.png")


# =============================================================
# FIGURE 3 – 슬라이드용 통합 1장 (도넛 2개 나란히)
# =============================================================
fig3, (ax_L, ax_R) = plt.subplots(1, 2, figsize=(16, 7))
fig3.patch.set_facecolor('#FAFAFA')

# 왼쪽: 피해 유형
wL, _, atL = ax_L.pie(
    harm_values, labels=None, colors=harm_colors,
    autopct=lambda p: f'{p:.1f}%',
    pctdistance=0.74, startangle=140,
    wedgeprops=dict(width=0.52, edgecolor='white', linewidth=2),
)
for at in atL:
    at.set_fontsize(11); at.set_fontweight('bold'); at.set_color('white')
ax_L.text(0, 0.10, f'{harm_total:,}', ha='center', va='center',
          fontsize=22, fontweight='bold', color='#2C2C2A')
ax_L.text(0, -0.14, '유형 건수 합계', ha='center', va='center',
          fontsize=9, color='#888')
lgL = [mpatches.Patch(color=c,
       label=f'{l.replace(chr(10)," ")}  ({v:,}건, {v/harm_total*100:.1f}%)')
       for c, l, v in zip(harm_colors, harm_labels, harm_values)]
ax_L.legend(handles=lgL, loc='lower center', bbox_to_anchor=(0.5, -0.24),
            fontsize=9.5, framealpha=0.8, ncol=2)
ax_L.set_title('피해 유형별 비율\n(Hallucination Harm Type Ratio)',
               fontsize=13, fontweight='bold', pad=16)

# 오른쪽: 당사자 유형
wR, _, atR = ax_R.pie(
    fault_values, labels=None, colors=fault_colors,
    autopct=lambda p: f'{p:.1f}%',
    pctdistance=0.72, startangle=90,
    wedgeprops=dict(width=0.52, edgecolor='white', linewidth=2),
)
for at in atR:
    at.set_fontsize(11); at.set_fontweight('bold'); at.set_color('white')
ax_R.text(0, 0.10, f'{TOTAL_CASES:,}', ha='center', va='center',
          fontsize=22, fontweight='bold', color='#2C2C2A')
ax_R.text(0, -0.14, '총 케이스', ha='center', va='center',
          fontsize=9, color='#888')
lgR = [mpatches.Patch(color=c,
       label=f'{l.replace(chr(10)," ")}  ({v:,}건, {v/TOTAL_CASES*100:.1f}%)')
       for c, l, v in zip(fault_colors, fault_labels, fault_values)]
ax_R.legend(handles=lgR, loc='lower center', bbox_to_anchor=(0.5, -0.24),
            fontsize=9.5, framealpha=0.8, ncol=1)
ax_R.set_title('AI 주도 오류 vs 전문직 과실\n(AI-Led Error vs Professional Fault)',
               fontsize=13, fontweight='bold', pad=16)

fig3.suptitle('Damien Charlotin AI 할루시네이션 판례 DB  (n = 1,174건)',
              fontsize=15, fontweight='bold', y=1.02)
fig3.text(0.5, -0.03,
          '출처: damiencharlotin.com/hallucinations',
          ha='center', fontsize=9, color='#888')
plt.tight_layout()
fig3.savefig(out('09_combined_harm_and_fault.png'), dpi=150, bbox_inches='tight')
plt.close(fig3)
print("Saved: 09_combined_harm_and_fault.png")
print("\nDone!")
