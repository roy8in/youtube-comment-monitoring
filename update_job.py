import os
import pandas as pd
from comment_collector import fetch_youtube_comments, fetch_video_stats
from comment_analyzer import analyze_comments_with_llm

DATA_FILE = "analyzed_comments.csv"
STATS_FILE = "video_stats.csv"
VIDEO_URL = "https://youtu.be/fNHLffyXnQM?si=MqWixiMHqKLpMsiG"


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
        existing_df = pd.DataFrame(columns=['text', 'sentiment', 'keyword'])
        
    existing_texts = set(existing_df['text'].tolist()) if not existing_df.empty else set()
    new_comments = [c for c in raw_comments if c not in existing_texts]
    
    if new_comments:
        analyzed_list = analyze_comments_with_llm(new_comments)
        if analyzed_list:
            new_df = pd.DataFrame(analyzed_list)
            updated_df = pd.concat([existing_df, new_df], ignore_index=True)
            updated_df.to_csv(DATA_FILE, index=False)
            print(f"새 댓글 {len(new_comments)}개 분석 및 저장 완료.")
    else:
        print("분석할 새로운 댓글이 없습니다.")


if __name__ == "__main__":
    run_update()