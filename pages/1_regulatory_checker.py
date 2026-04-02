import json
import streamlit as st
import pandas as pd

import sys
sys.path.insert(0, ".")
from utils.regulatory_db import (
    RegulatoryStatus,
    check_ingredient,
    search_ingredient,
    get_all_ingredients,
    SAMPLE_FORMULAS,
    REGULATORY_DATABASE,
)

st.set_page_config(page_title="규제 성분 검증 | C&C AI Labs", page_icon="🔬", layout="wide")

st.markdown("# 🔬 화장품 성분 규제 검증 시스템")
st.markdown("INCI 성분 리스트를 입력하면 **EU / 미국 / 중국 / 한국** 4개 시장의 규제 적합성을 동시에 검증합니다.")
st.markdown("---")

STATUS_EMOJI = {
    RegulatoryStatus.ALLOWED: "✅",
    RegulatoryStatus.RESTRICTED: "⚠️",
    RegulatoryStatus.BANNED: "🚫",
    RegulatoryStatus.NOT_LISTED: "❓",
    RegulatoryStatus.REQUIRES_NOTIFICATION: "📋",
}

STATUS_COLOR = {
    RegulatoryStatus.ALLOWED: "green",
    RegulatoryStatus.RESTRICTED: "orange",
    RegulatoryStatus.BANNED: "red",
    RegulatoryStatus.NOT_LISTED: "gray",
    RegulatoryStatus.REQUIRES_NOTIFICATION: "blue",
}


def render_status_badge(status: RegulatoryStatus) -> str:
    emoji = STATUS_EMOJI.get(status, "❓")
    return f"{emoji} {status.value}"


def run_db_check(ingredients_input: list[tuple[str, str]]) -> list[dict]:
    results = []
    for inci_name, concentration in ingredients_input:
        reg = check_ingredient(inci_name)
        if reg is None:
            searched = search_ingredient(inci_name)
            if searched:
                reg = searched[0]

        if reg:
            results.append({
                "inci_name": reg.inci_name,
                "common_name_ko": reg.common_name_ko,
                "concentration": concentration,
                "function": reg.function,
                "category": reg.category,
                "eu_status": reg.eu_status,
                "us_status": reg.us_status,
                "cn_status": reg.cn_status,
                "kr_status": reg.kr_status,
                "eu_max": reg.eu_max_concentration,
                "us_max": reg.us_max_concentration,
                "cn_max": reg.cn_max_concentration,
                "kr_max": reg.kr_max_concentration,
                "eu_note": reg.eu_note,
                "us_note": reg.us_note,
                "cn_note": reg.cn_note,
                "kr_note": reg.kr_note,
                "required_labeling": reg.required_labeling,
            })
        else:
            results.append({
                "inci_name": inci_name.upper(),
                "common_name_ko": "-",
                "concentration": concentration,
                "function": "-",
                "category": "-",
                "eu_status": RegulatoryStatus.NOT_LISTED,
                "us_status": RegulatoryStatus.NOT_LISTED,
                "cn_status": RegulatoryStatus.NOT_LISTED,
                "kr_status": RegulatoryStatus.NOT_LISTED,
                "eu_max": "", "us_max": "", "cn_max": "", "kr_max": "",
                "eu_note": "DB 미등재 — LLM 심층 분석 또는 CosIng/KFDA 직접 확인 필요",
                "us_note": "DB 미등재", "cn_note": "DB 미등재", "kr_note": "DB 미등재",
                "required_labeling": [],
            })
    return results


def run_llm_analysis(ingredients_input: list[tuple[str, str]], db_results: list[dict]) -> str:
    demo_mode = st.session_state.get("demo_mode", True)
    api_key = st.session_state.get("api_key", "")

    if demo_mode or not api_key:
        return generate_demo_analysis(db_results)

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)

        db_summary = json.dumps([{
            "inci": r["inci_name"],
            "concentration": r["concentration"],
            "eu": r["eu_status"].value,
            "us": r["us_status"].value,
            "cn": r["cn_status"].value,
            "kr": r["kr_status"].value,
        } for r in db_results], ensure_ascii=False)

        prompt = f"""You are a cosmetics regulatory expert specializing in global market compliance.
Analyze this cosmetics formula for regulatory compliance across EU, US, China (NMPA), and Korea (MFDS).

FORMULA INGREDIENTS:
{json.dumps([{"inci": name, "concentration": conc} for name, conc in ingredients_input], ensure_ascii=False)}

PRELIMINARY DB CHECK RESULTS:
{db_summary}

Provide a comprehensive analysis IN KOREAN (한국어) with:

1. **종합 판정**: 각 시장별 출시 가능 여부 (가능/조건부 가능/불가)
2. **주요 리스크**: 금지/제한 성분 상세 분석
3. **농도 초과 여부**: 각 제한 성분의 허용 농도 vs 실제 농도 비교
4. **필수 라벨링**: 시장별 필수 표시 사항
5. **권고사항**: 처방 수정 제안, 대체 성분 추천
6. **규제 동향**: 향후 규제 변경 가능성 (PFAS, 레티놀 등)

Be specific, cite regulation numbers where possible. This is for a professional ODM context."""

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text
    except Exception as e:
        return f"API 호출 실패: {e}\n\n데모 모드 분석으로 대체합니다.\n\n{generate_demo_analysis(db_results)}"


def generate_demo_analysis(db_results: list[dict]) -> str:
    banned_eu = [r for r in db_results if r["eu_status"] == RegulatoryStatus.BANNED]
    banned_us = [r for r in db_results if r["us_status"] == RegulatoryStatus.BANNED]
    banned_cn = [r for r in db_results if r["cn_status"] == RegulatoryStatus.BANNED]
    banned_kr = [r for r in db_results if r["kr_status"] == RegulatoryStatus.BANNED]

    restricted_eu = [r for r in db_results if r["eu_status"] == RegulatoryStatus.RESTRICTED]
    restricted_us = [r for r in db_results if r["us_status"] == RegulatoryStatus.RESTRICTED]
    restricted_cn = [r for r in db_results if r["cn_status"] == RegulatoryStatus.RESTRICTED]
    restricted_kr = [r for r in db_results if r["kr_status"] == RegulatoryStatus.RESTRICTED]

    not_listed = [r for r in db_results if r["eu_status"] == RegulatoryStatus.NOT_LISTED]

    labeling_items = []
    for r in db_results:
        labeling_items.extend(r.get("required_labeling", []))

    eu_verdict = "🚫 출시 불가" if banned_eu else ("⚠️ 조건부 가능" if restricted_eu else "✅ 출시 가능")
    us_verdict = "🚫 출시 불가" if banned_us else ("⚠️ 조건부 가능" if restricted_us else "✅ 출시 가능")
    cn_verdict = "🚫 출시 불가" if banned_cn else ("⚠️ 조건부 가능" if restricted_cn else "✅ 출시 가능")
    kr_verdict = "🚫 출시 불가" if banned_kr else ("⚠️ 조건부 가능" if restricted_kr else "✅ 출시 가능")

    analysis = f"""## 📋 AI 심층 분석 리포트 (데모 모드)

> ⚠️ 이 분석은 내장 DB 기반 데모입니다. 실제 서비스에서는 Claude API를 통해 최신 규제 정보와 교차 검증합니다.

### 1. 종합 판정

| 시장 | 판정 | 금지 성분 | 제한 성분 |
|------|------|----------|----------|
| 🇪🇺 EU | {eu_verdict} | {len(banned_eu)}건 | {len(restricted_eu)}건 |
| 🇺🇸 US | {us_verdict} | {len(banned_us)}건 | {len(restricted_us)}건 |
| 🇨🇳 CN | {cn_verdict} | {len(banned_cn)}건 | {len(restricted_cn)}건 |
| 🇰🇷 KR | {kr_verdict} | {len(banned_kr)}건 | {len(restricted_kr)}건 |

### 2. 주요 리스크 분석
"""
    all_banned = set()
    for r in banned_eu + banned_us + banned_cn + banned_kr:
        all_banned.add(r["inci_name"])

    if all_banned:
        analysis += "\n**금지 성분 발견:**\n"
        for name in all_banned:
            matching = [r for r in db_results if r["inci_name"] == name][0]
            markets = []
            if matching["eu_status"] == RegulatoryStatus.BANNED:
                markets.append(f"EU: {matching['eu_note']}")
            if matching["us_status"] == RegulatoryStatus.BANNED:
                markets.append(f"US: {matching['us_note']}")
            if matching["cn_status"] == RegulatoryStatus.BANNED:
                markets.append(f"CN: {matching['cn_note']}")
            if matching["kr_status"] == RegulatoryStatus.BANNED:
                markets.append(f"KR: {matching['kr_note']}")
            analysis += f"\n- **{name}** ({matching['common_name_ko']})\n"
            for m in markets:
                analysis += f"  - {m}\n"
    else:
        analysis += "\n금지 성분 없음.\n"

    if restricted_eu or restricted_us or restricted_cn or restricted_kr:
        analysis += "\n### 3. 제한 성분 농도 확인\n\n"
        analysis += "| 성분 | 배합 농도 | EU 한도 | US 한도 | CN 한도 | KR 한도 |\n"
        analysis += "|------|----------|---------|---------|---------|----------|\n"
        seen = set()
        for r in restricted_eu + restricted_us + restricted_cn + restricted_kr:
            if r["inci_name"] not in seen:
                seen.add(r["inci_name"])
                analysis += f"| {r['inci_name']} | {r['concentration']} | {r['eu_max'] or '-'} | {r['us_max'] or '-'} | {r['cn_max'] or '-'} | {r['kr_max'] or '-'} |\n"

    if labeling_items:
        analysis += "\n### 4. 필수 라벨링 사항\n\n"
        for item in set(labeling_items):
            analysis += f"- {item}\n"

    if not_listed:
        analysis += "\n### 5. DB 미등재 성분\n\n"
        analysis += "다음 성분은 내장 DB에 없어 수동 확인이 필요합니다:\n\n"
        for r in not_listed:
            analysis += f"- **{r['inci_name']}** — EU CosIng, KFDA 원료목록에서 직접 확인 권장\n"

    analysis += "\n### 6. 권고사항\n\n"
    analysis += "- 금지 성분이 있는 경우 즉시 대체 원료를 검토하세요.\n"
    analysis += "- 제한 성분은 배합 농도가 각 시장 한도 이내인지 확인하세요.\n"
    analysis += "- EU PFAS 규제 강화 동향을 모니터링하세요 (PTFE 등 불소화합물).\n"
    analysis += "- 레티놀(Retinol) EU 규제 강화 (2025년): 페이스 0.3%, 바디 0.05% 상한 확인.\n"
    analysis += "- DB 미등재 성분은 CosIng (EU), FDA (US), NMPA (CN), MFDS (KR) 공식 DB에서 확인하세요.\n"

    return analysis


tab_formula, tab_search, tab_db = st.tabs(["📝 포뮬라 검증", "🔍 성분 개별 검색", "📚 규제 DB 전체 조회"])

with tab_formula:
    st.markdown("### 포뮬라 성분 리스트 검증")
    st.markdown("INCI 성분명과 배합 농도를 입력하세요. 샘플 포뮬라를 선택하거나 직접 입력할 수 있습니다.")

    sample_choice = st.selectbox(
        "샘플 포뮬라 선택 (또는 직접 입력)",
        ["직접 입력"] + list(SAMPLE_FORMULAS.keys()),
    )

    if sample_choice != "직접 입력":
        sample_data = SAMPLE_FORMULAS[sample_choice]
        default_text = "\n".join([f"{name}, {conc}" for name, conc in sample_data])
    else:
        default_text = "PHENOXYETHANOL, 0.9%\nCI 77491, 5.0%\nRETINOL, 0.5%"

    ingredients_text = st.text_area(
        "성분 리스트 (한 줄에 하나씩: INCI명, 농도%)",
        value=default_text,
        height=300,
        help="예시: PHENOXYETHANOL, 0.9%",
    )

    target_markets = st.multiselect(
        "대상 시장 선택",
        ["EU", "US (미국)", "CN (중국)", "KR (한국)"],
        default=["EU", "US (미국)", "CN (중국)", "KR (한국)"],
    )

    if st.button("🔍 규제 검증 실행", type="primary", use_container_width=True):
        lines = [line.strip() for line in ingredients_text.strip().split("\n") if line.strip()]
        parsed_ingredients = []
        for line in lines:
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 2:
                parsed_ingredients.append((parts[0], parts[1]))
            elif len(parts) == 1:
                parsed_ingredients.append((parts[0], "N/A"))

        if not parsed_ingredients:
            st.error("성분을 1개 이상 입력해주세요.")
        else:
            with st.spinner("규제 DB 검증 중..."):
                db_results = run_db_check(parsed_ingredients)

            st.markdown("### 📊 시장별 규제 검증 결과")

            summary_data = []
            for r in db_results:
                summary_data.append({
                    "INCI명": r["inci_name"],
                    "한국어명": r["common_name_ko"],
                    "배합 농도": r["concentration"],
                    "기능": r["function"],
                    "🇪🇺 EU": render_status_badge(r["eu_status"]),
                    "🇺🇸 US": render_status_badge(r["us_status"]),
                    "🇨🇳 CN": render_status_badge(r["cn_status"]),
                    "🇰🇷 KR": render_status_badge(r["kr_status"]),
                })

            st.dataframe(
                pd.DataFrame(summary_data),
                use_container_width=True,
                hide_index=True,
            )

            total = len(db_results)
            banned_count = sum(
                1 for r in db_results
                if any(s == RegulatoryStatus.BANNED for s in [r["eu_status"], r["us_status"], r["cn_status"], r["kr_status"]])
            )
            restricted_count = sum(
                1 for r in db_results
                if any(s == RegulatoryStatus.RESTRICTED for s in [r["eu_status"], r["us_status"], r["cn_status"], r["kr_status"]])
            )
            safe_count = total - banned_count - restricted_count

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("전체 성분", f"{total}개")
            col2.metric("안전 (전 시장)", f"{safe_count}개", delta=None)
            col3.metric("제한 성분", f"{restricted_count}개", delta=f"-{restricted_count}" if restricted_count else None, delta_color="inverse")
            col4.metric("금지 성분", f"{banned_count}개", delta=f"-{banned_count}" if banned_count else None, delta_color="inverse")

            st.markdown("---")

            with st.expander("📋 성분별 상세 규제 정보", expanded=True):
                for r in db_results:
                    has_issue = any(
                        s in (RegulatoryStatus.BANNED, RegulatoryStatus.RESTRICTED)
                        for s in [r["eu_status"], r["us_status"], r["cn_status"], r["kr_status"]]
                    )
                    icon = "🔴" if any(s == RegulatoryStatus.BANNED for s in [r["eu_status"], r["us_status"], r["cn_status"], r["kr_status"]]) else ("🟡" if has_issue else "🟢")

                    with st.expander(f"{icon} {r['inci_name']} ({r['common_name_ko']}) — {r['concentration']}"):
                        detail_col1, detail_col2 = st.columns(2)
                        with detail_col1:
                            st.markdown(f"**🇪🇺 EU**: {render_status_badge(r['eu_status'])}")
                            if r["eu_max"]:
                                st.markdown(f"  - 최대 허용 농도: {r['eu_max']}")
                            st.markdown(f"  - {r['eu_note']}")

                            st.markdown(f"**🇺🇸 US**: {render_status_badge(r['us_status'])}")
                            if r["us_max"]:
                                st.markdown(f"  - 최대 허용 농도: {r['us_max']}")
                            st.markdown(f"  - {r['us_note']}")

                        with detail_col2:
                            st.markdown(f"**🇨🇳 CN**: {render_status_badge(r['cn_status'])}")
                            if r["cn_max"]:
                                st.markdown(f"  - 최대 허용 농도: {r['cn_max']}")
                            st.markdown(f"  - {r['cn_note']}")

                            st.markdown(f"**🇰🇷 KR**: {render_status_badge(r['kr_status'])}")
                            if r["kr_max"]:
                                st.markdown(f"  - 최대 허용 농도: {r['kr_max']}")
                            st.markdown(f"  - {r['kr_note']}")

                        if r.get("required_labeling"):
                            st.markdown("**필수 라벨링:**")
                            for label in r["required_labeling"]:
                                st.markdown(f"- {label}")

            st.markdown("---")
            st.markdown("### 🤖 AI 심층 분석")

            with st.spinner("AI 분석 생성 중..."):
                analysis = run_llm_analysis(parsed_ingredients, db_results)

            st.markdown(analysis)

with tab_search:
    st.markdown("### 성분 개별 검색")
    query = st.text_input("INCI명 또는 한국어명으로 검색", placeholder="예: RETINOL, 레티놀, 페녹시에탄올")

    if query:
        results = search_ingredient(query)
        if results:
            for reg in results:
                st.markdown(f"#### {reg.inci_name} ({reg.common_name_ko})")
                st.markdown(f"**기능**: {reg.function} | **CAS**: {reg.cas_number} | **카테고리**: {reg.category}")

                detail_df = pd.DataFrame([
                    {"시장": "🇪🇺 EU", "상태": render_status_badge(reg.eu_status), "최대 농도": reg.eu_max_concentration, "비고": reg.eu_note},
                    {"시장": "🇺🇸 US", "상태": render_status_badge(reg.us_status), "최대 농도": reg.us_max_concentration, "비고": reg.us_note},
                    {"시장": "🇨🇳 CN", "상태": render_status_badge(reg.cn_status), "최대 농도": reg.cn_max_concentration, "비고": reg.cn_note},
                    {"시장": "🇰🇷 KR", "상태": render_status_badge(reg.kr_status), "최대 농도": reg.kr_max_concentration, "비고": reg.kr_note},
                ])
                st.dataframe(detail_df, use_container_width=True, hide_index=True)

                if reg.required_labeling:
                    st.markdown("**필수 라벨링:** " + " / ".join(reg.required_labeling))
                st.markdown("---")
        else:
            st.warning(f"'{query}'에 대한 결과가 없습니다. 내장 DB에 등록되지 않은 성분일 수 있습니다.")
            st.info("실제 서비스에서는 EU CosIng, FDA, NMPA, MFDS 공식 DB와 연동하여 포괄적으로 검색합니다.")

with tab_db:
    st.markdown("### 규제 DB 전체 조회")
    st.markdown(f"현재 등록 성분: **{len(REGULATORY_DATABASE)}개** (MVP 데모용)")

    category_filter = st.selectbox(
        "카테고리 필터",
        ["전체"] + list(set(r.category for r in REGULATORY_DATABASE.values() if r.category)),
    )

    all_data = []
    for reg in REGULATORY_DATABASE.values():
        if category_filter != "전체" and reg.category != category_filter:
            continue
        all_data.append({
            "INCI명": reg.inci_name,
            "한국어명": reg.common_name_ko,
            "기능": reg.function,
            "카테고리": reg.category,
            "🇪🇺 EU": render_status_badge(reg.eu_status),
            "🇺🇸 US": render_status_badge(reg.us_status),
            "🇨🇳 CN": render_status_badge(reg.cn_status),
            "🇰🇷 KR": render_status_badge(reg.kr_status),
        })

    st.dataframe(pd.DataFrame(all_data), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown(
        """
        > **참고**: 이 DB는 MVP 데모 목적으로 주요 규제 성분만 포함합니다.
        > 실제 서비스에서는 다음 공인 DB와 연동합니다:
        > - 🇪🇺 [EU CosIng](https://single-market-economy.ec.europa.eu/sectors/cosmetics/cosmetic-ingredient-database_en)
        > - 🇺🇸 [FDA/MoCRA](https://www.fda.gov/cosmetics)
        > - 🇨🇳 [NMPA 화장품 원료 목록](https://www.nmpa.gov.cn/)
        > - 🇰🇷 [MFDS 화장품 원료 기준](https://www.mfds.go.kr/)
        """
    )
