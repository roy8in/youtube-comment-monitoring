import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 설정
DATA_FILE = "analyzed_comments.csv"
STATS_FILE = "video_stats.csv"

def load_data(file_path):
    """CSV 파일을 읽어옵니다. 없으면 빈 데이터프레임 반환"""
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    return pd.DataFrame()

def main():
    st.set_page_config(layout="wide", page_title="국민연금 여론 모니터링 시스템")
    
    st.title("📊 국민연금공단 유튜브 여론 모니터링 대시보드")
    st.markdown("💡 *이 대시보드는 30분 주기로 최신 여론을 자동 수집 및 분석하여 반영합니다.*")
    st.markdown("---")

    # 데이터 로드 (API 호출 없이 오직 파일만 읽음)
    df_comments = load_data(DATA_FILE)
    df_stats = load_data(STATS_FILE)

    # --- 1구역: 영상 통계 (조회수 추이) ---
    st.header("📈 영상 성과 분석")
    if not df_stats.empty:
        c1, c2, c3, c4 = st.columns(4)
        latest = df_stats.iloc[-1]
        
        # 이전 데이터와 비교하여 증가분 표시
        delta_view = int(latest['view_count'] - df_stats.iloc[-2]['view_count']) if len(df_stats) > 1 else 0
        
        c1.metric("누적 조회수", f"{latest['view_count']:,}회", f"+{delta_view:,}" if delta_view else None)
        c2.metric("좋아요", f"{latest['like_count']:,}개")
        c3.metric("댓글", f"{latest['comment_count']:,}개")
        c4.metric("분석된 댓글", f"{len(df_comments):,}개")

        # 시간대별 조회수 그래프 (2월 14일 08:00 이후 필터링 적용)
        df_stats['timestamp'] = pd.to_datetime(df_stats['timestamp'])
        cutoff_time = pd.to_datetime("2026-02-14 08:00:00")
        df_filtered = df_stats[df_stats['timestamp'] >= cutoff_time]
        
        fig_views = px.line(df_filtered, x='timestamp', y='view_count', title="시간대별 조회수 추이 (2/14 08:00 이후)",
                            markers=True, line_shape='spline', template="plotly_white")
        fig_views.update_traces(line_color='#FF4B4B')
        st.plotly_chart(fig_views, width="stretch")
    else:
        st.info("영상 통계 데이터가 아직 수집되지 않았습니다. (데이터 갱신 대기 중)")

    st.markdown("---")

    # --- 2구역: 감성 분석 ---
    st.header("😊 여론 분석 결과")
    if not df_comments.empty:
        col_left, col_right = st.columns([1, 1])
        
        with col_left:
            st.subheader("감성 분포")
            fig_pie = px.pie(df_comments, names='sentiment', color='sentiment',
                             color_discrete_map={'긍정': '#00CC96', '부정': '#EF553B', '중립': '#636EFA', '오류': '#AB63FA'})
            st.plotly_chart(fig_pie, width="stretch")
            
        with col_right:
            st.subheader("주요 키워드 여론")
            keyword_sentiment = df_comments.groupby(['keyword', 'sentiment']).size().reset_index(name='count')
            top_keywords = df_comments['keyword'].value_counts().head(10).index
            ks_filtered = keyword_sentiment[keyword_sentiment['keyword'].isin(top_keywords)]
            fig_ks = px.bar(ks_filtered, x='keyword', y='count', color='sentiment',
                            color_discrete_map={'긍정': '#00CC96', '부정': '#EF553B', '중립': '#636EFA'},
                            barmode='stack')
            st.plotly_chart(fig_ks, width="stretch")

        st.markdown("### 📝 전체 분석 데이터")
        
        # 감성에 따라 차트와 동일한 색상 CSS를 적용하는 함수
        def color_sentiment(val):
            color_map = {
                '긍정': '#00CC96',
                '부정': '#EF553B',
                '중립': '#636EFA',
                '오류': '#AB63FA'
            }
            color = color_map.get(val, 'inherit')
            return f'color: {color}; font-weight: bold;'
            
        # 화면에 보여줄 데이터 정렬
        display_df = df_comments[['sentiment', 'keyword', 'text']].sort_index(ascending=False)
        
        # Pandas Styler를 사용해 'sentiment' 열에만 색상 함수 적용
        styled_df = display_df.style.map(color_sentiment, subset=['sentiment'])
        
        # 스타일이 적용된 데이터프레임 출력 (width="stretch" 대신 use_container_width 권장)
        st.dataframe(styled_df, use_container_width=True)
    else:
        st.info("분석된 댓글 데이터가 없습니다. (데이터 갱신 대기 중)")

if __name__ == "__main__":
    main()