# 웹 문서 지식 그래프 생성기

웹 문서를 읽어서 지식 그래프를 생성하고 JSON으로 저장하는 파이썬 스크립트입니다.

## 설치

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

## 사용법

### 1) JSON 생성 (웹 → 스토리 추출 → LLM → JSON 저장)
## 신규: Training Ops Chatbot (CLI)

팀스파르타 기업교육 PM 포지션과 연계해, 교육 운영 KPI/리스크/AAR/커리큘럼 추천을 빠르게 시연할 수 있는 간단한 CLI 챗봇을 추가했습니다. 목데이터로 동작하며 핵심 시나리오를 재현합니다.

폴더: `chatbot/`
- `data/seed.json`: 목데이터(회사, 코호트, 학습자, 출석, 과제/퀴즈, 만족도, 모듈)
- `core.py`: KPI 계산, 리스크 스코어, 추천, AAR, 주간리포트 로직
- `cli.py`: 커맨드라인 진입점

실행 방법 (Windows PowerShell):

```powershell
python -m chatbot.cli kpi --company A --cohort A-1
python -m chatbot.cli weekly --company A --cohort A-1
python -m chatbot.cli risk --cohort A-2 --top 3
python -m chatbot.cli recommend --role PM --level junior --weeks 4 --tags sql pm data
python -m chatbot.cli aar --cohort A-1
```

의도된 데모 포인트:
- KPI 카드: 출석/과제/퀴즈/완료/만족도/NPS
- 리스크 얼리워닝: 학습자별 위험 점수 산출
- AAR 위저드: 이슈 도출과 개선 액션 제안
- 커리큘럼 추천: 역할/레벨/주차/태그 기반 모듈 조합

향후 확장:
- Slack/Email Webhook 연동, PDF 리포트 Export, 시각 UI(웹)로 확장

## 신규: Sparta EduPM Copilot (Streamlit)

대시보드 없이도 대화형으로 Discovery→커리큘럼→타임라인→운영→문서→회고 전 과정을 시연하는 웹 앱 스켈레톤입니다.

폴더: `edupm_app/`
- `app.py`: Streamlit 진입점
- `modules/`: 단계별 모듈(Discovery, Curriculum, Timeline, Ops, Docs, Retro)
- `assets/`: 역할/레벨 매트릭스 샘플 등

실행 방법 (Windows PowerShell):

```powershell
C:/Users/songwanju/AppData/Local/Programs/Python/Python310/python.exe -m streamlit run edupm_app/app.py
```

데모 포인트:
- 디스커버리 콜 위저드로 브리프 생성
- 규칙 기반 커리큘럼 추천과 난이도 조정 포인트 제시
- 타임라인/Gantt 텍스트와 RACI 자동화 예시
- 운영 체크리스트/리스크 관리 템플릿
- 제안서/메일 문서 자동화 초안
- 사후 회고: 지표 입력→액션아이템 생성

### 항상 열리는 링크(배포)

옵션 A) Streamlit Community Cloud(무료)
1. 이 레포를 GitHub에 푸시
2. https://share.streamlit.io 에서 GitHub 레포 선택 → `edupm_app/app.py` 지정 → Deploy
3. 영구 URL 발급(예: https://your-app.streamlit.app)

옵션 B) Render(무료 플랜)
1. 이 레포를 GitHub에 푸시
2. https://render.com → New Web Service → GitHub 레포 선택
3. 루트에 있는 `render.yaml` 자동 인식 또는 수동 설정
4. 빌드 후 영구 URL 제공(예: https://sparta-edupm-copilot.onrender.com)

참고: Docker 배포도 가능(루트 `Dockerfile` 제공).

```bash
python web_to_knowledge_graph.py
```

## 기능

- **웹 스크래핑**: 지정된 URL에서 HTML 콘텐츠를 가져옵니다
- **스토리 추출**: HTML에서 Plot/Story 섹션을 자동으로 찾아 추출합니다  
- **지식 그래프 생성**: Google Gemini API를 사용하여 스토리에서 엔티티, 관계, 사건을 추출합니다
- **JSON 저장**: 구조화된 지식 그래프를 JSON 파일로 저장합니다

### 2) 시각화만 별도로 실행 (옵션)

PyVis를 사용해 JSON 지식 그래프를 HTML로 시각화합니다. 생성된 HTML은 로컬 브라우저에서 바로 열립니다.

1) 의존성 설치
```bash
pip install -r requirements.txt
```

2) 시각화 실행 (기본 입력/출력 경로 사용, 브라우저 자동 오픈 안 함)
```bash
python visualize_kg.py
```

설정 변경은 각 파일 상단의 상수를 수정하세요:
- `web_to_knowledge_graph.py`: `TARGET_URL`, `JSON_OUTPUT`
- `visualize_kg.py`: `input`, `output` (parse_args 내부의 상수)

## 출력 형식

생성되는 JSON 파일은 다음 구조를 가집니다:

```json
{
  "title": "제목",
  "entities": [
    {
      "id": "엔티티_id",
      "name": "엔티티 이름",
      "type": "인물|장소|사물|개념",
      "description": "설명",
      "attributes": {
        "속성명": "속성값"
      }
    }
  ],
  "relationships": [
    {
      "source": "출발_엔티티_id",
      "target": "도착_엔티티_id", 
      "relationship": "관계 유형",
      "description": "관계 설명"
    }
  ],
  "events": [
    {
      "id": "사건_id",
      "name": "사건 이름",
      "description": "사건 설명",
      "participants": ["참여자_id들"],
      "location": "장소_id",
      "sequence": 순서번호
    }
  ]
}
```

## 설정

- **API_KEY**: Google Gemini API 키 (현재 하드코딩됨)
- **TARGET_URL**: 분석할 웹 페이지 URL
- **OUTPUT_FILE**: 출력 JSON 파일명

## 주의사항

- API 키는 보안상 환경변수로 관리하는 것을 권장합니다
- 웹 페이지 구조가 변경되면 스토리 추출 로직 수정이 필요할 수 있습니다
- Google Gemini API 사용량 제한에 주의하세요
