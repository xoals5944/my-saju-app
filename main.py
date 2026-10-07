from fastapi import FastAPI
from pydantic import BaseModel
import google.generativeai as genai

app = FastAPI()

class SajuRequest(BaseModel):
    user_name: str
    birth_date: str
    birth_time: str
    gender: str
    saju_type: str = "total"

@app.post("/api/saju")
async def get_saju(req: SajuRequest):
    # 탭별 프롬프트 및 지시사항 분기
    if req.saju_type == "love":
        type_title = "❤️ 연애운 전용 풀이"
        type_instruction = """
        오직 '연애운' 및 '애정 흐름'에 대해서만 집중적으로 풀이해 주세요.
        - 타고난 연애 성향 및 매력 포인트
        - 현재~앞으로의 연애운 흐름 및 좋은 인연을 만날 시기
        - 연애 시주의해야 할 점 및 조언
        (금전운이나 다른 운세 이야기는 제외하고 연애운만 다뤄주세요)
        """
    elif req.saju_type == "wealth":
        type_title = "💰 금전운 전용 풀이"
        type_instruction = """
        오직 '금전운' 및 '재물 흐름'에 대해서만 집중적으로 풀이해 주세요.
        - 타고난 재물복 및 금전 성향
        - 재물이 모이는 시기와 주의해야 할 지출/손실 시기
        - 재물운을 높이기 위한 실천 팁 및 조언
        (연애운이나 다른 운세 이야기는 제외하고 금전운만 다뤄주세요)
        """
    else:  # total
        type_title = "🔮 전체 종합 사주 (오늘/이달/올해/전반적 운세)"
        type_instruction = """
        다음 항목들을 순서대로 깔끔하게 나누어 풀이해 주세요.
        1. 🌟 타고난 전반적 총운 및 성격
        2. 📅 오늘의 운세
        3. 🗓️ 이달의 운세
        4. 🐉 올해(2026년) 전체 운세
        """

    prompt = f"""
    당신은 친절하고 용한 사주 명리학자입니다.
    요청자의 사주 정보를 바탕으로 [{type_title}]를 풀어주세요.

    [요청자 정보]
    - 이름: {req.user_name}
    - 생년월일: {req.birth_date}
    - 태어난 시간: {req.birth_time}
    - 성별: {req.gender}

    [풀이 지침]
    {type_instruction}

    [출력 규칙]
    1. ** 별표, # 샵 등 마크다운 특수문자를 절대 쓰지 마세요.
    2. 딱딱한 말투 대신, 실제 상담하듯 자연스럽고 친근한 존댓말(~해요, ~랍니다, ~입니다)을 쓰세요.
    3. 구분을 위해 보기 좋은 이모지(✨, 🔮, 💡, 📌 등)를 사용하세요.
    """

    # Gemini 모델 호출 (기존 코드 사용)
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return {"result": response.text}
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="현재 접속자가 많아 응답이 지연되고 있습니다. 잠시 후 다시 시도해 주세요.",
        )