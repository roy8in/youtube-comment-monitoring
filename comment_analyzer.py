import json
import os
import re

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def analyze_comments_with_llm(comments: list, prompt_template: str) -> list:
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
        prompt = f"{prompt_template}\n\n댓글 목록: {json.dumps(batch, ensure_ascii=False)}"

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