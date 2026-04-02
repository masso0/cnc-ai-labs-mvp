import json
import streamlit as st
import pandas as pd

import sys
sys.path.insert(0, ".")
from utils.rfq_processor import (
    RFQ_EXTRACTION_PROMPT,
    QUOTATION_PROMPT,
    SAMPLE_RFQS,
)

st.set_page_config(page_title="RFQ 자동 파서 | C&C AI Labs", page_icon="📋", layout="wide")

st.markdown("# 📋 RFQ 자동 파서 + 견적서 생성")
st.markdown("글로벌 고객의 제품 브리프(RFQ)를 입력하면 **제품 사양을 자동 추출**하고 **견적서 초안**을 생성합니다.")
st.markdown("---")


DEMO_EXTRACTIONS = {
    "글로벌 브랜드 매트 립스틱 RFQ": {
        "product_type": "lipstick",
        "product_name": "Velvet Noir Matte Lipstick Collection",
        "shade_count": 12,
        "texture_finish": "velvet matte",
        "packaging_type": "bullet",
        "packaging_details": "Standard bullet tube, magnetic closure, soft-touch matte exterior, black with gold accent, brand logo engraving on cap",
        "target_cost_usd": "$3.50-4.50 (primary packaging included, secondary excluded)",
        "moq": "5,000 units per shade (60,000 total)",
        "target_markets": ["US", "EU", "ME"],
        "delivery_timeline": "Samples: Aug 2026 / Production: Oct 2026 / Delivery: Dec 2026",
        "special_requirements": ["Vegan", "Cruelty-free (Leaping Bunny)", "Clean at Sephora compliant", "Paraben-free", "PFAS-free", "Mineral oil-free"],
        "key_claims": ["8-hour wear", "Transfer-proof", "Hydrating", "Lightweight feel", "Non-drying"],
        "raw_summary": "미국 시장 중심의 K-뷰티 감성 벨벳 매트 립스틱 12색 컬렉션. 비건/크루얼티프리/세포라 클린 뷰티 기준 충족 필요. 셰이드당 5,000개 MOQ, 단가 $3.50-4.50 타겟."
    },
    "중국 로컬 브랜드 쿠션 파운데이션 RFQ": {
        "product_type": "cushion_foundation",
        "product_name": "气垫粉底液 (쿠션 파운데이션)",
        "shade_count": 8,
        "texture_finish": "dewy",
        "packaging_type": "cushion",
        "packaging_details": "Square cushion compact, 15g+15g (with refill), matte white shell, silver logo embossing, custom mold required",
        "target_cost_usd": "¥35-45 RMB/set (~$4.80-6.20 USD, including refill and packaging)",
        "moq": "3,000 sets per shade (24,000 total)",
        "target_markets": ["CN", "SEA"],
        "delivery_timeline": "Samples: Jul 2026 / Mass production delivery: Oct 2026",
        "special_requirements": ["NMPA registration required", "Halal certification (for SEA market)"],
        "key_claims": ["SPF50+ PA++++", "Dewy/luminous finish", "Medium coverage", "Asian skin tone optimized"],
        "raw_summary": "중국 신흥 뷰티 브랜드의 아시안 피부톤 특화 쿠션 파운데이션 8색. SPF50+ PA++++, 광택감 마감. 티몰 플래그십 + Shopee(동남아) 판매 예정. NMPA 등록 및 할랄 인증 필요."
    },
    "유럽 인디 브랜드 아이섀도우 팔레트 RFQ": {
        "product_type": "eyeshadow",
        "product_name": "Aurora Borealis 12-Pan Eyeshadow Palette",
        "shade_count": 12,
        "texture_finish": "mixed (matte/shimmer/duochrome/glitter)",
        "packaging_type": "compact",
        "packaging_details": "Rectangular cardboard palette, magnetic closure, full-size mirror inside, FSC-certified packaging, Aurora design artwork (client provides files)",
        "target_cost_usd": "EUR 4.00-5.50 (~$4.30-5.90 USD, excluding secondary packaging)",
        "moq": "3,000 units",
        "target_markets": ["EU", "UK"],
        "delivery_timeline": "Samples: Jun 2026 / Production: Sep 2026",
        "special_requirements": ["Talc-free formula", "EU Cosmetics Regulation 1223/2009 compliant", "FSC-certified packaging"],
        "key_claims": ["Highly pigmented", "Buildable", "Blendable", "Minimal fallout"],
        "raw_summary": "스웨덴 인디 뷰티 브랜드의 오로라 테마 12팬 아이섀도우 팔레트. 매트4+쉬머4+듀오크롬2+글리터2 구성. 탈크프리, EU 규제 완전 준수 필요. FSC 인증 포장재 사용. K-뷰티 트렌드 색상 조합 제안 요청."
    },
}


DEMO_QUOTATION = """## 견적서 초안 (Quotation Draft)

> ⚠️ 이 견적서는 AI가 생성한 초안입니다. 최종 견적은 R&D 실현성 검토 및 구매팀 가격 확인 후 확정됩니다.

### 1. 프로젝트 개요

| 항목 | 내용 |
|------|------|
| 제품 유형 | {product_type} |
| 제품명 | {product_name} |
| 셰이드 수 | {shade_count}색 |
| 마감 | {texture_finish} |
| 패키징 | {packaging_type} — {packaging_details} |
| 대상 시장 | {target_markets} |
| 특수 요구사항 | {special_requirements} |

### 2. 예상 원가 구조 (Per Unit)

| 항목 | 예상 단가 (USD) | 비고 |
|------|----------------|------|
| 원료비 (Raw Materials) | $0.80 ~ 1.20 | 색소, 왁스, 오일, 기능성 원료 |
| 포장재비 (Packaging) | $1.00 ~ 1.80 | 1차 포장 (튜브/컴팩트), 2차 제외 |
| 인건비 (Labor) | $0.30 ~ 0.50 | 제조/포장/검사 인력 |
| 제조간접비 (Overhead) | $0.20 ~ 0.35 | 설비 감가, 유틸리티, 임대 |
| R&D비 (Development) | $0.15 ~ 0.25 | 처방 개발, 안정성 시험 (총 MOQ 배분) |
| QC/규제비 (QA/Regulatory) | $0.10 ~ 0.20 | 품질검사, 시장별 인증/등록 |
| **합계** | **$2.55 ~ 4.30** | MOQ, 패키징 사양에 따라 변동 |

### 3. MOQ 및 리드타임

| 단계 | 기간 | 비고 |
|------|------|------|
| 처방 개발 (R&D) | 4~6주 | 기존 유사 처방 활용 시 단축 가능 |
| 샘플 승인 | 2~4주 (1차) | 평균 3~5회 수정 반복 |
| 안정성 시험 | 4~8주 | 가속 안정성 (45°C/75%RH) |
| 원료/포장재 조달 | 4~8주 | 특수 포장재의 경우 12주 |
| 양산 | 3~4주 | 셰이드 수에 따라 변동 |
| 출하/통관 | 1~3주 | 목적지 시장에 따라 |
| **총 리드타임** | **18~33주** | 샘플 승인 횟수에 따라 변동 |

### 4. 규제 사항 확인

| 시장 | 필수 인증/등록 | 예상 기간 | 비용 |
|------|--------------|----------|------|
| US | FDA MoCRA 시설 등록, 제품 등록 | 2~4주 | 포함 |
| EU | CPNP 등록, Responsible Person 지정 | 2~4주 | 별도 |
| CN | NMPA 비특수용도 화장품 등록 | 4~6개월 | 별도 견적 |
| KR | MFDS 화장품 제조판매 신고 | 2~4주 | 포함 |

### 5. 특이사항 및 권고

- **비건/크루얼티프리**: C&C는 동물실험 비수행 ODM. Leaping Bunny 인증 지원 가능.
- **클린뷰티**: Sephora Clean 기준 충족 처방 개발 경험 다수. 성분 제한 목록 사전 검토 포함.
- **PFAS-free**: 현재 PTFE-free 대체 처방 보유. EU PFAS 규제 선제 대응.
- **커스텀 패키징**: 전용 금형 개발 시 추가 6~8주 및 금형비 별도 (약 $3,000~8,000).
- **일정 주의**: 샘플 개발 시작 후 양산 납품까지 최소 18주. 역산 일정 확인 필요.

---

*C&C International | AI Labs 자동 생성 견적서 초안 | 최종 확정 전 R&D/구매팀 검토 필요*"""


def extract_specs_with_llm(rfq_text: str) -> dict:
    demo_mode = st.session_state.get("demo_mode", True)
    api_key = st.session_state.get("api_key", "")

    if demo_mode or not api_key:
        for sample_name, sample_text in SAMPLE_RFQS.items():
            if sample_text.strip()[:50] == rfq_text.strip()[:50]:
                return DEMO_EXTRACTIONS.get(sample_name, DEMO_EXTRACTIONS["글로벌 브랜드 매트 립스틱 RFQ"])
        return DEMO_EXTRACTIONS["글로벌 브랜드 매트 립스틱 RFQ"]

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": RFQ_EXTRACTION_PROMPT.format(rfq_text=rfq_text),
            }],
        )
        return json.loads(message.content[0].text)
    except Exception as e:
        st.error(f"API 호출 실패: {e}")
        return DEMO_EXTRACTIONS["글로벌 브랜드 매트 립스틱 RFQ"]


def generate_quotation_with_llm(specs: dict) -> str:
    demo_mode = st.session_state.get("demo_mode", True)
    api_key = st.session_state.get("api_key", "")

    if demo_mode or not api_key:
        return DEMO_QUOTATION.format(
            product_type=specs.get("product_type", "N/A"),
            product_name=specs.get("product_name", "N/A"),
            shade_count=specs.get("shade_count", "N/A"),
            texture_finish=specs.get("texture_finish", "N/A"),
            packaging_type=specs.get("packaging_type", "N/A"),
            packaging_details=specs.get("packaging_details", "N/A"),
            target_markets=", ".join(specs.get("target_markets", [])),
            special_requirements=", ".join(specs.get("special_requirements", [])),
        )

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,
            messages=[{
                "role": "user",
                "content": QUOTATION_PROMPT.format(specs_json=json.dumps(specs, ensure_ascii=False, indent=2)),
            }],
        )
        return message.content[0].text
    except Exception as e:
        return f"API 호출 실패: {e}\n\n데모 견적서로 대체합니다."


tab_parser, tab_samples = st.tabs(["📝 RFQ 파싱 + 견적서", "📄 샘플 RFQ 모음"])

with tab_parser:
    st.markdown("### 고객 RFQ 입력")

    input_method = st.radio(
        "입력 방식",
        ["샘플 RFQ 선택", "직접 입력"],
        horizontal=True,
    )

    if input_method == "샘플 RFQ 선택":
        sample_choice = st.selectbox("샘플 선택", list(SAMPLE_RFQS.keys()))
        rfq_text = st.text_area(
            "RFQ 내용 (수정 가능)",
            value=SAMPLE_RFQS[sample_choice],
            height=400,
        )
    else:
        rfq_text = st.text_area(
            "RFQ 내용 붙여넣기",
            placeholder="고객의 RFQ 이메일, 제품 브리프, 또는 사양서 내용을 붙여넣으세요.\n\n영어, 중국어, 한국어 모두 지원합니다.",
            height=400,
        )

    col1, col2 = st.columns(2)

    with col1:
        extract_btn = st.button("1️⃣ 사양 추출", type="primary", use_container_width=True)
    with col2:
        quotation_btn = st.button("2️⃣ 견적서 생성", type="secondary", use_container_width=True, disabled="extracted_specs" not in st.session_state)

    if extract_btn and rfq_text.strip():
        with st.spinner("RFQ 분석 중... (LLM이 제품 사양을 추출합니다)"):
            specs = extract_specs_with_llm(rfq_text)
            st.session_state["extracted_specs"] = specs

    if "extracted_specs" in st.session_state:
        specs = st.session_state["extracted_specs"]

        st.markdown("---")
        st.markdown("### 📊 추출된 제품 사양")

        col_left, col_right = st.columns(2)

        with col_left:
            st.markdown("#### 기본 정보")
            basic_df = pd.DataFrame([
                {"항목": "제품 유형", "값": specs.get("product_type", "")},
                {"항목": "제품명", "값": specs.get("product_name", "")},
                {"항목": "셰이드 수", "값": str(specs.get("shade_count", ""))},
                {"항목": "텍스처/마감", "값": specs.get("texture_finish", "")},
                {"항목": "패키징 유형", "값": specs.get("packaging_type", "")},
                {"항목": "패키징 상세", "값": specs.get("packaging_details", "")},
            ])
            st.dataframe(basic_df, use_container_width=True, hide_index=True)

        with col_right:
            st.markdown("#### 상업 조건")
            commercial_df = pd.DataFrame([
                {"항목": "타겟 단가", "값": specs.get("target_cost_usd", "")},
                {"항목": "MOQ", "값": specs.get("moq", "")},
                {"항목": "대상 시장", "값": ", ".join(specs.get("target_markets", []))},
                {"항목": "납기", "값": specs.get("delivery_timeline", "")},
            ])
            st.dataframe(commercial_df, use_container_width=True, hide_index=True)

        col_req, col_claim = st.columns(2)

        with col_req:
            st.markdown("#### 특수 요구사항")
            for req in specs.get("special_requirements", []):
                st.markdown(f"- {req}")

        with col_claim:
            st.markdown("#### 핵심 클레임")
            for claim in specs.get("key_claims", []):
                st.markdown(f"- {claim}")

        if specs.get("raw_summary"):
            st.info(f"**AI 요약**: {specs['raw_summary']}")

    if quotation_btn and "extracted_specs" in st.session_state:
        st.markdown("---")
        st.markdown("### 💰 AI 견적서 초안")

        with st.spinner("견적서 생성 중..."):
            quotation = generate_quotation_with_llm(st.session_state["extracted_specs"])

        st.markdown(quotation)

        st.download_button(
            label="📥 견적서 초안 다운로드 (Markdown)",
            data=quotation,
            file_name="quotation_draft.md",
            mime="text/markdown",
        )

with tab_samples:
    st.markdown("### 샘플 RFQ 모음")
    st.markdown("실제 ODM 영업 현장에서 수신하는 다양한 형태의 RFQ 예시입니다.")

    for name, text in SAMPLE_RFQS.items():
        with st.expander(f"📄 {name}"):
            st.text(text)
            st.markdown("---")
            if name in DEMO_EXTRACTIONS:
                demo = DEMO_EXTRACTIONS[name]
                st.markdown(f"**제품**: {demo['product_name']} | **셰이드**: {demo['shade_count']}색 | **시장**: {', '.join(demo['target_markets'])}")
                st.markdown(f"**요약**: {demo['raw_summary']}")
