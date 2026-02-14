import json
import os
import re

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def analyze_comments_with_llm(comments: list) -> list:
    """OpenRouter를 사용하여 댓글의 감성과 주요 키워드를 분석합니다."""
    if not comments:
        return []

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("CRITICAL ERROR: OPENROUTER_API_KEY가 .env 파일에 없습니다.")
        return [
            {"text": t, "sentiment": "오류", "keyword": "API키누락"}
            for t in comments
        ]

    # 1. OpenRouter가 권장하는 필수 헤더 추가
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        default_headers={
            "HTTP-Referer": "http://localhost:8501", 
            "X-Title": "NPS_PR_Dashboard"
        }
    )

    model = "openai/gpt-4o-mini"
    analyzed_data = []

    batch_size = 15
    for i in range(0, len(comments), batch_size):
        batch = comments[i:i + batch_size]
        
        # 최상위를 {} 객체로 감싸도록 프롬프트 수정
        # 타겟(국민연금, 이사장) 중심의 감성 분석으로 프롬프트 고도화
        prompt = f"""당신은 국민연금공단 홍보실 소속 수석 여론 분석 전문가입니다.
                    제시된 유튜브 댓글들을 분석하여 반드시 아래 JSON 형식으로만 답변하세요.

                    [분석 기준]
                    1. sentiment(감성): 댓글 전체의 단순한 분위기가 아니라, 오직 '국민연금공단', '국민연금 제도' 또는 '김성주 이사장'에 대한 태도를 기준으로 '긍정', '부정', '중립'을 평가하세요.
                    - 국민연금이나 이사장에 대한 칭찬, 응원, 기대감 -> 긍정
                    - 국민연금이나 이사장에 대한 비판, 우려, 불만 -> 부정
                    - 단순 시장 전망, 타인에 대한 비판, 연금과 무관한 넋두리, 질문 -> 중립
                    2. keyword(핵심주제): 댓글의 핵심 내용을 1~2단어로 압축하세요. (예: 수익률, 기금고갈, 의결권, 코스닥투자 등)

                    [출력 형식]
                    {{
                    "data": [
                        {{"text": "원본댓글", "sentiment": "긍정|부정|중립", "keyword": "핵심주제"}}
                    ]
                    }}

댓글 목록: {json.dumps(batch, ensure_ascii=False)}"""

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                response_format={"type": "json_object"}  # JSON 구조 완벽 강제
            )
            
            content = response.choices[0].message.content.strip()
            result_dict = json.loads(content)  # 정규식 없이 깔끔하게 파싱!
            
            # 딕셔너리 안의 리스트를 추출
            if "data" in result_dict:
                analyzed_data.extend(result_dict["data"])
            else:
                raise ValueError("JSON에 'data' 키가 없습니다.")
                

        except Exception as e:
            # 2. 대시보드에서 직접 에러 종류를 확인 가능하도록 추적 로직 강화
            error_type = type(e).__name__
            print(f"배치 {i//batch_size} 분석 중 오류 발생: {e}")
            if 'content' in locals():
                print(f"Raw response: {content[:200]}")
            
            for text in batch:
                analyzed_data.append({
                    "text": text,
                    "sentiment": "오류",
                    "keyword": f"에러: {error_type}"  # 화면에 '에러: NotFoundError' 등으로 표시됨
                })

    return analyzed_data