import json
import importlib
import re
import sys

pd = importlib.import_module("pandas")
px = importlib.import_module("plotly.express")
st = importlib.import_module("streamlit")

sys.path.insert(0, ".")
from utils.rfq_processor import (
    BOM_COST_DB,
    DEMO_EXTRACTIONS,
    QUOTATION_PROMPT,
    RFQ_EXTRACTION_PROMPT,
    SAMPLE_RFQS,
    assess_risks,
    calculate_bom_cost,
    get_regulatory_info,
)

st.set_page_config(page_title="RFQ 자동 파서 | C&C AI Labs", page_icon="📋", layout="wide")


def parse_target_cost_mid(target_cost_text: str) -> float | None:
    dollar_values = re.findall(r"\$(\d+(?:\.\d+)?)", target_cost_text or "")
    if len(dollar_values) >= 2:
        nums = [float(v) for v in dollar_values[:2]]
        return round((nums[0] + nums[1]) / 2, 2)
    values = re.findall(r"\d+(?:\.\d+)?", target_cost_text or "")
    if not values:
        return None
    nums = [float(v) for v in values]
    if len(nums) >= 2:
        return round((nums[0] + nums[1]) / 2, 2)
    return round(nums[0], 2)


def render_badges(items: list[str], color: str):
    if not items:
        st.markdown("-")
        return
    badge_html = "".join(
        [
            f"<span style='display:inline-block;background:{color};color:white;padding:6px 10px;border-radius:999px;margin:4px 6px 4px 0;font-size:0.85rem;'>{item}</span>"
            for item in items
        ]
    )
    st.markdown(badge_html, unsafe_allow_html=True)


def extract_specs(rfq_text: str) -> dict:
    demo_mode = st.session_state.get("demo_mode", True)
    api_key = st.session_state.get("api_key", "")

    if demo_mode or not api_key:
        for sample_name, sample_text in SAMPLE_RFQS.items():
            if sample_text.strip()[:50] == rfq_text.strip()[:50]:
                return DEMO_EXTRACTIONS.get(sample_name, DEMO_EXTRACTIONS["글로벌 브랜드 매트 립스틱 RFQ"])
        return DEMO_EXTRACTIONS["글로벌 브랜드 매트 립스틱 RFQ"]

    anthropic = importlib.import_module("anthropic")

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": RFQ_EXTRACTION_PROMPT.format(rfq_text=rfq_text)}],
    )
    return json.loads(message.content[0].text)


def build_quotation(specs: dict, bom_cost: dict, risk_assessment: dict, regulatory_info: list[dict]) -> str:
    demo_mode = st.session_state.get("demo_mode", True)
    api_key = st.session_state.get("api_key", "")
    bom = bom_cost["bom"]
    categories = {
        "원료비": "raw_materials",
        "포장재비": "packaging",
        "인건비": "labor",
        "제조간접비": "overhead",
        "R&D비": "rnd",
        "QC/규제비": "qc_regulatory",
    }
    table_rows = "\n".join(
        [
            f"| {label} | ${bom[key]['min']:.2f} ~ ${bom[key]['max']:.2f} | {bom[key]['note']} |"
            for label, key in categories.items()
        ]
    )
    lead = bom.get("lead_time_weeks", {})
    risk_summary = "\n".join(
        [
            f"- 납기: {', '.join(risk_assessment['risks']['timeline'])}",
            f"- 규제: {', '.join(risk_assessment['risks']['regulatory'])}",
            f"- 원가: {', '.join(risk_assessment['risks']['cost'])}",
            f"- 기술: {', '.join(risk_assessment['risks']['technical'])}",
        ]
    )
    reg_rows = "\n".join(
        [
            f"| {m['flag']} {m['name']} | {m['requirements']} | {m['timeline']} | {m['cost']} | {m['risk_notes']} |"
            for m in regulatory_info
        ]
    )
    quotation = f"""## 견적서 초안 (Quotation Draft)

### 1. 프로젝트 개요
- 제품명: {specs.get('product_name', '-')}
- 제품 유형: {bom.get('label', specs.get('product_type', '-'))}
- 셰이드 수: {specs.get('shade_count', '-')}색
- 제형/마감: {specs.get('texture_finish', '-')}
- 패키징: {specs.get('packaging_type', '-')} / {specs.get('packaging_details', '-')}
- 대상 시장: {', '.join(specs.get('target_markets', [])) or '-'}
- 특수 요구사항: {', '.join(specs.get('special_requirements', [])) or '-'}

### 2. 예상 원가 구조 (Per Unit)
| 항목 | 예상 단가 (USD) | 비고 |
|------|----------------|------|
{table_rows}
| **합계** | **${bom_cost['total_min']:.2f} ~ ${bom_cost['total_max']:.2f}** | 제품 유형별 기준 BOM 산출 |

### 3. MOQ 및 리드타임
- MOQ: {specs.get('moq', '-')}
- 샘플 개발: {lead.get('sample', '-')}주
- 승인 라운드: {lead.get('approval_rounds', '-')} 
- 안정성 시험: {lead.get('stability', '-')}주
- 원부자재 조달: {lead.get('procurement', '-')}주
- 양산: {lead.get('production', '-')}주
- 출하: {lead.get('shipping', '-')}주

### 4. 규제 사항
| 시장 | 요구사항 | 기간 | 비용 | 리스크 메모 |
|------|----------|------|------|------------|
{reg_rows if reg_rows else '| - | - | - | - | - |'}

### 5. 특이사항 및 권고
- 종합 리스크 등급: **{risk_assessment['overall_label']}** (점수 {risk_assessment['overall']}/100)
{risk_summary}

---
*C&C International | AI Labs 자동 생성 초안 | 내부 검토 후 확정 필요*
"""
    if demo_mode or not api_key:
        return quotation

    anthropic = importlib.import_module("anthropic")

    client = anthropic.Anthropic(api_key=api_key)
    llm_prompt = QUOTATION_PROMPT.format(specs_json=json.dumps(specs, ensure_ascii=False, indent=2))
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=3000,
        messages=[{"role": "user", "content": f"{llm_prompt}\n\n참고 BOM 데이터:\n{quotation}"}],
    )
    return message.content[0].text


st.markdown("# 📋 RFQ 자동 파서 + 견적서 생성")
st.markdown("글로벌 고객 RFQ를 입력하면 **사양 추출 · BOM 원가 분석 · 리스크 평가 · 견적서 초안**을 한 번에 생성합니다.")

left, right = st.columns(2)
with left:
    st.markdown(
        """
        <div style="background:#ffe9e9;border:1px solid #ffcccc;border-radius:12px;padding:16px;min-height:120px;">
            <h4 style="margin:0 0 8px 0;color:#c62828;">기존 프로세스</h4>
            <p style="margin:0;color:#4e342e;">RFQ 수신 → 수동 파싱(2~5일) → Excel BOM 계산 → 견적서 작성 = <b>건당 12시간+</b></p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with right:
    st.markdown(
        """
        <div style="background:#e8f5e9;border:1px solid #b9e6bf;border-radius:12px;padding:16px;min-height:120px;">
            <h4 style="margin:0 0 8px 0;color:#2e7d32;">AI 자동화</h4>
            <p style="margin:0;color:#1b5e20;">RFQ 입력 → 자동 파싱 + BOM 계산 + 리스크 분석 + 견적서 생성 = <b>2시간 이내</b></p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")
st.markdown("### RFQ 입력")

input_mode = st.radio("입력 방식", ["샘플 RFQ 선택", "직접 입력"], horizontal=True)

if input_mode == "샘플 RFQ 선택":
    selected_sample = st.selectbox("샘플 선택", list(SAMPLE_RFQS.keys()))
    rfq_text = st.text_area("RFQ 원문", value=SAMPLE_RFQS[selected_sample], height=350)
else:
    selected_sample = None
    rfq_text = st.text_area(
        "RFQ 원문",
        placeholder="고객 RFQ 이메일/브리프 전문을 붙여넣어 주세요. 영어/중국어/한국어 모두 분석 가능합니다.",
        height=350,
    )

run_analysis = st.button("🔍 RFQ 분석 시작", type="primary", use_container_width=True)

if run_analysis:
    if not rfq_text.strip():
        st.warning("RFQ 내용을 입력해 주세요.")
    else:
        with st.spinner("RFQ 분석 파이프라인 실행 중..."):
            specs = extract_specs(rfq_text)
            product_type = specs.get("product_type", "other")
            if product_type not in BOM_COST_DB:
                product_type = "other"
            bom_cost = calculate_bom_cost(product_type)
            risk_assessment = assess_risks(specs)
            regulatory_info = get_regulatory_info(specs.get("target_markets", []))
            quotation = build_quotation(specs, bom_cost, risk_assessment, regulatory_info)
            st.session_state["rfq_analysis_result"] = {
                "specs": specs,
                "bom_cost": bom_cost,
                "risk_assessment": risk_assessment,
                "regulatory_info": regulatory_info,
                "quotation": quotation,
            }

if "rfq_analysis_result" in st.session_state:
    result = st.session_state["rfq_analysis_result"]
    specs = result["specs"]
    bom_cost = result["bom_cost"]
    risk_assessment = result["risk_assessment"]
    regulatory_info = result["regulatory_info"]
    quotation = result["quotation"]
    bom = bom_cost["bom"]

    st.markdown("---")
    tabs = st.tabs(["📊 사양 추출", "💰 BOM 원가 분석", "⚠️ 리스크 평가", "📋 견적서 초안", "🌍 규제 사항"])

    with tabs[0]:
        left_col, right_col = st.columns(2)
        with left_col:
            st.markdown("#### 기본 정보")
            basic_df = pd.DataFrame(
                [
                    {"항목": "제품 유형", "값": specs.get("product_type", "-")},
                    {"항목": "제품명", "값": specs.get("product_name", "-")},
                    {"항목": "셰이드 수", "값": f"{specs.get('shade_count', '-')}"},
                    {"항목": "텍스처/마감", "값": specs.get("texture_finish", "-")},
                    {"항목": "패키징", "값": specs.get("packaging_type", "-")},
                ]
            )
            st.dataframe(basic_df, use_container_width=True, hide_index=True)
        with right_col:
            st.markdown("#### 상업 조건")
            commercial_df = pd.DataFrame(
                [
                    {"항목": "타겟 단가", "값": specs.get("target_cost_usd", "-")},
                    {"항목": "MOQ", "값": specs.get("moq", "-")},
                    {"항목": "대상 시장", "값": ", ".join(specs.get("target_markets", [])) or "-"},
                    {"항목": "요청 납기", "값": specs.get("delivery_timeline", "-")},
                ]
            )
            st.dataframe(commercial_df, use_container_width=True, hide_index=True)

        req_col, claim_col = st.columns(2)
        with req_col:
            st.markdown("#### 특수 요구사항")
            render_badges(specs.get("special_requirements", []), "#7e57c2")
        with claim_col:
            st.markdown("#### 핵심 클레임")
            render_badges(specs.get("key_claims", []), "#00897b")

        st.info(f"AI 요약: {specs.get('raw_summary', '-')}")

    with tabs[1]:
        st.markdown(f"### 제품 유형: **{bom.get('label', '기타')}**")
        cost_rows = [
            {"항목": "원료비", "최소 단가 (USD)": bom["raw_materials"]["min"], "최대 단가 (USD)": bom["raw_materials"]["max"], "비고": bom["raw_materials"]["note"]},
            {"항목": "포장재비", "최소 단가 (USD)": bom["packaging"]["min"], "최대 단가 (USD)": bom["packaging"]["max"], "비고": bom["packaging"]["note"]},
            {"항목": "인건비", "최소 단가 (USD)": bom["labor"]["min"], "최대 단가 (USD)": bom["labor"]["max"], "비고": bom["labor"]["note"]},
            {"항목": "제조간접비", "최소 단가 (USD)": bom["overhead"]["min"], "최대 단가 (USD)": bom["overhead"]["max"], "비고": bom["overhead"]["note"]},
            {"항목": "R&D비", "최소 단가 (USD)": bom["rnd"]["min"], "최대 단가 (USD)": bom["rnd"]["max"], "비고": bom["rnd"]["note"]},
            {"항목": "QC/규제비", "최소 단가 (USD)": bom["qc_regulatory"]["min"], "최대 단가 (USD)": bom["qc_regulatory"]["max"], "비고": bom["qc_regulatory"]["note"]},
            {"항목": "TOTAL", "최소 단가 (USD)": bom_cost["total_min"], "최대 단가 (USD)": bom_cost["total_max"], "비고": "제품 유형별 BOM 합계"},
        ]
        st.dataframe(pd.DataFrame(cost_rows), use_container_width=True, hide_index=True)

        target_mid = parse_target_cost_mid(specs.get("target_cost_usd", ""))
        calc_mid = round((bom_cost["total_min"] + bom_cost["total_max"]) / 2, 2)
        delta_text = "타겟 단가 없음"
        margin_text = "N/A"
        if target_mid is not None:
            delta_text = f"{calc_mid - target_mid:+.2f} USD vs 타겟"
            margin = ((target_mid - calc_mid) / target_mid) * 100 if target_mid > 0 else 0
            margin_text = f"{margin:.1f}%"

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("총 원가 최소", f"${bom_cost['total_min']:.2f}")
        m2.metric("총 원가 최대", f"${bom_cost['total_max']:.2f}")
        m3.metric("타겟 단가 대비", f"${calc_mid:.2f}", delta=delta_text, delta_color="inverse")
        m4.metric("예상 마진", margin_text)

        chart_df = pd.DataFrame(
            [
                {"항목": "원료비", "평균 단가": round((bom["raw_materials"]["min"] + bom["raw_materials"]["max"]) / 2, 2)},
                {"항목": "포장재비", "평균 단가": round((bom["packaging"]["min"] + bom["packaging"]["max"]) / 2, 2)},
                {"항목": "인건비", "평균 단가": round((bom["labor"]["min"] + bom["labor"]["max"]) / 2, 2)},
                {"항목": "제조간접비", "평균 단가": round((bom["overhead"]["min"] + bom["overhead"]["max"]) / 2, 2)},
                {"항목": "R&D비", "평균 단가": round((bom["rnd"]["min"] + bom["rnd"]["max"]) / 2, 2)},
                {"항목": "QC/규제비", "평균 단가": round((bom["qc_regulatory"]["min"] + bom["qc_regulatory"]["max"]) / 2, 2)},
            ]
        )
        fig = px.bar(chart_df, x="평균 단가", y="항목", orientation="h", title="BOM 항목별 평균 원가 기여도", color="평균 단가", color_continuous_scale="Blues")
        st.plotly_chart(fig, use_container_width=True)

        lead = bom.get("lead_time_weeks", {})
        lead_df = pd.DataFrame(
            [
                {"단계": "샘플 개발", "예상 기간": f"{lead.get('sample', '-')}주"},
                {"단계": "승인 라운드", "예상 기간": lead.get("approval_rounds", "-")},
                {"단계": "안정성 시험", "예상 기간": f"{lead.get('stability', '-')}주"},
                {"단계": "원부자재 조달", "예상 기간": f"{lead.get('procurement', '-')}주"},
                {"단계": "양산", "예상 기간": f"{lead.get('production', '-')}주"},
                {"단계": "출하", "예상 기간": f"{lead.get('shipping', '-')}주"},
            ]
        )
        st.markdown("#### 리드타임 타임라인")
        st.dataframe(lead_df, use_container_width=True, hide_index=True)

    with tabs[2]:
        scores = risk_assessment["scores"]
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("납기 리스크", f"{scores['timeline']}/100", delta=f"{scores['timeline'] - 20:+}", delta_color="inverse")
        r2.metric("규제 리스크", f"{scores['regulatory']}/100", delta=f"{scores['regulatory'] - 20:+}", delta_color="inverse")
        r3.metric("원가 리스크", f"{scores['cost']}/100", delta=f"{scores['cost'] - 20:+}", delta_color="inverse")
        r4.metric("기술 리스크", f"{scores['technical']}/100", delta=f"{scores['technical'] - 20:+}", delta_color="inverse")

        overall_color = risk_assessment["overall_color"]
        st.markdown(
            f"""
            <div style="margin:16px 0;padding:14px 18px;border-radius:10px;background:{overall_color};color:white;font-weight:700;font-size:1.05rem;">
                종합 리스크 등급: {risk_assessment['overall_label']} ({risk_assessment['overall']}/100)
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.expander("납기 리스크 상세", expanded=True):
            for item in risk_assessment["risks"]["timeline"]:
                st.markdown(f"- {item}")
        with st.expander("규제 리스크 상세", expanded=True):
            for item in risk_assessment["risks"]["regulatory"]:
                st.markdown(f"- {item}")
        with st.expander("원가 리스크 상세", expanded=True):
            for item in risk_assessment["risks"]["cost"]:
                st.markdown(f"- {item}")
        with st.expander("기술 리스크 상세", expanded=True):
            for item in risk_assessment["risks"]["technical"]:
                st.markdown(f"- {item}")

    with tabs[3]:
        st.markdown(quotation)
        st.download_button(
            label="📥 견적서 초안 다운로드 (Markdown)",
            data=quotation,
            file_name="quotation_draft.md",
            mime="text/markdown",
            use_container_width=True,
        )

    with tabs[4]:
        high_risk_names = {"중국", "중동"}
        for market_row in regulatory_info:
            is_high_risk = market_row["name"] in high_risk_names
            if is_high_risk:
                st.markdown(
                    f"<div style='background:#ffebee;border:1px solid #ef9a9a;color:#b71c1c;padding:10px 12px;border-radius:8px;margin-bottom:8px;'><b>고위험 시장:</b> {market_row['flag']} {market_row['name']}</div>",
                    unsafe_allow_html=True,
                )
            reg_df = pd.DataFrame(
                [
                    {
                        "국가": f"{market_row['flag']} {market_row['name']}",
                        "요구사항": market_row["requirements"],
                        "예상 기간": market_row["timeline"],
                        "추가 비용": market_row["cost"],
                        "리스크 메모": market_row["risk_notes"],
                    }
                ]
            )
            st.dataframe(reg_df, use_container_width=True, hide_index=True)

st.markdown("---")
with st.expander("샘플 RFQ 모음", expanded=False):
    for sample_name, sample_text in SAMPLE_RFQS.items():
        st.markdown(f"#### {sample_name}")
        st.text(sample_text)
