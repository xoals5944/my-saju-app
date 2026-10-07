import os
import time
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from google import genai

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

class SajuRequest(BaseModel):
    user_name: str
    birth_date: str
    calendar_type: str = "양력"
    birth_time: str
    gender: str
    saju_type: str = "total"

@app.get("/")
async def read_index():
    from fastapi.responses import FileResponse
    return FileResponse('static/index.html')

@app.post("/api/saju")
async def get_saju(req: SajuRequest):
    if req.saju_type == "love":
        type_title = "❤️ 연애운 및 인연법 전문 풀이"
        type_instruction = """
        오직 '연애운'과 '인연의 기운'에 대해서만 명리학적 오행과 기운의 흐름을 살펴 전문적으로 풀이해 주세요.
        - 타고난 애정 기운과 매력의 원천 (음양오행적 특성)
        - 이성과의 인연이 강하게 들어오는 시기 및 합(合)의 흐름
        - 연애 중 일어날 수 있는 살(煞)이나 다툼을 피하는 지혜와 조언
        (다른 운세 이야기는 제외하고 연애운만 다뤄주세요)
        """
    elif req.saju_type == "wealth":
        type_title = "💰 금전운 및 재물복 전문 풀이"
        type_instruction = """
        오직 '금전운'과 '재물 창고(財庫)'에 대해서만 명리학적 기운을 살펴 전문적으로 풀이해 주세요.
        - 타고난 재물복의 크기와 금전 성향 (정재/편재의 기운)
        - 재물이 크게 융성하는 시기와 손재수(손실)를 주의해야 할 시기
        - 재물운을 끌어올리고 대운을 잡기 위한 전문적인 조언
        (다른 운세 이야기는 제외하고 금전운만 다뤄주세요)
        """
    else:
        type_title = "🔮 전체 종합 사주 대운 풀이"
        type_instruction = """
        다음 항목들을 순서대로 오행의 생극제화와 기운의 흐름을 짚어 깔끔하게 나누어 풀이해 주세요.
        1. 🌟 타고난 원국(原局) 분석 및 전체 총운
        2. 📅 오늘의 운세 (일진의 기운)
        3. 🗓️ 이달의 운세 (월운의 흐름)
        4. 🐉 올해 전체 운세 (세운의 기운)
        """

    prompt = f"""
    당신은 신통하고 용하기로 소문난 영험한 신점 및 사주 명리학자입니다.
    신점과 사주명리학의 전문적인 기운(음양오행, 대운, 천간지지의 흐름)을 짚어내되, 말투는 따뜻하고 친근한 존댓말(~해요, ~랍니다, ~입니다)을 사용해 주세요.

    [요청자 정보]
    - 이름: {req.user_name}
    - 생년월일: {req.birth_date} ({req.calendar_type})
    - 태어난 시간: {req.birth_time}
    - 성별: {req.gender}

    [풀이 지침]
    {type_instruction}

    [출력 및 페르소나 규칙]
    1. 말투는 친근하고 다정한 존댓말(~해요, ~랍니다)을 그대로 유지하세요.
    2. 단, 어휘와 설명 방식은 영험한 무속인이나 깊이 있는 명리학자가 사주 원국과 오행의 기운을 짚어주듯 전문성과 깊이감을 갖추세요.
    3. **, # 등 마크다운 특수문자는 절대로 사용하지 마세요.
    4. 보기 좋은 이모지를 적절히 활용하여 읽기 쉽게 구성해 주세요.
    """

    api_key = os.getenv("GEMINI_API_KEY")

    # ⭐ 최대 3번까지 재시도하는 로직 적용
    max_retries = 3
    for attempt in range(max_retries):
        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-2.5-flash", contents=prompt
            )
            return {"result": response.text}
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2)  # 2초간 대기 후 재시도
                continue
            else:
                raise HTTPException(
                    status_code=500,
                    detail="현재 AI 응답이 순간적으로 지연되고 있습니다. 3~5초 후 다시 '사주 보기' 버튼을 눌러주세요!",
                )