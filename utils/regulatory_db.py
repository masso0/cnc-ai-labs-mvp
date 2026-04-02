"""
화장품 성분 규제 데이터베이스 (Cosmetics Ingredient Regulatory Database)

4개 시장의 주요 화장품 성분 규제 정보를 관리합니다:
- EU: Cosmetics Regulation (EC) No 1223/2009
- US: FDA / MoCRA (Modernization of Cosmetics Regulation Act)
- CN: NMPA (National Medical Products Administration)
- KR: MFDS (식품의약품안전처)

NOTE: 이 데이터베이스는 MVP 데모 목적입니다.
실제 규제 검증은 공인 데이터베이스(EU CosIng, KFDA 등)와 교차 확인이 필요합니다.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class RegulatoryStatus(Enum):
    ALLOWED = "허용"
    RESTRICTED = "제한적 허용"
    BANNED = "사용 금지"
    NOT_LISTED = "미등재/확인 필요"
    REQUIRES_NOTIFICATION = "사전 신고 필요"


@dataclass
class IngredientRegulation:
    """단일 성분의 시장별 규제 정보"""
    inci_name: str
    common_name_ko: str
    cas_number: str = ""
    function: str = ""
    # 시장별 규제 상태
    eu_status: RegulatoryStatus = RegulatoryStatus.NOT_LISTED
    us_status: RegulatoryStatus = RegulatoryStatus.NOT_LISTED
    cn_status: RegulatoryStatus = RegulatoryStatus.NOT_LISTED
    kr_status: RegulatoryStatus = RegulatoryStatus.NOT_LISTED
    # 상세 정보
    eu_max_concentration: str = ""
    us_max_concentration: str = ""
    cn_max_concentration: str = ""
    kr_max_concentration: str = ""
    eu_note: str = ""
    us_note: str = ""
    cn_note: str = ""
    kr_note: str = ""
    # 필수 라벨링
    required_labeling: list[str] = field(default_factory=list)
    # 카테고리
    category: str = ""  # preservative, colorant, UV filter, fragrance, etc.


# ============================================================
# 주요 화장품 규제 성분 데이터베이스
# ============================================================

REGULATORY_DATABASE: dict[str, IngredientRegulation] = {
    # ── 방부제 (Preservatives) ──
    "PHENOXYETHANOL": IngredientRegulation(
        inci_name="PHENOXYETHANOL",
        common_name_ko="페녹시에탄올",
        cas_number="122-99-6",
        function="방부제",
        category="preservative",
        eu_status=RegulatoryStatus.RESTRICTED,
        us_status=RegulatoryStatus.ALLOWED,
        cn_status=RegulatoryStatus.RESTRICTED,
        kr_status=RegulatoryStatus.RESTRICTED,
        eu_max_concentration="1.0%",
        us_max_concentration="제한 없음 (GRAS 판단)",
        cn_max_concentration="1.0%",
        kr_max_concentration="1.0%",
        eu_note="Annex V/29. 최대 1.0%. 3세 이하 어린이용 제품은 주의 라벨링 필요.",
        us_note="FDA는 일반적으로 안전(GRAS)으로 간주. 별도 농도 제한 없음.",
        cn_note="화장품 안전 기술 규범 표 4. 최대 1.0%.",
        kr_note="화장품 안전기준 별표 2. 최대 1.0%.",
    ),
    "METHYLPARABEN": IngredientRegulation(
        inci_name="METHYLPARABEN",
        common_name_ko="메틸파라벤",
        cas_number="99-76-3",
        function="방부제",
        category="preservative",
        eu_status=RegulatoryStatus.RESTRICTED,
        us_status=RegulatoryStatus.ALLOWED,
        cn_status=RegulatoryStatus.RESTRICTED,
        kr_status=RegulatoryStatus.RESTRICTED,
        eu_max_concentration="0.4% (단독) / 0.8% (파라벤 혼합 총합)",
        us_max_concentration="제한 없음",
        cn_max_concentration="0.4% (단독) / 0.8% (혼합 총합)",
        kr_max_concentration="0.4% (단독) / 0.8% (혼합 총합)",
        eu_note="Annex V/12. 3세 이하 기저귀 부위 사용 제품 금지 (propyl/butylparaben에 해당).",
        us_note="CIR에서 안전성 재확인(2019). FDA 별도 규제 없음.",
        cn_note="파라벤류 총합 0.8% 이내.",
        kr_note="파라벤류 총합 0.8% 이내. 배합한도 준수 필요.",
    ),
    "FORMALDEHYDE": IngredientRegulation(
        inci_name="FORMALDEHYDE",
        common_name_ko="포름알데히드",
        cas_number="50-00-0",
        function="방부제",
        category="preservative",
        eu_status=RegulatoryStatus.BANNED,
        us_status=RegulatoryStatus.RESTRICTED,
        cn_status=RegulatoryStatus.BANNED,
        kr_status=RegulatoryStatus.BANNED,
        eu_note="Annex II/1577. 2024년 8월부터 화장품 전면 사용 금지 (이전에는 0.2% 제한).",
        us_note="FDA는 네일 하드너에서 제한적 허용. OSHA 노출 기준 적용.",
        cn_note="화장품 사용 금지 성분 목록 등재.",
        kr_note="화장품 사용 금지 원료. 포름알데히드 방출 방부제도 제한.",
        required_labeling=["Contains Formaldehyde (EU, if >0.05% free formaldehyde from releasers)"],
    ),
    "METHYLISOTHIAZOLINONE": IngredientRegulation(
        inci_name="METHYLISOTHIAZOLINONE",
        common_name_ko="메틸이소치아졸리논 (MIT)",
        cas_number="2682-20-4",
        function="방부제",
        category="preservative",
        eu_status=RegulatoryStatus.RESTRICTED,
        us_status=RegulatoryStatus.ALLOWED,
        cn_status=RegulatoryStatus.RESTRICTED,
        kr_status=RegulatoryStatus.RESTRICTED,
        eu_max_concentration="0.0015% (린스오프 제품만)",
        cn_max_concentration="0.01%",
        kr_max_concentration="0.01% (린스오프), 사용 금지(리브온)",
        eu_note="Annex V/57. 리브온(leave-on) 제품 사용 금지. 린스오프(rinse-off)만 0.0015%.",
        us_note="CIR 안전성 검토 진행 중. 현재 별도 규제 없음.",
        cn_note="린스오프 제품 0.01% 이하.",
        kr_note="리브온 제품 사용 금지. 린스오프 제품 0.01% 이하.",
    ),

    # ── 자외선 차단제 (UV Filters) ──
    "BENZOPHENONE-3": IngredientRegulation(
        inci_name="BENZOPHENONE-3",
        common_name_ko="벤조페논-3 (옥시벤존)",
        cas_number="131-57-7",
        function="자외선 차단제",
        category="uv_filter",
        eu_status=RegulatoryStatus.RESTRICTED,
        us_status=RegulatoryStatus.RESTRICTED,
        cn_status=RegulatoryStatus.RESTRICTED,
        kr_status=RegulatoryStatus.RESTRICTED,
        eu_max_concentration="6.0% (2025년 이후 2.2%로 하향 예정)",
        us_max_concentration="6.0%",
        cn_max_concentration="10.0%",
        kr_max_concentration="5.0%",
        eu_note="Annex VI/4. 2025년 SCCS 의견에 따라 농도 하향 조정 진행 중.",
        us_note="FDA 모노그래프 GRASE Category I. 최대 6%.",
        cn_note="화장품 안전 기술 규범. 최대 10%.",
        kr_note="기능성 화장품 자외선 차단 원료. 최대 5%.",
        required_labeling=["Contains Benzophenone-3 (EU)"],
    ),
    "OCTOCRYLENE": IngredientRegulation(
        inci_name="OCTOCRYLENE",
        common_name_ko="옥토크릴렌",
        cas_number="6197-30-4",
        function="자외선 차단제",
        category="uv_filter",
        eu_status=RegulatoryStatus.RESTRICTED,
        us_status=RegulatoryStatus.RESTRICTED,
        cn_status=RegulatoryStatus.RESTRICTED,
        kr_status=RegulatoryStatus.RESTRICTED,
        eu_max_concentration="10.0% (산으로서)",
        us_max_concentration="10.0%",
        cn_max_concentration="10.0%",
        kr_max_concentration="10.0%",
        eu_note="Annex VI/10. 벤조페논 불순물 관리 필요.",
        us_note="FDA 모노그래프 GRASE. 최대 10%.",
        cn_note="최대 10% (산으로서).",
        kr_note="기능성 화장품 자외선 차단 원료. 최대 10%.",
    ),
    "TITANIUM DIOXIDE": IngredientRegulation(
        inci_name="TITANIUM DIOXIDE",
        common_name_ko="이산화티타늄",
        cas_number="13463-67-7",
        function="자외선 차단제 / 착색제",
        category="uv_filter",
        eu_status=RegulatoryStatus.RESTRICTED,
        us_status=RegulatoryStatus.ALLOWED,
        cn_status=RegulatoryStatus.RESTRICTED,
        kr_status=RegulatoryStatus.RESTRICTED,
        eu_max_concentration="25.0% (UV 필터) / CI 77891 (착색제)",
        us_max_concentration="25.0% (OTC sunscreen)",
        cn_max_concentration="25.0%",
        kr_max_concentration="25.0%",
        eu_note="Annex VI/27 (UV필터), Annex IV/143 (착색제 CI 77891). 나노 형태는 추가 안전성 평가 필요. 스프레이 제품 흡입 경로 사용 금지.",
        us_note="FDA OTC 자외선 차단 원료 GRASE. 착색제로도 허용 (21 CFR 73.2575).",
        cn_note="자외선 차단 원료. 나노 형태 별도 안전성 자료 제출 필요.",
        kr_note="자외선 차단 원료 및 착색제. 나노입자 별도 심사.",
        required_labeling=["[nano] 표기 필요 (EU, 나노 형태 사용 시)"],
    ),

    # ── 착색제 (Colorants) — 색조 화장품 ODM 핵심 ──
    "CI 77491": IngredientRegulation(
        inci_name="CI 77491",
        common_name_ko="산화철 (적색)",
        cas_number="1309-37-1",
        function="착색제 (Iron Oxide Red)",
        category="colorant",
        eu_status=RegulatoryStatus.ALLOWED,
        us_status=RegulatoryStatus.ALLOWED,
        cn_status=RegulatoryStatus.ALLOWED,
        kr_status=RegulatoryStatus.ALLOWED,
        eu_note="Annex IV. 화장품 전반 사용 허용. 중금속 순도 기준 적용 (Pb<20ppm, As<5ppm 등).",
        us_note="21 CFR 73.2250. 눈 포함 전 부위 사용 허용. FDA 배치 인증 불요.",
        cn_note="화장품 착색제 목록 등재. 순도 기준 적용.",
        kr_note="화장품 착색제. 중금속 순도 기준 충족 필요.",
    ),
    "CI 77492": IngredientRegulation(
        inci_name="CI 77492",
        common_name_ko="산화철 (황색)",
        cas_number="51274-00-1",
        function="착색제 (Iron Oxide Yellow)",
        category="colorant",
        eu_status=RegulatoryStatus.ALLOWED,
        us_status=RegulatoryStatus.ALLOWED,
        cn_status=RegulatoryStatus.ALLOWED,
        kr_status=RegulatoryStatus.ALLOWED,
        eu_note="Annex IV. 화장품 전반 사용 허용.",
        us_note="21 CFR 73.2250. 전 부위 허용.",
        cn_note="화장품 착색제 목록 등재.",
        kr_note="화장품 착색제.",
    ),
    "CI 77499": IngredientRegulation(
        inci_name="CI 77499",
        common_name_ko="산화철 (흑색)",
        cas_number="1317-61-9",
        function="착색제 (Iron Oxide Black)",
        category="colorant",
        eu_status=RegulatoryStatus.ALLOWED,
        us_status=RegulatoryStatus.ALLOWED,
        cn_status=RegulatoryStatus.ALLOWED,
        kr_status=RegulatoryStatus.ALLOWED,
        eu_note="Annex IV. 화장품 전반 사용 허용.",
        us_note="21 CFR 73.2250. 전 부위 허용.",
        cn_note="화장품 착색제 목록 등재.",
        kr_note="화장품 착색제.",
    ),
    "CARMINE": IngredientRegulation(
        inci_name="CARMINE",
        common_name_ko="카민 (CI 75470)",
        cas_number="1390-65-4",
        function="착색제 (천연 적색)",
        category="colorant",
        eu_status=RegulatoryStatus.ALLOWED,
        us_status=RegulatoryStatus.ALLOWED,
        cn_status=RegulatoryStatus.ALLOWED,
        kr_status=RegulatoryStatus.ALLOWED,
        eu_note="Annex IV/73. 화장품 전반 사용 허용. 코치닐 추출물에서 유래.",
        us_note="21 CFR 73.2087. FDA 배치 인증 면제. 알레르기 주의 라벨 권고.",
        cn_note="화장품 착색제 허용.",
        kr_note="화장품 착색제 허용. 비건/할랄 인증 시 사용 불가 (동물 유래).",
        required_labeling=["알레르기 유발 가능 (FDA 권고)", "비건/할랄 비적합 (동물 유래 원료)"],
    ),
    "CI 15850": IngredientRegulation(
        inci_name="CI 15850",
        common_name_ko="D&C Red No. 7 Calcium Lake",
        cas_number="5281-04-9",
        function="착색제 (합성 적색)",
        category="colorant",
        eu_status=RegulatoryStatus.RESTRICTED,
        us_status=RegulatoryStatus.RESTRICTED,
        cn_status=RegulatoryStatus.RESTRICTED,
        kr_status=RegulatoryStatus.RESTRICTED,
        eu_max_concentration="3.0%",
        us_max_concentration="사용 부위 제한",
        cn_max_concentration="3.0%",
        kr_max_concentration="3.0%",
        eu_note="Annex IV. 립 제품, 외용 제품에 제한적 허용. 최대 3%.",
        us_note="D&C Red No. 7: 입술 및 외용에만 허용. 눈 주위 불가. FDA 배치 인증 필요.",
        cn_note="색조 화장품용. 최대 3%. 눈 주위 제품 제한.",
        kr_note="색조 화장품 착색제. 배합한도 3%.",
    ),
    "CI 42090": IngredientRegulation(
        inci_name="CI 42090",
        common_name_ko="FD&C Blue No. 1 (브릴리언트 블루)",
        cas_number="3844-45-9",
        function="착색제 (합성 청색)",
        category="colorant",
        eu_status=RegulatoryStatus.ALLOWED,
        us_status=RegulatoryStatus.RESTRICTED,
        cn_status=RegulatoryStatus.ALLOWED,
        kr_status=RegulatoryStatus.ALLOWED,
        eu_note="Annex IV. 화장품 전반 허용.",
        us_note="FD&C Blue No. 1: 전 부위 허용이나 FDA 배치 인증 필수 (certified color).",
        cn_note="화장품 착색제 허용 목록 등재.",
        kr_note="화장품 착색제 허용.",
        required_labeling=["FDA 배치 인증 필수 (미국 수출 시)"],
    ),

    # ── 향료/알레르겐 (Fragrance Allergens) ──
    "LINALOOL": IngredientRegulation(
        inci_name="LINALOOL",
        common_name_ko="리날로올",
        cas_number="78-70-6",
        function="향료 성분",
        category="fragrance_allergen",
        eu_status=RegulatoryStatus.RESTRICTED,
        us_status=RegulatoryStatus.ALLOWED,
        cn_status=RegulatoryStatus.ALLOWED,
        kr_status=RegulatoryStatus.RESTRICTED,
        eu_note="Annex III/89. 리브온 0.001% 초과, 린스오프 0.01% 초과 시 표시 의무.",
        us_note="별도 규제 없음. 향료 성분으로 사용 가능.",
        cn_note="별도 농도 제한 없음.",
        kr_note="알레르기 유발 성분. 함유 시 표시 의무 (0.001%/0.01% 기준).",
        required_labeling=["EU/KR: 알레르기 유발 향료 표시 의무"],
    ),
    "LIMONENE": IngredientRegulation(
        inci_name="LIMONENE",
        common_name_ko="리모넨",
        cas_number="5989-27-5",
        function="향료 성분",
        category="fragrance_allergen",
        eu_status=RegulatoryStatus.RESTRICTED,
        us_status=RegulatoryStatus.ALLOWED,
        cn_status=RegulatoryStatus.ALLOWED,
        kr_status=RegulatoryStatus.RESTRICTED,
        eu_note="Annex III/88. 리브온 0.001% 초과, 린스오프 0.01% 초과 시 표시 의무.",
        us_note="별도 규제 없음.",
        cn_note="별도 농도 제한 없음.",
        kr_note="알레르기 유발 성분. 표시 의무.",
        required_labeling=["EU/KR: 알레르기 유발 향료 표시 의무"],
    ),
    "CITRAL": IngredientRegulation(
        inci_name="CITRAL",
        common_name_ko="시트랄",
        cas_number="5392-40-5",
        function="향료 성분",
        category="fragrance_allergen",
        eu_status=RegulatoryStatus.RESTRICTED,
        us_status=RegulatoryStatus.ALLOWED,
        cn_status=RegulatoryStatus.ALLOWED,
        kr_status=RegulatoryStatus.RESTRICTED,
        eu_note="Annex III/87. 알레르기 유발 향료. 표시 의무.",
        us_note="별도 규제 없음.",
        cn_note="별도 농도 제한 없음.",
        kr_note="알레르기 유발 성분. 표시 의무.",
        required_labeling=["EU/KR: 알레르기 유발 향료 표시 의무"],
    ),

    # ── 기능성 원료 ──
    "RETINOL": IngredientRegulation(
        inci_name="RETINOL",
        common_name_ko="레티놀",
        cas_number="68-26-8",
        function="항노화 / 기능성 원료",
        category="active",
        eu_status=RegulatoryStatus.RESTRICTED,
        us_status=RegulatoryStatus.ALLOWED,
        cn_status=RegulatoryStatus.RESTRICTED,
        kr_status=RegulatoryStatus.RESTRICTED,
        eu_max_concentration="0.3% (페이스), 0.05% (바디)",
        us_max_concentration="제한 없음 (화장품 범주)",
        cn_max_concentration="0.5%",
        kr_max_concentration="2,500 IU/g (기능성 화장품)",
        eu_note="2025년 EU 규제 강화: 페이스 0.3%, 바디 0.05% 상한. 립/아이 제품 금지.",
        us_note="FDA는 OTC 여드름 약에서 규제. 화장품으로는 제한 없음.",
        cn_note="NMPA 등록 필요. 최대 0.5%.",
        kr_note="기능성 화장품 원료. 주름 개선 기능. 2,500 IU/g 이하.",
        required_labeling=["EU: 임산부 사용 주의 경고문 필수", "KR: 기능성 화장품 심사 필요"],
    ),
    "SALICYLIC ACID": IngredientRegulation(
        inci_name="SALICYLIC ACID",
        common_name_ko="살리실산",
        cas_number="69-72-7",
        function="각질제거제 / 방부제",
        category="active",
        eu_status=RegulatoryStatus.RESTRICTED,
        us_status=RegulatoryStatus.RESTRICTED,
        cn_status=RegulatoryStatus.RESTRICTED,
        kr_status=RegulatoryStatus.RESTRICTED,
        eu_max_concentration="2.0% (린스오프), 2.0% (기타 용도 방부)",
        us_max_concentration="2.0% (OTC 여드름)",
        cn_max_concentration="2.0%",
        kr_max_concentration="0.5% (화장품) / 2.0% (기능성)",
        eu_note="Annex III/98. 3세 이하 어린이 제품 사용 금지.",
        us_note="OTC 여드름 약물(0.5-2.0%) 또는 화장품 성분으로 사용.",
        cn_note="최대 2.0%. 3세 이하 어린이 제품 불가.",
        kr_note="화장품 0.5% 이하, 기능성(각질제거) 2.0% 이하.",
        required_labeling=["EU: '3세 이하 사용 금지' 경고문"],
    ),
    "NIACINAMIDE": IngredientRegulation(
        inci_name="NIACINAMIDE",
        common_name_ko="나이아신아마이드",
        cas_number="98-92-0",
        function="미백/보습 기능성 원료",
        category="active",
        eu_status=RegulatoryStatus.ALLOWED,
        us_status=RegulatoryStatus.ALLOWED,
        cn_status=RegulatoryStatus.ALLOWED,
        kr_status=RegulatoryStatus.RESTRICTED,
        eu_note="별도 농도 제한 없음. 안전한 화장품 성분으로 간주.",
        us_note="제한 없음. 널리 사용됨.",
        cn_note="제한 없음. 미백 기능성으로 등록 시 별도 절차.",
        kr_note="기능성 화장품(미백) 원료. 2~5% 사용 시 기능성 심사 필요.",
        kr_max_concentration="기능성 심사 시 2~5%",
        required_labeling=["KR: 미백 기능성 화장품 심사 필요 (2% 이상)"],
    ),

    # ── 기초 원료 (Base Ingredients) ──
    "DIMETHICONE": IngredientRegulation(
        inci_name="DIMETHICONE",
        common_name_ko="디메치콘 (실리콘)",
        cas_number="9006-65-9",
        function="피부 컨디셔닝제 / 에몰리언트",
        category="base",
        eu_status=RegulatoryStatus.ALLOWED,
        us_status=RegulatoryStatus.ALLOWED,
        cn_status=RegulatoryStatus.ALLOWED,
        kr_status=RegulatoryStatus.ALLOWED,
        eu_note="제한 없음. Annex 해당사항 없음.",
        us_note="제한 없음. 널리 사용됨.",
        cn_note="제한 없음.",
        kr_note="제한 없음.",
    ),
    "ISODODECANE": IngredientRegulation(
        inci_name="ISODODECANE",
        common_name_ko="이소도데칸",
        cas_number="31807-55-3",
        function="용매 / 에몰리언트",
        category="base",
        eu_status=RegulatoryStatus.ALLOWED,
        us_status=RegulatoryStatus.ALLOWED,
        cn_status=RegulatoryStatus.ALLOWED,
        kr_status=RegulatoryStatus.ALLOWED,
        eu_note="색조 화장품(립틴트, 파운데이션)에 널리 사용. 제한 없음.",
        us_note="제한 없음.",
        cn_note="제한 없음.",
        kr_note="제한 없음.",
    ),
    "CASTOR OIL": IngredientRegulation(
        inci_name="RICINUS COMMUNIS SEED OIL",
        common_name_ko="피마자유 (캐스터 오일)",
        cas_number="8001-79-4",
        function="에몰리언트 / 바인더",
        category="base",
        eu_status=RegulatoryStatus.ALLOWED,
        us_status=RegulatoryStatus.ALLOWED,
        cn_status=RegulatoryStatus.ALLOWED,
        kr_status=RegulatoryStatus.ALLOWED,
        eu_note="립스틱의 주요 기제 성분. 제한 없음.",
        us_note="제한 없음. GRAS.",
        cn_note="제한 없음.",
        kr_note="제한 없음.",
    ),

    # ── 유해 우려 성분 ──
    "HYDROQUINONE": IngredientRegulation(
        inci_name="HYDROQUINONE",
        common_name_ko="하이드로퀴논",
        cas_number="123-31-9",
        function="미백제",
        category="active",
        eu_status=RegulatoryStatus.BANNED,
        us_status=RegulatoryStatus.RESTRICTED,
        cn_status=RegulatoryStatus.BANNED,
        kr_status=RegulatoryStatus.BANNED,
        us_max_concentration="2.0% (OTC 약품으로만)",
        eu_note="Annex II/1339. 화장품 사용 전면 금지 (미용 목적). 네일 시스템 제외.",
        us_note="OTC 피부 미백 약품으로만 2.0% 허용. 화장품 불가. MoCRA 강화 검토 중.",
        cn_note="화장품 사용 금지.",
        kr_note="화장품 사용 금지 원료.",
    ),
    "LEAD ACETATE": IngredientRegulation(
        inci_name="LEAD ACETATE",
        common_name_ko="초산납",
        cas_number="6080-56-4",
        function="착색제 (구 염모제)",
        category="heavy_metal",
        eu_status=RegulatoryStatus.BANNED,
        us_status=RegulatoryStatus.BANNED,
        cn_status=RegulatoryStatus.BANNED,
        kr_status=RegulatoryStatus.BANNED,
        eu_note="Annex II. 납 화합물 전면 금지.",
        us_note="2022년 FDA 최종 규칙으로 사용 금지 확정 (이전에는 헤어 다이에 허용).",
        cn_note="중금속 화합물 사용 금지.",
        kr_note="사용 금지 원료.",
    ),
    "TALC": IngredientRegulation(
        inci_name="TALC",
        common_name_ko="탈크",
        cas_number="14807-96-6",
        function="벌킹제 / 흡수제",
        category="base",
        eu_status=RegulatoryStatus.ALLOWED,
        us_status=RegulatoryStatus.RESTRICTED,
        cn_status=RegulatoryStatus.ALLOWED,
        kr_status=RegulatoryStatus.ALLOWED,
        eu_note="화장품 사용 허용. 석면 비검출 필수. 분말 제품 흡입 주의.",
        us_note="MoCRA(2024) 이후 석면 비검출 테스트 의무화. FDA 강화 감시 대상.",
        cn_note="화장품 사용 허용. 순도 기준 적용.",
        kr_note="화장품 사용 허용. 석면 불검출 기준 충족 필요.",
        required_labeling=["석면(asbestos) 비검출 시험 필수 (전 시장)"],
    ),

    # ── PFAS 관련 ──
    "PTFE": IngredientRegulation(
        inci_name="PTFE",
        common_name_ko="폴리테트라플루오로에틸렌 (테플론)",
        cas_number="9002-84-0",
        function="텍스처 개선제",
        category="base",
        eu_status=RegulatoryStatus.RESTRICTED,
        us_status=RegulatoryStatus.ALLOWED,
        cn_status=RegulatoryStatus.ALLOWED,
        kr_status=RegulatoryStatus.ALLOWED,
        eu_note="EU PFAS 규제 제안(2023) 진행 중. 향후 사용 제한 가능성 높음. 클린뷰티 트렌드에서 기피.",
        us_note="현재 규제 없음. 캘리포니아 등 주 단위 PFAS 금지 법안 진행 중.",
        cn_note="현재 제한 없음.",
        kr_note="현재 제한 없음. 향후 규제 동향 모니터링 필요.",
        required_labeling=["EU PFAS 규제 모니터링 필요 (2025-2027 시행 예상)"],
    ),
}


# ============================================================
# 검색 / 조회 함수
# ============================================================

def normalize_inci_name(name: str) -> str:
    """INCI 이름 정규화 (대문자 변환, 앞뒤 공백 제거)"""
    return name.strip().upper()


def search_ingredient(query: str) -> list[IngredientRegulation]:
    """성분명으로 검색 (INCI명, 한국어명 모두 검색)"""
    query_upper = normalize_inci_name(query)
    results = []
    for key, reg in REGULATORY_DATABASE.items():
        if (query_upper in key or
            query_upper in reg.inci_name.upper() or
            query in reg.common_name_ko or
            query_upper in reg.cas_number):
            results.append(reg)
    return results


def check_ingredient(inci_name: str) -> Optional[IngredientRegulation]:
    """정확한 INCI명으로 규제 정보 조회"""
    key = normalize_inci_name(inci_name)
    # 직접 매칭
    if key in REGULATORY_DATABASE:
        return REGULATORY_DATABASE[key]
    # INCI명 매칭
    for reg in REGULATORY_DATABASE.values():
        if normalize_inci_name(reg.inci_name) == key:
            return reg
    return None


def get_all_ingredients() -> list[IngredientRegulation]:
    """전체 성분 목록 반환"""
    return list(REGULATORY_DATABASE.values())


def get_ingredients_by_category(category: str) -> list[IngredientRegulation]:
    """카테고리별 성분 목록 반환"""
    return [reg for reg in REGULATORY_DATABASE.values() if reg.category == category]


# ============================================================
# 데모용 샘플 포뮬라
# ============================================================

SAMPLE_FORMULAS = {
    "매트 립스틱 (Matte Lipstick)": [
        ("RICINUS COMMUNIS SEED OIL", "25.0%"),
        ("ISODODECANE", "15.0%"),
        ("DIMETHICONE", "8.0%"),
        ("CANDELILLA CERA", "6.0%"),
        ("CI 77491", "5.0%"),
        ("CI 77492", "2.0%"),
        ("CI 77499", "1.0%"),
        ("CI 15850", "2.5%"),
        ("PHENOXYETHANOL", "0.8%"),
        ("TOCOPHERYL ACETATE", "0.5%"),
        ("LINALOOL", "0.005%"),
        ("LIMONENE", "0.003%"),
    ],
    "쿠션 파운데이션 (Cushion Foundation)": [
        ("WATER", "45.0%"),
        ("CYCLOPENTASILOXANE", "12.0%"),
        ("TITANIUM DIOXIDE", "8.0%"),
        ("CI 77491", "2.0%"),
        ("CI 77492", "1.5%"),
        ("CI 77499", "0.3%"),
        ("NIACINAMIDE", "3.0%"),
        ("DIMETHICONE", "5.0%"),
        ("PHENOXYETHANOL", "0.9%"),
        ("TALC", "4.0%"),
        ("SALICYLIC ACID", "0.3%"),
        ("LINALOOL", "0.002%"),
    ],
    "젤 아이라이너 (Gel Eyeliner)": [
        ("ISODODECANE", "30.0%"),
        ("DIMETHICONE", "10.0%"),
        ("CI 77499", "15.0%"),
        ("CI 77491", "3.0%"),
        ("CI 42090", "1.0%"),
        ("PTFE", "2.0%"),
        ("CARMINE", "1.5%"),
        ("METHYLPARABEN", "0.3%"),
        ("RETINOL", "0.01%"),
    ],
}
