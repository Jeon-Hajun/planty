# Planty

Planty는 식물을 돌보는 AI 어시스턴트입니다.

## 기능

- 음성 인식 및 대화
- 식물 상태 모니터링
- 실시간 센서 데이터 수집
- 웹 대시보드

## 설치

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

2. API 키 설정:
   - `.env` 파일 생성:
   ```bash
   # OpenAI API 키
   OPENAI_API_KEY=your_openai_api_key
   
   # Google Cloud TTS 인증 파일 경로
   GOOGLE_APPLICATION_CREDENTIALS=credentials/google_credentials.json
   ```
   
   - Google Cloud TTS 설정:
     - `credentials` 폴더 생성:
     ```bash
     mkdir credentials
     ```
     - Google Cloud Console에서 서비스 계정 키를 다운로드하여 `credentials/google_credentials.json`으로 저장

## 실행

```bash
python src/main.py
```

## 프로젝트 구조

```
Planty/
├── src/
│   ├── __init__.py
│   ├── circuit_controller.py    # 회로 제어 관련
│   ├── dashboard.py            # 웹 대시보드 관련
│   ├── ai_controller.py        # AI (음성인식, GPT, TTS) 관련
│   └── main.py                 # 메인 실행 파일
├── tests/
│   └── __init__.py
├── templates/
│   └── index.html
├── static/
│   └── images/
├── requirements.txt
└── README.md
```

## 개발

### 테스트 실행

```bash
python -m pytest tests/
```

### 새로운 기능 추가

1. `src/` 폴더에 새로운 모듈 추가
2. `tests/` 폴더에 테스트 코드 추가
3. `main.py`에 새로운 모듈 통합

## 라이선스

MIT License