#!/usr/bin/env python3
"""
AI 전문직 보험료 산정 프로그램
2025년 표준형 (보상한도 1억/1억, 자기부담금 500만원) 기준
"""

import os
import sys
from typing import Optional

# ───────────────────────────────────────────────
# ANSI 색상 (터미널 출력용)
# ───────────────────────────────────────────────
class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    DIM    = "\033[2m"
    BLUE   = "\033[94m"
    CYAN   = "\033[96m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    PURPLE = "\033[95m"
    WHITE  = "\033[97m"
    BG_DARK = "\033[40m"

def b(text):  return f"{C.BOLD}{text}{C.RESET}"
def c(text):  return f"{C.CYAN}{text}{C.RESET}"
def g(text):  return f"{C.GREEN}{text}{C.RESET}"
def y(text):  return f"{C.YELLOW}{text}{C.RESET}"
def r(text):  return f"{C.RED}{text}{C.RESET}"
def p(text):  return f"{C.PURPLE}{text}{C.RESET}"
def d(text):  return f"{C.DIM}{text}{C.RESET}"

def clear():
    os.system("clear" if os.name != "nt" else "cls")

def hr(char="─", width=58, color=C.DIM):
    print(f"{color}{char * width}{C.RESET}")

def header(title: str):
    clear()
    hr("═", 58, C.BLUE)
    print(f"{C.BLUE}{C.BOLD}  AI 전문직 배상책임보험 — 보험료 산정 시스템{C.RESET}")
    print(f"{C.DIM}  2025년 표준형 (보상한도 1억/1억 | 자기부담금 500만원){C.RESET}")
    hr("═", 58, C.BLUE)
    print(f"\n{C.BOLD}{C.WHITE}  {title}{C.RESET}\n")


# ───────────────────────────────────────────────
# 데이터 테이블
# ───────────────────────────────────────────────
BASE_PREMIUM_TABLE = {
    "1": ("1억 이하",   215_200),
    "2": ("1.5억 이하", 241_700),
    "3": ("2억 이하",   248_300),
    "4": ("3억 이하",   284_200),
    "5": ("4억 이하",   346_800),
    "6": ("5억 이하",   391_300),
    "7": ("5억 초과",   555_900),
}

JOB_WEIGHTS = {
    "1": ("변호사", 1.30),
    "2": ("변리사", 1.20),
    "3": ("법무사", 1.10),
    "4": ("기타",   1.00),
}

TASK_WEIGHTS = {
    "1": ("판례·법령 검색 후 소장·준비서면에 직접 인용", 1.21),
    "2": ("법률의견서 작성",                              1.37),
    "3": ("계약서 조항 작성",                             0.92),
    "4": ("계약서 검토 및 리스크 포인트 추출",            0.92),
    "5": ("판례·판결문 요약 및 리서치",                   0.81),
    "6": ("문서 초안 작성 (전면 재검토 전제)",            0.81),
    "7": ("의뢰인 상담 내용 정리",                        0.6),
    "8": ("자료 정리·번역·기일 관리",                     0.5),
}

AI_RISK = {
    "1": ("L1 — 저위험 +0%",  0.00, "내부 리서치·단순 번역·기일 관리 등"),
    "2": ("L2 — 중위험 +10%", 0.10, "의뢰인 전달 레포트·법률의견서 초안 등"),
    "3": ("L3 — 고위험 +20%", 0.20, "소장 내 판례 인용·특허 청구범위·법원 제출 증거 등"),
}

SKILL_DISCOUNT = {
    "1": ("1~2년",    0.00),
    "2": ("3~4년",    0.10),
    "3": ("5~9년",    0.15),
    "4": ("10~14년",  0.20),
    "5": ("15년 이상", 0.30),
}

ML_FEATURES = {
    "history": {
        "label": "과거 클레임 이력 (가중치 30%)",
        "options": [
            ("무사고",           0.00),
            ("부분 보상 이력",   0.15),
            ("면책(C구간) 이력", 0.30),
        ],
    },
    "comply": {
        "label": "준칙 준수율 (가중치 20%)",
        "options": [
            ("90% 이상",  0.00),
            ("70~90%",    0.10),
            ("70% 미만",  0.20),
        ],
    },
    "model": {
        "label": "사용 AI 모델 (가중치 15%)",
        "options": [
            ("LegalBench 고득점 모델", 0.00),
            ("범용 유료 모델",         0.08),
            ("무료·저성능 모델",       0.15),
        ],
    },
    "duty": {
        "label": "고위험 업무 비중 (가중치 15%)",
        "options": [
            ("30% 미만",  0.00),
            ("30~60%",    0.08),
            ("60% 초과",  0.15),
        ],
    },
    "skill": {
        "label": "전문 경력·AI 숙련도 (가중치 10%)",
        "options": [
            ("AI 3년 이상 숙련", 0.00),
            ("1~3년",            0.05),
            ("1년 미만",         0.10),
        ],
    },
    "freq": {
        "label": "월평균 AI 사용 빈도 (가중치 10%)",
        "options": [
            ("적정 (검토 충분)",   0.00),
            ("고빈도 (검토 부족)", 0.05),
            ("초고빈도 (무분별)", 0.10),
        ],
    },
    "case": {
        "label": "사건 난이도",
        "options": [
            ("일반 업무 (민형사 등)          +0%",  0.00),
            ("전문 업무 (의료·지식재산권 등) +15%", 0.15),
        ],
    },
    "dmg": {
        "label": "피해 예상액",
        "options": [
            ("5,000만 원 미만  +0%",  0.00),
            ("5,000만~1억 원  +10%",  0.10),
            ("1억 원 초과     +20%",  0.20),
        ],
    },
    "org": {
        "label": "관리 조직 규모",
        "options": [
            ("1인 단독    ±0%",  0.00),
            ("2~4인       -5%", -0.05),
            ("5~10인     -10%", -0.10),
        ],
    },
    "cert": {
        "label": "AI 솔루션 인증",
        "options": [
            ("미인증  ±0%",       0.00),
            ("인증 모델 사용 -5%", -0.05),
        ],
    },
}


# ───────────────────────────────────────────────
# 입력 유틸
# ───────────────────────────────────────────────
def prompt(text: str, valid: list[str]) -> str:
    while True:
        val = input(f"  {c('▶')} {text}: ").strip()
        if val in valid:
            return val
        print(f"  {r('✗')} {d(f'유효한 값을 입력하세요: {valid}')}")

def choose(options: dict, title: str, multi: bool = False):
    """
    options: {key: (label, value, ...)} 형태
    multi=True 이면 쉼표 구분 복수 선택 허용
    """
    print(f"  {d('┌' + '─'*46)}")
    for k, v in options.items():
        label = v[0]
        extra = f"  {d(v[2])}" if len(v) > 2 else ""
        print(f"  {d('│')}  {b(k)}.  {label}{extra}")
    print(f"  {d('└' + '─'*46)}")

    if multi:
        while True:
            raw = input(f"  {c('▶')} 번호를 쉼표로 구분 입력 (예: 1,3,5): ").strip()
            keys = [k.strip() for k in raw.split(",")]
            if all(k in options for k in keys) and len(keys) >= 1:
                return keys
            print(f"  {r('✗')} {d(f'유효한 번호를 입력하세요: {list(options.keys())}')}")
    else:
        return prompt(f"번호 선택 ({'/'.join(options.keys())})", list(options.keys()))


# ───────────────────────────────────────────────
# 핵심 계산 로직
# ───────────────────────────────────────────────
def compute_task_weight(selected_keys: list[str]) -> dict:
    weights = [TASK_WEIGHTS[k][1] for k in selected_keys]
    avg = sum(weights) / len(weights)
    high_cnt = sum(1 for w in weights if w >= 1.0)
    ratio = high_cnt / len(weights)
    if ratio > 0.7:
        corr, corr_label = 1.2, "×1.2  고위험 집중 (70% 초과)"
    elif ratio >= 0.4:
        corr, corr_label = 1.0, "×1.0  보정 없음 (40~70%)"
    else:
        corr, corr_label = 0.9, "×0.9  저위험 집중 (40% 미만)"
    return {
        "avg": avg, "ratio": ratio,
        "corr": corr, "corr_label": corr_label,
        "final": round(avg * corr, 4),
    }

def calculate_premium(inputs: dict) -> dict:
    base        = inputs["base"]
    job_w       = inputs["job_w"]
    task        = compute_task_weight(inputs["task_keys"])
    ai_sur      = inputs["ai_sur"]
    skill_disc  = inputs["skill_disc"]
    freq_sur    = 0.10 if inputs["under_inv"] else 0.00

    raw = base * job_w * task["final"] * (1 + ai_sur) * (1 - skill_disc) * (1 + freq_sur)
    rounded = round(raw / 100) * 100

    return {
        "base": base, "job_w": job_w,
        "task": task,
        "ai_sur": ai_sur, "skill_disc": skill_disc, "freq_sur": freq_sur,
        "raw": raw, "final": rounded,
    }

def calculate_renewal(base: int, ml_vals: dict) -> dict:
    mult = 1.0 + sum(ml_vals.values())
    premium = round(base * mult / 100) * 100
    return {"mult": mult, "premium": premium}


# ───────────────────────────────────────────────
# STEP 1 — 인수심사 (초기 보험료)
# ───────────────────────────────────────────────
def step_underwrite() -> dict:
    header("STEP 1 / 3  —  인수심사  ·  초기 보험료 산출")

    # 연매출 구간
    print(b("① 연매출 구간 선택") + d("  (전년도 기준)"))
    print()
    for k, (label, price) in BASE_PREMIUM_TABLE.items():
        print(f"  {b(k)}.  {label:<12}  {d('기준보험료')} {g(f'₩{price:,}')}")
    print()
    rev_key = prompt("번호 선택 (1~7)", list(BASE_PREMIUM_TABLE.keys()))
    rev_label, base = BASE_PREMIUM_TABLE[rev_key]

    print()
    print(f"  {g('✓')} 기준보험료 {b(f'₩{base:,}')} 설정 완료\n")

    # 직군
    hr()
    print(b("② 직군 선택"))
    print()
    job_key = choose(JOB_WEIGHTS, "직군")
    job_name, job_w = JOB_WEIGHTS[job_key]

    # AI 활용 업무
    print()
    hr()
    print(b("③ AI 활용 업무 선택") + d("  (복수 선택 가능, 쉼표로 구분)"))
    print()
    task_keys = choose(TASK_WEIGHTS, "업무", multi=True)
    task_names = [TASK_WEIGHTS[k][0] for k in task_keys]

    # AI 리스크 등급
    print()
    hr()
    print(b("④ AI 리스크 등급"))
    print()
    ai_key = choose(AI_RISK, "리스크 등급")
    ai_label, ai_sur, ai_desc = AI_RISK[ai_key]

    # 숙련도 할인
    print()
    hr()
    print(b("⑤ 무사고 가입기간 (숙련도 할인)"))
    print()
    skill_key = choose(SKILL_DISCOUNT, "가입기간")
    skill_label, skill_disc = SKILL_DISCOUNT[skill_key]

    # 사고 조사
    print()
    hr()
    print(b("⑥ 사고 조사 진행 중 여부"))
    print()
    print(f"  {b('1')}.  해당 없음")
    print(f"  {b('2')}.  진행 중  {d('+10% 할증')}")
    print()
    under_key = prompt("번호 선택 (1/2)", ["1", "2"])
    under_inv = under_key == "2"

    return {
        "rev_label": rev_label,
        "base": base,
        "job_name": job_name, "job_w": job_w,
        "task_keys": task_keys, "task_names": task_names,
        "ai_label": ai_label, "ai_sur": ai_sur,
        "skill_label": skill_label, "skill_disc": skill_disc,
        "under_inv": under_inv,
    }


# ───────────────────────────────────────────────
# STEP 2 — 클레임 심사 시뮬레이션
# ───────────────────────────────────────────────
def step_claim():
    header("STEP 2 / 3  —  클레임 심사  ·  보상 판정 시뮬레이션")

    # 트랙
    print(b("① 로그 트랙 선택"))
    print()
    print(f"  {b('1')}.  트랙 A — 브라우저 확장 프로그램 (WORM 자동 로그)")
    print(f"         {d('AI 감사 48h · 전액/부분/면책 전체 적용 · 보험료 할인')}")
    print(f"  {b('2')}.  트랙 B — 가입자 자체 제출")
    print(f"         {d('로그 신뢰도 낮음 · 전액 보상 불가 · 보상 상한선 낮음')}")
    print()
    track = prompt("번호 선택 (1/2)", ["1", "2"])
    track_label = "트랙 A" if track == "1" else "트랙 B"

    # 준칙 준수
    print()
    hr()
    print(b("② AI 사용 준칙 준수 여부"))
    print()
    complies = {}
    checks = [
        ("log",    "AI 출력 원본 저장 여부"),
        ("review", "1차 검토 기록 보존 여부"),
        ("cross",  "판례·법령 원문 교차 확인 여부"),
    ]
    for key, label in checks:
        print(f"  {label}")
        val = prompt("준수(y) / 미준수(n)", ["y", "n"])
        complies[key] = val == "y"
        print()

    # 오류 위치 (트랙 A만)
    err_loc = None
    if track == "1":
        hr()
        print(b("③ NLP Diff 분석 — 오류 발생 구간 (트랙 A 전용)"))
        print()
        print(f"  {b('1')}.  AI 유지 구간      {d('AI 원본 출력이 수정 없이 그대로 유지된 부분')}")
        print(f"  {b('2')}.  복수 구간 혼합    {d('AI + 전문직 수정 구간에 걸쳐 오류 발생')}")
        print(f"  {b('3')}.  전문직 수정 구간  {d('전문직이 수정·추가한 부분에서 오류 발생')}")
        print()
        err_key = prompt("번호 선택 (1/2/3)", ["1", "2", "3"])
        err_loc = {"1": "AI", "2": "mixed", "3": "human"}[err_key]

    # 판정
    all_ok  = all(complies.values())
    any_no  = not all_ok
    all_no  = not any(complies.values())

    if track == "1":
        if all_no or err_loc == "human":
            verdict, color = "면책", r
            reason = "전문직 수정 구간 오류 또는 준칙 전부 미준수"
        elif err_loc == "AI" and all_ok:
            verdict, color = "전액 보상", g
            reason = "AI 유지 구간 오류 + 준칙 전부 준수"
        else:
            verdict, color = "부분 보상", y
            reason = "혼합 과실 또는 준칙 일부 위반"
        process = "AI 자동 감사 → 48시간 내 1차 판정"
    else:
        if all_no:
            verdict, color = "면책", r
            reason = "로그 미제출 또는 전면 불충분"
        elif all_ok:
            verdict, color = "부분 보상 (상한)", y
            reason = "준칙 전부 준수 입증 — 보상 상한선 내, 전액 불가"
        else:
            verdict, color = "감액", y
            reason = "준칙 일부 위반 또는 입증 불충분"
        process = "인간 심사관 → 5영업일 내 판정"

    # 결과 출력
    print()
    hr("═", 58, C.BLUE)
    print(f"\n  {b('판정 결과')}  →  {color(b(verdict))}\n")
    print(f"  {d('사유')}    :  {reason}")
    print(f"  {d('심사 방식')}:  {process}")
    print(f"  {d('트랙')}    :  {track_label}")
    comply_str = "전부 준수" if all_ok else ("전부 미준수" if all_no else "일부 위반")
    print(f"  {d('준칙 준수')}:  {comply_str}")
    if err_loc:
        err_str = {"AI": "AI 유지 구간", "mixed": "복수 구간 혼합", "human": "전문직 수정 구간"}[err_loc]
        print(f"  {d('오류 구간')}:  {err_str}")
    print()

    input(f"  {d('Enter를 눌러 다음 단계로 진행...')}")


# ───────────────────────────────────────────────
# STEP 3 — 갱신 요율 (ML)
# ───────────────────────────────────────────────
def step_renewal(base: int) -> dict:
    header("STEP 3 / 3  —  갱신 요율  ·  ML 피처 기반 보험료 산출")
    print(f"  {d('기준보험료 (① 탭 연동)')}  {g(f'₩{base:,}')}\n")

    ml_vals = {}

    feature_order = ["history","comply","model","duty","skill","freq","case","dmg","org","cert"]
    separators = {
        "history": "ML 피처 — 리스크 변수 (합산 가중치 100%)",
        "case":    "업무 요소 — 추가 조정",
    }

    for key in feature_order:
        feat = ML_FEATURES[key]
        if key in separators:
            print()
            hr()
            print(b(separators[key]))
            print()

        print(f"  {b(feat['label'])}")
        for i, (label, val) in enumerate(feat["options"], 1):
            sign = f"+{int(val*100)}%" if val > 0 else (f"{int(val*100)}%" if val < 0 else "±0%")
            print(f"    {b(str(i))}.  {label:<42}  {d(sign)}")
        valid = [str(i) for i in range(1, len(feat["options"]) + 1)]
        sel = prompt("번호 선택", valid)
        ml_vals[key] = feat["options"][int(sel)-1][1]
        print()

    return ml_vals


# ───────────────────────────────────────────────
# 결과 출력
# ───────────────────────────────────────────────
def print_underwrite_result(inputs: dict, result: dict):
    header("보험료 산출 결과")

    hr("═", 58, C.BLUE)
    print(f"\n  {b('[ 입력 정보 ]')}\n")
    print(f"  {d('연매출 구간')}  :  {inputs['rev_label']}")
    print(f"  {d('직군')}        :  {inputs['job_name']}")
    print(f"  {d('AI 리스크')}   :  {inputs['ai_label']}")
    print(f"  {d('무사고기간')}  :  {inputs['skill_label']}")
    print(f"  {d('사고조사중')}  :  {'예 (+10%)' if inputs['under_inv'] else '아니오'}")
    print(f"\n  {d('선택 업무')}  :")
    for name in inputs['task_names']:
        print(f"    {d('·')}  {name}")

    print()
    hr()
    print(f"\n  {b('[ 단계별 계산 ]')}\n")

    tw = result["task"]
    steps = [
        ("① 기준보험료",         f"₩{result['base']:,}",                      g),
        ("② 직군 가중치",         f"×{result['job_w']}",                       c),
        ("③ 업무 가중치 (평균)",  f"×{tw['avg']:.4f}  ({len(inputs['task_keys'])}개 선택)", c),
        ("   집중도 보정",         tw['corr_label'],                             d),
        ("   최종 업무 가중치",   f"×{tw['final']}",                            c),
        ("④ AI 리스크 할증",      f"+{int(result['ai_sur']*100)}%",             y),
        ("⑤ 숙련도 할인",         f"-{int(result['skill_disc']*100)}%",         g),
        ("⑥ 빈도 할증",           f"+{int(result['freq_sur']*100)}%",           y),
    ]
    for label, val, col in steps:
        print(f"  {d(label):<30}  {col(val)}")

    print()
    hr("═", 58, C.GREEN)
    final_str = f"₩{result['final']:,}"
    print(f"\n  {b('최종 연간 보험료')}  →  {g(b(final_str))}")
    print(f"  {d('(100원 단위 반올림 적용)')}")
    print()

def print_renewal_result(base: int, ml_vals: dict, renewal: dict):
    print()
    hr("═", 58, C.PURPLE)
    print(f"\n  {b('갱신 보험료 산출')}\n")
    mult_str = f"×{renewal['mult']:.4f}"
    print(f"  {d('기준보험료')}   :  {g(f'₩{base:,}')}")
    print(f"  {d('갱신 배수')}    :  {p(mult_str)}")
    print()

    # 피처 기여도 바
    print(f"  {b('피처별 기여도')}")
    bar_items = [
        ("과거 이력",   ml_vals.get("history",0), 0.30),
        ("준칙 준수율", ml_vals.get("comply",0),  0.20),
        ("AI 모델",    ml_vals.get("model",0),   0.15),
        ("직무 위험도", ml_vals.get("duty",0),    0.15),
        ("숙련도",      ml_vals.get("skill",0),   0.10),
        ("사용 빈도",   ml_vals.get("freq",0),    0.10),
    ]
    for label, val, max_val in bar_items:
        pct = int(val / max_val * 20) if max_val > 0 else 0
        bar = "█" * pct + "░" * (20 - pct)
        sign = f"+{int(val*100)}%" if val > 0 else "±0%"
        print(f"  {d(f'{label:<8}')}  {y(bar)}  {d(sign)}")

    print()
    hr("═", 58, C.PURPLE)

    mult = renewal["mult"]
    if mult >= 1.5:
        level, col = "고위험 — 대폭 할증", r
    elif mult >= 1.2:
        level, col = "주의 — 갱신 할증 적용", y
    elif mult < 1.0:
        level, col = "우량 가입자 — 보험료 인하", g
    else:
        level, col = "표준 리스크", c

    renewal_str = f"₩{renewal['premium']:,}"
    print(f"\n  {b('갱신 연간 보험료')}  →  {col(b(renewal_str))}")
    print(f"  {d('리스크 평가')}       :  {col(level)}")
    print()


# ───────────────────────────────────────────────
# 메인 루프
# ───────────────────────────────────────────────
def main():
    while True:
        header("메인 메뉴")
        print(f"  {b('1')}.  {b('인수심사')}  — 초기 보험료 산출")
        print(f"       {d('연매출 구간 → 기준보험료 자동 설정 → 단계별 위험 가중치 적용')}\n")
        print(f"  {b('2')}.  {b('클레임 심사')}  — 보상 판정 시뮬레이션")
        print(f"       {d('트랙 A/B · 준칙 준수 · NLP Diff 오류 위치 → 전액/부분/면책')}\n")
        print(f"  {b('3')}.  {b('갱신 요율 (ML)')}  — 갱신 보험료 산출")
        print(f"       {d('6개 ML 피처 + 업무 요소 → 갱신 배수 × 기준보험료')}\n")
        print(f"  {b('4')}.  {b('전체 시뮬레이션')}  — 1·2·3단계 순서대로 진행\n")
        print(f"  {b('0')}.  종료\n")

        choice = prompt("메뉴 선택", ["0","1","2","3","4"])

        if choice == "0":
            clear()
            print(f"\n  {d('프로그램을 종료합니다.')}\n")
            sys.exit(0)

        elif choice == "1":
            try:
                inputs = step_underwrite()
                result = calculate_premium(inputs)
                print_underwrite_result(inputs, result)
                input(f"  {d('Enter를 눌러 메인 메뉴로 돌아가기...')}")
            except KeyboardInterrupt:
                pass

        elif choice == "2":
            try:
                step_claim()
            except KeyboardInterrupt:
                pass

        elif choice == "3":
            try:
                header("STEP 3 갱신 요율 — 기준보험료 설정")
                print(b("기준보험료 설정") + d("  (연매출 구간 선택)"))
                print()
                for k, (label, price) in BASE_PREMIUM_TABLE.items():
                    print(f"  {b(k)}.  {label:<12}  {g(f'₩{price:,}')}")
                print()
                rev_key = prompt("번호 선택 (1~7)", list(BASE_PREMIUM_TABLE.keys()))
                base = BASE_PREMIUM_TABLE[rev_key][1]
                ml_vals = step_renewal(base)
                renewal = calculate_renewal(base, ml_vals)
                print_renewal_result(base, ml_vals, renewal)
                input(f"  {d('Enter를 눌러 메인 메뉴로 돌아가기...')}")
            except KeyboardInterrupt:
                pass

        elif choice == "4":
            try:
                # 1단계
                inputs = step_underwrite()
                result = calculate_premium(inputs)
                print_underwrite_result(inputs, result)
                input(f"\n  {d('Enter → 2단계 클레임 심사...')}")

                # 2단계
                step_claim()

                # 3단계
                ml_vals = step_renewal(inputs["base"])
                renewal = calculate_renewal(inputs["base"], ml_vals)
                print_renewal_result(inputs["base"], ml_vals, renewal)

                # 최종 요약
                print()
                hr("═", 58, C.BLUE)
                print(f"\n  {b('전체 시뮬레이션 요약')}\n")
                initial_str = f"₩{result['final']:,}"
                mult_disp = f"×{renewal['mult']:.4f}"
                renewal_disp = f"₩{renewal['premium']:,}"
                print(f"  {d('초기 보험료')}  :  {g(b(initial_str))}")
                print(f"  {d('갱신 배수')}    :  {p(mult_disp)}")
                print(f"  {d('갱신 보험료')}  :  {p(b(renewal_disp))}")
                diff = renewal["premium"] - result["final"]
                diff_str = f"+₩{diff:,}" if diff >= 0 else f"-₩{abs(diff):,}"
                color_fn = r if diff > 0 else g
                print(f"  {d('증감')}         :  {color_fn(diff_str)}")
                print()
                hr("═", 58, C.BLUE)
                print()
                input(f"  {d('Enter를 눌러 메인 메뉴로 돌아가기...')}")
            except KeyboardInterrupt:
                pass


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n  {d('프로그램을 종료합니다.')}\n")
        sys.exit(0)
