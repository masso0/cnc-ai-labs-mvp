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
