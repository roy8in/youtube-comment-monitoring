import os
import json
import pandas as pd
from comment_collector import fetch_youtube_comments, fetch_video_stats
from comment_analyzer import analyze_comments_with_llm

CONFIG_FILE = "dashboard_config.json"
with open(CONFIG_FILE, "r", encoding="utf-8") as f:
    config = json.load(f)

TARGET_DATE = config["target_date"]
VIDEO_URL = config["video_url"]
DATA_FILE = f"analyzed_comments_{TARGET_DATE}.csv"
STATS_FILE = f"video_stats_{TARGET_DATE}.csv"
PROMPT_FILE = f"prompt_{TARGET_DATE}.txt"

def run_update():
    """영상 통계 및 댓글 데이터를 업데이트하고 CSV에 저장합니다."""
    # 1. 영상 통계 업데이트
    stats = fetch_video_stats(VIDEO_URL)
    if stats:
        if os.path.exists(STATS_FILE):
            df_stats = pd.read_csv(STATS_FILE)
        else:
            columns = ['timestamp', 'view_count', 'like_count', 
                       'comment_count', 'title']
            df_stats = pd.DataFrame(columns=columns)
            
        new_row = pd.DataFrame([stats])
        df_stats = pd.concat([df_stats, new_row], ignore_index=True)
        df_stats.to_csv(STATS_FILE, index=False)
        print("영상 통계 업데이트 완료.")

    # 2. 신규 댓글 수집 및 LLM 분석
    raw_comments = fetch_youtube_comments(VIDEO_URL)
    
    if os.path.exists(DATA_FILE):
        existing_df = pd.read_csv(DATA_FILE)
    else:
        existing_df = pd.DataFrame(columns=['text', 'sentiment', 'category', 'keyword'])
        
    def normalize(t):
        return "".join(t.split()) if isinstance(t, str) else ""

    existing_normalized = set(normalize(t) for t in existing_df['text'].tolist()) if not existing_df.empty else set()
    
    # 중복되지 않은 신규 댓글만 선별 (공백 무시 기준)
    new_comments = []
    seen_in_batch = set()
    for c in raw_comments:
        norm_c = normalize(c)
        if norm_c not in existing_normalized and norm_c not in seen_in_batch:
            new_comments.append(c)
            seen_in_batch.add(norm_c)
    
    if new_comments:
        with open(PROMPT_FILE, "r", encoding="utf-8") as f:
            prompt_template = f.read()
        
        analyzed_list = analyze_comments_with_llm(new_comments, prompt_template)
        if analyzed_list:
            # LLM이 반환한 text가 변형되었을 수 있으므로, 원본 new_comments와 순서대로 매칭하여 저장
            # (analyze_comments_with_llm이 입력 리스트와 동일한 순서/개수를 반환한다고 가정)
            final_data = []
            for i, result in enumerate(analyzed_list):
                if i < len(new_comments):
                    # 결과 딕셔너리에서 text만 원본으로 교체
                    item = result.copy()
                    item['text'] = new_comments[i] 
                    final_data.append(item)

            new_df = pd.DataFrame(final_data)
            updated_df = pd.concat([existing_df, new_df], ignore_index=True)
            updated_df.to_csv(DATA_FILE, index=False)
            print(f"새 댓글 {len(new_comments)}개 분석 및 저장 완료.")
    else:
        print("분석할 새로운 댓글이 없습니다.")


if __name__ == "__main__":
    run_update()