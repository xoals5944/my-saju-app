from datetime import datetime
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from google import genai
from pydantic import BaseModel

# FastAPI 앱 생성
app = FastAPI()

# static 폴더 연결 (index.html 파일 제공)
app.mount("/static", StaticFiles(directory="static"), name="static")


class SajuRequest(BaseModel):
    user_name: str
    birth_date: str
    birth_time: str
    gender: str


# 웹사이트 메인 화면 접속 시 static/index.html 열기
@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()


# 사주 분석 API
@app.post("/api/saju")
def get_saju(data: SajuRequest):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500, detail="API 키가 설정되지 않았습니다."
        )

    # 오늘 날짜 구하기
    today_str = datetime.now().strftime("%Y년 %m월 %d일")

    # 기존 프롬프트
    prompt = f"""
    당신은 복잡하고 어려운 사주 용어를 세상에서 가장 쉽고 재미있게 설명해 주는 태민사주 입니다.
    다음 사용자 정보를 바탕으로 사주를 분석해 주세요.

    [오늘 날짜 기준: {today_str}]
    - 이름: {data.user_name}
    - 생년월일: {data.birth_date}
    - 태어난 시간: {data.birth_time}
    - 성별: {data.gender}

    [작성 가이드라인 - 필수]
    1. **[이름 반영]** 모든 항목의 답변과 설명에서 사용자 이름인 '{data.user_name}님'을 자연스럽고 친근하게 자주 지칭해 주세요.
    2. 한자어나 용어는 가급적 사용하지 말아주세요. 만약 사용하게 된다면 해석을 알아듣기 쉽게 풀어주세요.
    3. 어렵고 복잡한 명리학 용어(십성, 용신, 신살, 격국, 갑목, 병화 등)를 사용하더라도 누구나 알아들을 수 있게 쉬운 비유와 해석을 덧붙여주세요.
    4. AI 같지 않고 전문적인 명리 상담사처럼 친절하고 다정하게 알려주세요.
    5. 타고난 사주 기운을 '자연의 요소(따뜻한 햇살, 울창한 나무, 비옥한 땅, 반짝이는 보석, 시원한 바다 등)'에 비유해서 친근하게 설명하세요.
    6. 친절하고 다정한 말투(~해요, ~랍니다)를 사용하세요.
    7. 날짜나 시점이 언급되는 부분은 오늘 날짜인 '{today_str}'를 기준으로 작성해 주세요.
    8. 직관적이고 읽기 쉬운 표현을 사용하여 아래 항목들로 나누어 작성해 주세요.

    [출력 양식]
    1. 🌿 **{data.user_name}님을 나타내는 자연의 기운**
    2. 💡 **{data.user_name}님의 타고난 성격과 숨겨진 매력**
    3. 💰 **{data.user_name}님의 재물운과 딱 맞는 일**
    4. 💌 **{data.user_name}님의 삶이 더 행복해지는 꿀팁**
    5. ❤️ **{data.user_name}님의 연애운은??!!**
    6. 👍 **오늘({today_str}) {data.user_name}님의 운세!!**
    7. ⏩ **이달의 {data.user_name}님 운세!!**
    8. 🌹 **올해 {data.user_name}님의 일년 운세!!**
    9. 🏆 **{data.user_name}님을 위한 총평과 운세 가이드**
    """

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-3.6-flash", contents=prompt
        )
        return {"result": response.text}
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="현재 접속자가 많아 응답이 지연되고 있습니다. 잠시 후 다시 시도해 주세요.",
        )