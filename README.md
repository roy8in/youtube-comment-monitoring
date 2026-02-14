# 유튜브 댓글 모니터링 시스템 (YouTube Comment Monitoring System)

특정 유튜브 영상의 댓글과 통계 데이터를 자동으로 수집하고, LLM(GPT-4o-mini)을 사용하여 댓글의 감성과 키워드를 분석한 뒤 Streamlit 대시보드로 시각화하는 프로젝트입니다.

## 🚀 주요 기능

- **자동 데이터 수집**: YouTube Data API v3를 사용하여 영상 통계(조회수, 좋아요, 댓글 수) 및 신규 댓글을 실시간으로 가져옵니다.
- **LLM 기반 여론 분석**: OpenRouter를 통해 GPT-4o-mini 모델을 사용하여 각 댓글의 감성(긍정, 부정, 중립)과 핵심 키워드를 추출합니다.
- **인터랙티브 대시보드**: Streamlit을 활용하여 다음 데이터를 시각화합니다.
    - 시간대별 조회수 추이 그래프
    - 감성 분포 (파이 차트)
    - 주요 키워드별 여론 분석 (바 차트)
    - 상세 분석 데이터 테이블
- **GitHub Actions 자동화**: 30분 주기로 데이터를 자동 갱신하고 결과를 저장소에 커밋하는 워크플로우가 포함되어 있습니다.

## 🛠 기술 스택

- **언어**: Python 3.10+
- **대시보드**: Streamlit, Plotly
- **데이터 처리**: Pandas
- **API**: YouTube Data API v3, OpenRouter (OpenAI SDK)
- **자동화**: GitHub Actions

## 📋 사전 준비 사항

- Python 3.10 이상
- [YouTube Data API Key](https://console.cloud.google.com/) (Google Cloud Console에서 발급)
- [OpenRouter API Key](https://openrouter.ai/)

## ⚙️ 설치 및 설정

1. **저장소 클론**:
   ```bash
   git clone <repository-url>
   cd youtube-comment-monitoring
   ```

2. **가상환경 생성 및 활성화**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

3. **필수 라이브러리 설치**:
   ```bash
   pip install -r requirements.txt
   ```

4. **환경 변수 설정**:
   루트 디렉토리에 `.env` 파일을 생성하고 발급받은 API 키를 입력합니다.
   ```env
   YOUTUBE_API_KEY=your_youtube_api_key_here
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   ```

## 📖 사용 방법

### 대시보드 실행
로컬에서 Streamlit 대시보드를 실행하려면 다음 명령어를 입력하세요.
```bash
streamlit run streamlit_dashboard.py
```

### 데이터 수동 업데이트
새로운 댓글을 즉시 수집하고 분석하려면 다음 스크립트를 실행하세요.
```bash
python update_job.py
```
*참고: `update_job.py` 파일 내의 `VIDEO_URL` 상수를 수정하여 분석 대상을 변경할 수 있습니다.*

## 🤖 자동화 (GitHub Actions)

이 프로젝트는 `.github/workflows/update_data.yml` 설정을 통해 자동 업데이트를 지원합니다.

1. **주기**: 매 30분마다 실행
2. **동작**: `update_job.py` 실행 -> 데이터 갱신 -> CSV 파일 자동 커밋 및 푸시
3. **설정**: GitHub 저장소의 **Settings > Secrets and variables > Actions** 메뉴에 `YOUTUBE_API_KEY`와 `OPENROUTER_API_KEY`를 추가해야 합니다.

## 📁 프로젝트 구조

- `streamlit_dashboard.py`: 시각화 대시보드 메인 앱
- `update_job.py`: 데이터 수집 및 분석 실행 스크립트
- `comment_collector.py`: 유튜브 API 통신 모듈
- `comment_analyzer.py`: LLM 기반 댓글 분석 모듈
- `analyzed_comments.csv`: 분석된 댓글 데이터 저장소
- `video_stats.csv`: 영상 통계 히스토리 저장소
- `.github/workflows/update_data.yml`: GitHub Actions 자동화 설정
