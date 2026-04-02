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
st.markdown("### 색조 화장품 ODM 업무 자동화 MVP")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        ### 1. 화장품 성분 규제 검증 시스템
        INCI 성분 리스트를 입력하면 **EU / 미국 / 중국 / 한국** 4개 시장의
        규제 적합성을 동시에 검증합니다.

        **해결하는 문제**: R&D/QA팀이 수동으로 4개 시장 규제 DB를
        교차 확인하던 작업을 자동화. 1건의 미스 = 제품 리콜 리스크.

        **기술 스택**: Claude API + 규제 DB + Streamlit

        👉 좌측 사이드바에서 **규제 성분 검증** 페이지로 이동하세요.
        """
    )

with col2:
    st.markdown(
        """
        ### 2. RFQ 자동 파서 + 견적서 생성
        글로벌 고객의 제품 브리프(RFQ)를 업로드하면 **제품 사양을
        자동 추출**하고 **견적서 초안**을 생성합니다.

        **해결하는 문제**: 영업팀이 수동으로 RFQ 파싱 (2~5일) →
        견적서 작성하던 과정을 2시간 이내로 단축.

        **기술 스택**: Claude API + 구조화 파싱 + Streamlit

        👉 좌측 사이드바에서 **RFQ 자동 파서** 페이지로 이동하세요.
        """
    )

st.markdown("---")

st.markdown(
    """
    ### 프로젝트 배경

    | 항목 | 내용 |
    |------|------|
    | **회사** | 씨앤씨인터내셔널 (KOSDAQ:352480) — 한국 색조 화장품 ODM 1위 |
    | **매출** | 2,885억원 (FY2025, 역대 최고) |
    | **고객** | 100+ 글로벌 브랜드 (아모레퍼시픽, 3CE, CLIO, 로레알 등) |
    | **최근 변화** | SAP ERP 도입 (2026.1), PE 인수, 청주 신공장 착공 |
    | **AI 기회** | 다품종 소량 생산 비효율 해소, 규제 자동화, 영업 생산성 향상 |

    > 이 MVP는 C&C인터내셔널 AI Labs 인턴십 지원을 위해 제작되었습니다.
    > 뷰티 ODM 업계의 실제 Pain Point를 분석하고, LLM(Claude) API를 활용한
    > 업무 자동화 솔루션을 기획·구현한 프로토타입입니다.
    """
)
