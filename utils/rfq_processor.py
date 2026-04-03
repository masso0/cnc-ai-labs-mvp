import json
from dataclasses import dataclass, field


@dataclass
class RFQExtraction:
    product_type: str = ""
    product_name: str = ""
    shade_count: int = 0
    texture_finish: str = ""
    packaging_type: str = ""
    packaging_details: str = ""
    target_cost_usd: str = ""
    moq: str = ""
    target_markets: list[str] = field(default_factory=list)
    delivery_timeline: str = ""
    special_requirements: list[str] = field(default_factory=list)
    key_claims: list[str] = field(default_factory=list)
    raw_summary: str = ""


RFQ_EXTRACTION_PROMPT = """You are an expert cosmetics ODM (Original Design Manufacturer) sales coordinator.
You specialize in parsing product briefs and RFQs (Request for Quotation) from global beauty brand clients.

Extract the following structured information from the client's RFQ below.
If information is not explicitly stated, infer reasonable defaults based on industry standards and mark as "[추정]".

Return ONLY valid JSON with this exact structure:
{
  "product_type": "lipstick | lip_tint | lip_gloss | foundation | cushion_foundation | eyeshadow | eyeliner | mascara | blush | concealer | other",
  "product_name": "client's product name or description",
  "shade_count": 0,
  "texture_finish": "matte | glossy | satin | velvet | dewy | shimmer | cream | powder | gel",
  "packaging_type": "tube | bullet | compact | cushion | pencil | pot | stick | pan",
  "packaging_details": "any specific packaging requirements",
  "target_cost_usd": "per unit cost target or range",
  "moq": "minimum order quantity per shade",
  "target_markets": ["US", "EU", "CN", "KR", "JP", "SEA", "ME"],
  "delivery_timeline": "requested delivery timeline",
  "special_requirements": ["vegan", "cruelty-free", "clean beauty", "halal", "paraben-free", etc.],
  "key_claims": ["long-wear", "transfer-proof", "hydrating", "SPF", etc.],
  "raw_summary": "1-2 sentence summary of the RFQ in Korean"
}

CLIENT RFQ:
---
{rfq_text}
---

Return ONLY the JSON object. No explanation."""


QUOTATION_PROMPT = """You are a senior cosmetics ODM quotation specialist at C&C International, Korea's #1 color cosmetics ODM.
Based on the extracted RFQ specifications, generate a professional quotation draft in Korean.

EXTRACTED SPECIFICATIONS:
{specs_json}

Generate a quotation draft with the following sections. Use realistic industry-standard pricing.
Write in Korean. Be professional but detailed.

Format your response as follows:

## 견적서 초안 (Quotation Draft)

### 1. 프로젝트 개요
- 제품 유형, 셰이드 수, 마감, 패키징 요약

### 2. 예상 원가 구조 (Per Unit)
Create a cost breakdown table:
| 항목 | 예상 단가 (USD) | 비고 |
|------|----------------|------|
| 원료비 (Raw Materials) | | 색소, 왁스, 오일 등 |
| 포장재비 (Packaging) | | 1차/2차 포장 |
| 인건비 (Labor) | | 제조/포장 인력 |
| 제조간접비 (Overhead) | | 설비, 유틸리티 |
| R&D비 (Development) | | 처방 개발, 안정성 시험 |
| QC/규제비 (QA/Regulatory) | | 품질검사, 인증 |
| **합계** | | |

### 3. MOQ 및 리드타임
- MOQ per shade
- 샘플 개발: X주
- 양산 리드타임: X주

### 4. 규제 사항 확인
- 대상 시장별 필수 인증/등록 사항
- 주요 규제 리스크 (성분 제한 등)

### 5. 특이사항 및 권고
- Clean beauty/비건 등 특수 요구사항 대응 방안
- 패키징 관련 권고사항
- 일정 관련 주의사항

NOTE: This is an AI-generated draft for internal review. Final quotation requires R&D feasibility check and procurement team pricing confirmation."""


BOM_COST_DB = {
    "lipstick": {
        "label": "립스틱 (Bullet Lipstick)",
        "raw_materials": {"min": 0.80, "max": 1.20, "note": "왁스(카나우바/칸델릴라), 오일(캐스터), 색소(CI 77491/77492/77499), 에몰리언트"},
        "packaging": {"min": 0.80, "max": 1.50, "note": "불릿 튜브, 캡, 자석 클로저. 소프트터치/각인 시 +$0.3"},
        "labor": {"min": 0.25, "max": 0.40, "note": "혼합→몰딩→탈형→조립→검사. 라인 속도 ~2,000개/시간"},
        "overhead": {"min": 0.15, "max": 0.30, "note": "설비 감가, 유틸리티, 세정비 (색상전환 시 2~4시간)"},
        "rnd": {"min": 0.10, "max": 0.20, "note": "처방 개발 + 안정성 시험 (3개월 가속). MOQ 배분"},
        "qc_regulatory": {"min": 0.08, "max": 0.15, "note": "경도/파단강도/색차/미생물 검사 + 시장별 인증"},
        "lead_time_weeks": {"sample": "4~6", "approval_rounds": "3~5회", "stability": "4~8", "procurement": "4~6", "production": "3~4", "shipping": "1~3"},
    },
    "lip_tint": {
        "label": "립틴트 (Lip Tint)",
        "raw_materials": {"min": 0.60, "max": 1.00, "note": "수용성 색소, 보습제, 폴리머 필름포머, 용매"},
        "packaging": {"min": 0.50, "max": 1.00, "note": "튜브 + 도우풋 어플리케이터. 커스텀 어플리케이터 시 +$0.2"},
        "labor": {"min": 0.20, "max": 0.35, "note": "혼합→충전→어플리케이터 조립→캡핑"},
        "overhead": {"min": 0.12, "max": 0.25, "note": "액상 라인 사용. 세정 비교적 용이"},
        "rnd": {"min": 0.08, "max": 0.18, "note": "발색력/지속력/건조속도 최적화. C&C 핵심 기술"},
        "qc_regulatory": {"min": 0.06, "max": 0.12, "note": "점도/pH/색차/미생물 + 시장 인증"},
        "lead_time_weeks": {"sample": "3~5", "approval_rounds": "2~4회", "stability": "4~8", "procurement": "3~5", "production": "2~3", "shipping": "1~3"},
    },
    "cushion_foundation": {
        "label": "쿠션 파운데이션 (Cushion Foundation)",
        "raw_materials": {"min": 1.20, "max": 1.80, "note": "에멀전 베이스, 자외선차단제(TiO2/ZnO), 색소, 보습 성분, 쿠션 스펀지 함침액"},
        "packaging": {"min": 1.50, "max": 3.00, "note": "쿠션 케이스(상/하판), 퍼프, 거울, 리필 포함. 커스텀 금형 시 별도 $3,000~8,000"},
        "labor": {"min": 0.40, "max": 0.60, "note": "에멀전 제조→스펀지 함침→케이스 조립→퍼프 삽입→검사"},
        "overhead": {"min": 0.25, "max": 0.40, "note": "쿠션 전용 함침 설비 + 클린룸 환경"},
        "rnd": {"min": 0.15, "max": 0.30, "note": "SPF 측정(in-vivo), 커버력/산화 안정성 테스트. 기능성 심사 (KR)"},
        "qc_regulatory": {"min": 0.12, "max": 0.20, "note": "SPF/PA 검증 + 피부 안전성 + 중금속 + 미생물 + 기능성 인증"},
        "lead_time_weeks": {"sample": "5~8", "approval_rounds": "4~6회", "stability": "6~10", "procurement": "6~10", "production": "4~5", "shipping": "2~4"},
    },
    "eyeshadow": {
        "label": "아이섀도우 팔레트 (Eyeshadow Palette)",
        "raw_materials": {"min": 1.00, "max": 1.50, "note": "탈크/마이카 기제, 색소(산화철, 울트라마린, 펄), 바인더, 프레싱 용매"},
        "packaging": {"min": 1.20, "max": 2.00, "note": "팔레트 케이스(자석), 거울, 개별 팬, 종이 슬리브. FSC인증 시 +10%"},
        "labor": {"min": 0.50, "max": 0.80, "note": "12팬 각각 프레싱→팬 삽입→팔레트 조립. 수동 공정 비율 높음"},
        "overhead": {"min": 0.20, "max": 0.35, "note": "프레스 설비 + 다색상 동시 관리"},
        "rnd": {"min": 0.20, "max": 0.40, "note": "12색 각각 개별 처방 개발. 듀오크롬/글리터는 난이도 높음"},
        "qc_regulatory": {"min": 0.10, "max": 0.18, "note": "팬별 경도/색차/비산도(fallout) + 팔레트 단위 외관 검사"},
        "lead_time_weeks": {"sample": "6~8", "approval_rounds": "3~6회", "stability": "4~8", "procurement": "5~8", "production": "4~6", "shipping": "1~3"},
    },
    "eyeliner": {
        "label": "아이라이너 (Gel Pencil / Liquid)",
        "raw_materials": {"min": 0.50, "max": 0.90, "note": "왁스/폴리머 기제, 흑색 색소(CI 77499), 필름포머"},
        "packaging": {"min": 0.60, "max": 1.20, "note": "리트랙터블 펜슬/펠트팁. 펠트팁 커스텀 시 +$0.3"},
        "labor": {"min": 0.20, "max": 0.35, "note": "압출/충전→캡핑→기능 테스트(리트랙트/발색)"},
        "overhead": {"min": 0.12, "max": 0.22, "note": "펜슬 라인 사용"},
        "rnd": {"min": 0.08, "max": 0.18, "note": "번짐 방지/지속력/발색 최적화"},
        "qc_regulatory": {"min": 0.06, "max": 0.12, "note": "눈가 사용 안전성 강화 검사"},
        "lead_time_weeks": {"sample": "4~6", "approval_rounds": "2~4회", "stability": "4~6", "procurement": "4~6", "production": "2~3", "shipping": "1~3"},
    },
    "other": {
        "label": "기타 색조 제품",
        "raw_materials": {"min": 0.70, "max": 1.30, "note": "제품 유형에 따라 상이"},
        "packaging": {"min": 0.80, "max": 1.80, "note": "제품 유형에 따라 상이"},
        "labor": {"min": 0.25, "max": 0.45, "note": "표준 제조 공정"},
        "overhead": {"min": 0.15, "max": 0.30, "note": "표준 간접비"},
        "rnd": {"min": 0.10, "max": 0.25, "note": "표준 R&D 비용"},
        "qc_regulatory": {"min": 0.08, "max": 0.15, "note": "표준 QC/인증 비용"},
        "lead_time_weeks": {"sample": "4~6", "approval_rounds": "3~5회", "stability": "4~8", "procurement": "4~8", "production": "3~4", "shipping": "1~3"},
    },
}

MARKET_REGULATORY_REQUIREMENTS = {
    "US": {"name": "미국", "flag": "🇺🇸", "requirements": "FDA MoCRA 시설 등록 + 제품 등록", "timeline": "2~4주", "cost": "포함", "risk_notes": "MoCRA(2024) 이후 석면 테스트 의무화, 제품 등록 의무"},
    "EU": {"name": "유럽", "flag": "🇪🇺", "requirements": "CPNP 등록 + Responsible Person 지정", "timeline": "2~4주", "cost": "별도 (RP 계약)", "risk_notes": "PFAS 규제 진행 중(2025~2027), 레티놀 농도 강화, 알레르겐 표시 확대"},
    "UK": {"name": "영국", "flag": "🇬🇧", "requirements": "SCPN 등록 (EU CPNP과 별도)", "timeline": "2~3주", "cost": "별도", "risk_notes": "Brexit 이후 EU와 별도 등록 필수"},
    "CN": {"name": "중국", "flag": "🇨🇳", "requirements": "NMPA 비특수용도 화장품 등록", "timeline": "4~6개월", "cost": "별도 견적 (₩500만~2,000만)", "risk_notes": "동물실험 이슈, 긴 등록 기간, 성분 제한 차이"},
    "KR": {"name": "한국", "flag": "🇰🇷", "requirements": "MFDS 화장품 제조판매 신고", "timeline": "2~4주", "cost": "포함", "risk_notes": "기능성 화장품(SPF/미백/주름) 시 별도 심사 3~6개월"},
    "JP": {"name": "일본", "flag": "🇯🇵", "requirements": "MHLW 화장품 수입판매업 등록", "timeline": "3~6주", "cost": "별도", "risk_notes": "의약부외품 분류 시 별도 승인 필요"},
    "SEA": {"name": "동남아", "flag": "🌏", "requirements": "ASEAN Cosmetics Directive + 국가별 신고", "timeline": "2~8주 (국가별 상이)", "cost": "별도", "risk_notes": "할랄 인증 필요 시 추가 6~8주"},
    "ME": {"name": "중동", "flag": "🕌", "requirements": "GCC Conformity + 국가별 등록", "timeline": "4~8주", "cost": "별도", "risk_notes": "할랄 인증 필수, 아랍어 라벨링 필수"},
}


def calculate_bom_cost(product_type: str) -> dict:
    bom = BOM_COST_DB.get(product_type, BOM_COST_DB["other"])
    categories = ["raw_materials", "packaging", "labor", "overhead", "rnd", "qc_regulatory"]
    total_min = sum(bom[c]["min"] for c in categories)
    total_max = sum(bom[c]["max"] for c in categories)
    return {
        "bom": bom,
        "total_min": round(total_min, 2),
        "total_max": round(total_max, 2),
        "categories": categories,
    }


def assess_risks(specs: dict) -> dict:
    risks = {"timeline": [], "regulatory": [], "cost": [], "technical": []}
    scores = {"timeline": 0, "regulatory": 0, "cost": 0, "technical": 0}

    markets = specs.get("target_markets", [])
    if "CN" in markets:
        risks["regulatory"].append("🔴 중국(NMPA) 등록 4~6개월 소요 — 납기 역산 필수")
        risks["timeline"].append("🔴 NMPA 등록 기간이 전체 일정의 병목이 될 수 있음")
        scores["regulatory"] += 30
        scores["timeline"] += 25

    reqs = specs.get("special_requirements", [])
    req_lower = [r.lower() for r in reqs]
    if any("halal" in r for r in req_lower):
        risks["regulatory"].append("🟡 할랄 인증 추가 6~8주 소요")
        scores["regulatory"] += 15

    if any("vegan" in r for r in req_lower):
        risks["technical"].append("🟢 비건 처방: C&C 대응 가능. 카민 등 동물유래 원료 제외 필요")
        scores["technical"] += 5

    if any("pfas" in r for r in req_lower):
        risks["technical"].append("🟡 PFAS-free: PTFE 대체 원료 필요. 텍스처 변화 가능성")
        scores["technical"] += 10

    if any("talc" in r for r in req_lower):
        risks["technical"].append("🟡 탈크프리: 대체 기제(마이카/합성 플루오로플로고파이트) 사용. 원가 +10~15%")
        scores["technical"] += 10
        scores["cost"] += 10

    if any("clean" in r for r in req_lower) or any("sephora" in r for r in req_lower):
        risks["technical"].append("🟡 클린뷰티 기준: 제한 성분 목록(1,400+개) 사전 검토 필요")
        scores["technical"] += 15

    shade_count = specs.get("shade_count", 0)
    if shade_count > 10:
        risks["timeline"].append(f"🟡 셰이드 {shade_count}색: 개별 처방 개발 필요. 샘플 단계 1~2주 추가")
        scores["timeline"] += 10

    if shade_count > 20:
        risks["timeline"].append("🔴 20색 이상: R&D 리소스 병목. 2단계 분할 개발 권장")
        scores["timeline"] += 20

    product_type = specs.get("product_type", "other")
    if product_type == "cushion_foundation":
        risks["cost"].append("🟡 쿠션: 커스텀 금형비 별도 $3,000~8,000")
        risks["timeline"].append("🟡 쿠션 금형 개발 6~8주 추가")
        scores["cost"] += 15
        scores["timeline"] += 15

    if product_type == "eyeshadow" and shade_count >= 12:
        risks["technical"].append("🟡 12팬 팔레트: 매트/쉬머/듀오크롬/글리터 각각 다른 프레싱 조건")
        scores["technical"] += 10

    claims = specs.get("key_claims", [])
    claims_lower = [c.lower() for c in claims]
    if any("spf" in c for c in claims_lower):
        risks["regulatory"].append("🟡 SPF 제품: 기능성 심사(KR) 3~6개월, in-vivo 테스트 필수")
        risks["cost"].append("🟡 SPF in-vivo 테스트 비용 $2,000~5,000")
        scores["regulatory"] += 20
        scores["cost"] += 10

    if not risks["timeline"]:
        risks["timeline"].append("🟢 특별한 납기 리스크 없음")
    if not risks["regulatory"]:
        risks["regulatory"].append("🟢 표준 규제 절차로 대응 가능")
    if not risks["cost"]:
        risks["cost"].append("🟢 표준 원가 범위 내 예상")
    if not risks["technical"]:
        risks["technical"].append("🟢 기존 처방/설비로 대응 가능")

    for key in scores:
        scores[key] = min(scores[key], 100)

    overall = sum(scores.values()) / 4
    if overall <= 15:
        overall_label = "✅ LOW"
        overall_color = "green"
    elif overall <= 35:
        overall_label = "⚠️ MEDIUM"
        overall_color = "orange"
    else:
        overall_label = "🚨 HIGH"
        overall_color = "red"

    return {
        "risks": risks,
        "scores": scores,
        "overall": round(overall),
        "overall_label": overall_label,
        "overall_color": overall_color,
    }


def get_regulatory_info(markets: list[str]) -> list[dict]:
    return [MARKET_REGULATORY_REQUIREMENTS[m] for m in markets if m in MARKET_REGULATORY_REQUIREMENTS]


SAMPLE_RFQS = {
    "글로벌 브랜드 매트 립스틱 RFQ": """Subject: RFQ - Matte Lipstick Collection Launch Q4 2026

Hi C&C Team,

We're planning to launch a new matte lipstick collection for our brand and would love to partner with your team.

Product: Long-wear Matte Lipstick
Collection: "Velvet Noir" - targeting the K-beauty inspired market
Shades: 12 shades (6 nude/neutral, 4 bold/red, 2 dark/berry)
Finish: Velvet matte, non-drying formula
Key Claims: 8-hour wear, transfer-proof, hydrating, lightweight feel

Packaging: Standard bullet tube, magnetic closure, soft-touch matte exterior
Color: Black tube with gold accent
Engraving: Brand logo on cap

Target Markets: US (primary), EU, Middle East
Certifications needed: Vegan, Cruelty-free (Leaping Bunny), Clean at Sephora compliant
NO parabens, NO PFAS, NO mineral oil

Target unit cost: $3.50-4.50 USD (including primary packaging, excluding secondary)
MOQ: 5,000 units per shade (60,000 total for initial order)

Timeline:
- Samples needed by: August 2026
- Production start: October 2026
- Delivery to US warehouse: December 2026

Please provide your quotation including development costs, timeline, and MOQ flexibility.

Best regards,
Sarah Chen
Product Development Manager
[Brand Name Beauty]""",

    "중국 로컬 브랜드 쿠션 파운데이션 RFQ": """发给C&C国际化妆品

您好，

我们是一家中国新锐美妆品牌，希望开发一款气垫粉底产品。

产品：气垫粉底液
色号：8个色号（适合亚洲肤色，从白皙到小麦色）
SPF：SPF50+ PA++++
质地：水润光泽感，中等遮瑕力

包装要求：
- 方形气垫盒，15g+15g（含替换装）
- 哑光白色外壳，银色logo压印
- 需要定制模具

目标市场：中国大陆（天猫旗舰店）、东南亚（Shopee）
认证需求：NMPA备案，清真认证（面向东南亚）

目标单价：人民币35-45元/套（含替换装和包装）
起订量：每色号3000套

时间要求：
- 样品：2026年7月
- 量产交货：2026年10月

请尽快报价。

谢谢！
王小明
[品牌名] 产品总监""",

    "유럽 인디 브랜드 아이섀도우 팔레트 RFQ": """Dear C&C International,

We are a European indie beauty brand looking for an ODM partner for our upcoming eyeshadow palette launch.

Product: 12-Pan Eyeshadow Palette
Theme: "Aurora Borealis" - inspired by Northern Lights
Shades: 12 shades total
  - 4 matte (earthy nudes)
  - 4 shimmer (aurora-inspired: green, purple, blue, pink)
  - 2 duochrome (color-shifting)
  - 2 glitter topper

Formula requirements:
- Highly pigmented, buildable
- Blendable with minimal fallout
- Talc-free formula preferred
- EU Cosmetics Regulation 1223/2009 compliant

Packaging:
- Rectangular cardboard palette with magnetic closure
- Full-size mirror inside
- FSC-certified packaging material
- Aurora design artwork (we provide artwork files)

Target markets: EU (primary), UK
Target cost: EUR 4.00-5.50 per palette (excluding secondary packaging)
MOQ: 3,000 units

Timeline: Samples by June 2026, production by September 2026

We would also appreciate if you could suggest trending shade combinations based on current K-beauty color trends.

Kind regards,
Emma Lindström
Founder & Creative Director
[Brand Name] Beauty, Stockholm""",
}

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
        "raw_summary": "미국 시장 중심의 K-뷰티 감성 벨벳 매트 립스틱 12색 컬렉션. 비건/크루얼티프리/세포라 클린 뷰티 기준 충족 필요. 셰이드당 5,000개 MOQ, 단가 $3.50-4.50 타겟.",
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
        "raw_summary": "중국 신흥 뷰티 브랜드의 아시안 피부톤 특화 쿠션 파운데이션 8색. SPF50+ PA++++, 광택감 마감. 티몰 플래그십 + Shopee(동남아) 판매 예정. NMPA 등록 및 할랄 인증 필요.",
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
        "raw_summary": "스웨덴 인디 뷰티 브랜드의 오로라 테마 12팬 아이섀도우 팔레트. 매트4+쉬머4+듀오크롬2+글리터2 구성. 탈크프리, EU 규제 완전 준수 필요. FSC 인증 포장재 사용. K-뷰티 트렌드 색상 조합 제안 요청.",
    },
}
