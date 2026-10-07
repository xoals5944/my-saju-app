import os
import time
import traceback
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
        type_instruction = "오직 '연애운'과 '인연의 기운'에 대해서만 명리학적 오행과 기운의 흐름을 살펴 전문적으로 풀이해 주세요."
    elif req.saju_type == "wealth":
        type_title = "💰 금전운 및 재물복 전문 풀이"
        type_instruction = "오직 '금전운'과 '재물 창고(財庫)'에 대해서만 명리학적 기운을 살펴 전문적으로 풀이해 주세요."
    else:
        type_title = "🔮 전체 종합 사주 대운 풀이"
        type_instruction = "전반적 총운, 오늘의 운세, 이달의 운세, 올해 전체 운세를 순서대로 오행의 흐름을 짚어 풀이해 주세요."

    prompt = f"""
    당신은 신통하고 용하기로 소문난 영험한 신점 및 사주 명리학자입니다.
    신점과 사주명리학의 전문적인 기운(음양오행, 대운)을 짚어내되, 말투는 따뜻하고 친근한 존댓말(~해요, ~랍니다)을 사용해 주세요.

    [요청자 정보]
    - 이름: {req.user_name}
    - 생년월일: {req.birth_date} ({req.calendar_type})
    - 태어난 시간: {req.birth_time}
    - 성별: {req.gender}

    [풀이 지침]
    {type_instruction}

    [출력 규칙]
    1. **, # 등 마크다운 특수문자는 절대로 사용하지 마세요.
    2. 다정한 존댓말을 유지하면서도 전문 용어를 살려 풀이해 주세요.
    """

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY가 설정되지 않았습니다.")

    client = genai.Client(api_key=api_key)

    max_retries = 3
    for attempt in range(max_retries):
        try:
            # ⭐ 최신 모델명 gemini-3.8-flash 로 변경
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt
            )
            return {"result": response.text}
        except Exception as e:
            print(f"❌ API 오류 발생 (시도 {attempt+1}/{max_retries}): {e}")
            traceback.print_exc()
            if attempt < max_retries - 1:
                time.sleep(4)
                continue
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"AI 응답 처리 중 오류가 발생했습니다: {str(e)}",
                )