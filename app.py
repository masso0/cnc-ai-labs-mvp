import streamlit as st

st.set_page_config(
    page_title="C&C AI Labs | ODM 업무 자동화 MVP",
    page_icon="💄",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.markdown(
    """
    ### C&C AI Labs
    **ODM 업무 자동화 MVP**

    ---
    **씨앤씨인터내셔널** AI Labs 인턴십 지원 프로젝트

    색조 화장품 ODM 핵심 업무를 AI로 자동화하는 프로토타입입니다.

    ---
    *Built with Streamlit + Claude API*
    """
)

demo_mode = st.sidebar.toggle("데모 모드 (API 키 없이 체험)", value=True)
st.session_state["demo_mode"] = demo_mode

if not demo_mode:
    api_key = st.sidebar.text_input("Anthropic API Key", type="password")
    if api_key:
        st.session_state["api_key"] = api_key

st.markdown("# C&C International AI Labs")
st.markdown("### 색조 화장품 ODM 영업 자동화 MVP")
st.markdown("---")

st.markdown(
    """
    <div style="background: linear-gradient(135deg, #FF4B6E 0%, #FF8F6B 100%); padding: 24px 28px; border-radius: 12px; color: white; margin-bottom: 24px;">
        <h3 style="margin:0 0 8px 0; color: white;">핵심 문제: 영업팀의 RFQ 처리 병목</h3>
        <p style="margin:0; font-size:16px; opacity:0.95;">
            C&C인터내셔널은 100+ 글로벌 브랜드에 색조 화장품을 공급합니다.<br>
            매일 수신되는 RFQ(견적 요청서)를 <b>수동으로 파싱하고 BOM 원가를 계산하여 견적서를 작성</b>하는 데<br>
            영업사원 1인당 <b>건당 12시간 이상</b>이 소요됩니다. 월 30~50건 × 12시간 = <b>월 360~600시간의 반복 업무.</b>
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("### 자동화 워크플로우")

col_before, col_arrow, col_after = st.columns([5, 1, 5])

with col_before:
    st.markdown(
        """
        <div style="background: #FFF3F3; border: 2px solid #FF4B6E; border-radius: 10px; padding: 20px;">
            <h4 style="color: #FF4B6E; margin-top:0;">❌ 기존 프로세스 (수동)</h4>
            <div style="font-size:14px;">
                <b>Step 1.</b> 이메일/PDF RFQ 수신 (EN/ZH/FR 다국어)<br>
                <b>Step 2.</b> 제품 사양 수동 파싱 → Excel 정리 <span style="color:#FF4B6E;">⏱ 2~4시간</span><br>
                <b>Step 3.</b> BOM 원가 수동 계산 (원료+포장+인건비) <span style="color:#FF4B6E;">⏱ 3~5시간</span><br>
                <b>Step 4.</b> 규제 검토 (4개국 수동 교차확인) <span style="color:#FF4B6E;">⏱ 1~3시간</span><br>
                <b>Step 5.</b> 견적서 작성 + 내부 검토 <span style="color:#FF4B6E;">⏱ 2~4시간</span><br>
                <hr style="border-color:#FF4B6E40;">
                <b style="color:#FF4B6E;">총 소요: 건당 12시간+ / 응답까지 2~5일</b>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_arrow:
    st.markdown(
        "<div style='display:flex; align-items:center; justify-content:center; height:280px; font-size:36px;'>→</div>",
        unsafe_allow_html=True,
    )

with col_after:
    st.markdown(
        """
        <div style="background: #F0FFF4; border: 2px solid #38A169; border-radius: 10px; padding: 20px;">
            <h4 style="color: #38A169; margin-top:0;">✅ AI 자동화 프로세스</h4>
            <div style="font-size:14px;">
                <b>Step 1.</b> RFQ 텍스트 붙여넣기 (다국어 자동 인식)<br>
                <b>Step 2.</b> LLM이 제품 사양 자동 추출 <span style="color:#38A169;">⏱ 10초</span><br>
                <b>Step 3.</b> 제품별 BOM 원가 자동 계산 <span style="color:#38A169;">⏱ 즉시</span><br>
                <b>Step 4.</b> 4축 리스크 자동 평가 (납기/규제/원가/기술) <span style="color:#38A169;">⏱ 즉시</span><br>
                <b>Step 5.</b> 견적서 초안 자동 생성 <span style="color:#38A169;">⏱ 5초</span><br>
                <hr style="border-color:#38A16940;">
                <b style="color:#38A169;">총 소요: 건당 2분 / 영업사원은 검토+승인만</b>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("")

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric("처리 시간", "2분", delta="-12시간", delta_color="inverse")
col_m2.metric("응답 속도", "즉시", delta="-2~5일", delta_color="inverse")
col_m3.metric("BOM 정확도", "제품별 맞춤", delta="generic 탈피")
col_m4.metric("리스크 감지", "자동 4축 분석", delta="수동→자동")

st.markdown("---")

st.markdown("### 👉 지금 바로 체험해보세요")
st.markdown("좌측 사이드바에서 **RFQ 자동 파서** 페이지로 이동하면, 3개 샘플 RFQ로 전체 파이프라인을 데모할 수 있습니다.")

col_demo1, col_demo2, col_demo3 = st.columns(3)

with col_demo1:
    st.markdown(
        """
        **🇺🇸 미국 브랜드 — 매트 립스틱**
        - 12색 벨벳 매트 컬렉션
        - 비건 / 세포라 클린 / PFAS-free
        - 리스크: ⚠️ MEDIUM
        """
    )

with col_demo2:
    st.markdown(
        """
        **🇨🇳 중국 브랜드 — 쿠션 파운데이션**
        - 8색 SPF50+ PA++++
        - NMPA 등록 + 할랄 인증
        - 리스크: 🚨 HIGH
        """
    )

with col_demo3:
    st.markdown(
        """
        **🇪🇺 유럽 인디 — 아이섀도우 팔레트**
        - 12팬 (매트/쉬머/듀오크롬/글리터)
        - 탈크프리 + FSC 인증 포장
        - 리스크: ⚠️ MEDIUM
        """
    )

st.markdown("---")

st.markdown(
    """
    ### MVP 기술 스택

    | 구성 요소 | 기술 | 역할 |
    |----------|------|------|
    | **AI 엔진** | Claude API (Anthropic) | RFQ 파싱, 사양 추출, 견적서 생성 |
    | **BOM 원가 엔진** | Python (자체 개발) | 제품 유형별 원가 자동 계산 (6개 카테고리) |
    | **리스크 엔진** | Python (자체 개발) | 4축 리스크 스코어링 (납기/규제/원가/기술) |
    | **규제 DB** | Python (자체 개발) | 7개 시장 규제 요구사항 + EU/US/CN/KR 성분 DB |
    | **UI** | Streamlit | 인터랙티브 웹 앱 + Plotly 시각화 |

    ### 프로젝트 배경

    | 항목 | 내용 |
    |------|------|
    | **회사** | 씨앤씨인터내셔널 (KOSDAQ:352480) — 한국 색조 화장품 ODM 1위 |
    | **매출** | 2,885억원 (FY2025, 역대 최고) / 100+ 글로벌 브랜드 고객 |
    | **최근 변화** | SAP ERP 도입 (2026.1), PE 인수 (PACM+신세계), 청주 신공장 ₩790억 착공 |
    | **핵심 이슈** | 다품종 소량 생산 비효율 → 영업이익 41.5%↓ (삼성증권 지적) |
    | **AI 기회** | 영업 자동화, 규제 검증, 생산 스케줄 최적화, 경영 리포트 자동화 |

    > 이 MVP는 C&C인터내셔널 AI Labs 인턴십 지원을 위해 제작되었습니다.
    > 뷰티 ODM 업계의 실제 Pain Point를 분석하고, 영업팀 RFQ 처리 자동화를 기획·구현한 프로토타입입니다.
    """
)
