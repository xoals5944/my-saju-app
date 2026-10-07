import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from google import genai

app = FastAPI()

# static 폴더 연결
app.mount("/static", StaticFiles(directory="static"), name="static")

# 1. 요청 데이터 구조 정의 (saju_type 추가)
class SajuRequest(BaseModel):
    user_name: str
    birth_date: str
    birth_time: str
    gender: str
    saju_type: str = "total"

@app.get("/")
async def read_index():
    from fastapi.responses import FileResponse
    return FileResponse('static/index.html')

@app.post("/api/saju")
async def get_saju(req: SajuRequest):
    # 2. 탭별 프롬프트 분기 설정
    if req.saju_type == "love":
        type_title = "❤️ 연애운 전용 풀이"
        type_instruction = "오직 '연애운' 및 '애정 흐름'에 대해서만 집중적으로 풀이해 주세요."
    elif req.saju_type == "wealth":
        type_title = "💰 금전운 전용 풀이"
        type_instruction = "오직 '금전운' 및 '재물 흐름'에 대해서만 집중적으로 풀이해 주세요."
    else:
        type_title = "🔮 전체 종합 사주 (오늘/이달/올해/전반적 운세)"
        type_instruction = "1. 전반적 총운, 2. 오늘의 운세, 3. 이달의 운세, 4. 올해 전체 운세 순서로 나누어 풀이해 주세요."

    # 3. AI 프롬프트 작성
    prompt = f"""
    당신은 친절한 사주 명리학자입니다. 요청자의 사주 정보를 바탕으로 [{type_title}]를 풀어주세요.

    [요청자 정보]
    - 이름: {req.user_name}
    - 생년월일: {req.birth_date}
    - 태어난 시간: {req.birth_time}
    - 성별: {req.gender}

    [풀이 지침]
    {type_instruction}

    [출력 규칙]
    1. **, # 등 마크다운 특수문자를 절대 사용하지 마세요.
    2. 자연스럽고 친근한 존댓말(~해요, ~랍니다)을 사용하세요.
    """

    api_key = os.getenv("GEMINI_API_KEY")

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )
        return {"result": response.text}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="현재 접속자가 많아 응답이 지연되고 있습니다. 잠시 후 다시 시도해 주세요.",
        )