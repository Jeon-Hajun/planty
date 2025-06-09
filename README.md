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

## 시스템 아키텍처

Planty 시스템은 다음과 같은 주요 컴포넌트들로 구성되며, 이들은 `GlobalState` 객체를 중심으로 유기적으로 상호작용합니다.

```mermaid
graph TD
    subgraph User Interaction
        User[사용자]
        Microphone[마이크 입력]
        Speaker[스피커 출력]
        Browser[웹 브라우저 (대시보드)]
    end

    subgraph Planty Core
        main_py(main.py)
        GlobalState(GlobalState)
        AIController(AIController)
        CircuitController(CircuitController)
        Dashboard(Dashboard)
    end

    subgraph External Services
        OpenAI[OpenAI API (GPT-4o-mini)]
        GoogleTTS[Google Cloud TTS API]
        Whisper[Whisper Model (Local)]
        PlantSensors[실제 식물 센서 (TODO)]
    end

    User -->|음성 명령| Microphone
    Microphone --> AIController
    AIController -->|텍스트 변환| Whisper
    AIController -->|대화 처리| OpenAI
    OpenAI --> AIController
    AIController -->|음성 합성| GoogleTTS
    GoogleTTS --> Speaker
    Speaker --> User

    AIController -->|상태 업데이트| GlobalState
    CircuitController -->|센서 데이터 업데이트| GlobalState
    Dashboard -->|상태 및 센서 데이터 요청| GlobalState

    main_py -->|초기화| GlobalState
    main_py -->|초기화 및 스레드 시작| AIController
    main_py -->|초기화 및 스레드 시작| CircuitController
    main_py -->|초기화 및 웹 서버 시작| Dashboard

    CircuitController -->|데이터 읽기| PlantSensors
    Dashboard -->|데이터 표시| Browser
    Browser --> User
```

### 컴포넌트별 역할:

*   **`main.py`**: 애플리케이션의 메인 진입점입니다. `GlobalState`, `AIController`, `CircuitController`, `Dashboard`를 초기화하고, 각 컨트롤러를 별도의 스레드로 실행하여 시스템이 동시에 여러 작업을 수행할 수 있도록 합니다.
*   **`GlobalState`**: 시스템의 현재 상태(식물의 표정, 행동)와 모든 센서 데이터를 중앙에서 관리하는 객체입니다. 다른 컴포넌트들은 이 `GlobalState`를 통해 데이터를 공유하고 업데이트합니다.
*   **`AIController`**: 사용자의 음성 명령을 처리하고 응답을 생성합니다. 
    *   **음성 인식**: 마이크 입력을 받아 로컬 `Whisper` 모델을 사용하여 텍스트로 변환합니다.
    *   **대화 처리**: 인식된 텍스트를 `gpt-4o-mini` 모델(OpenAI API)로 전송하여 적절한 식물 관리 조언이나 대화 응답을 생성합니다.
    *   **음성 합성**: 생성된 텍스트 응답을 Google Cloud TTS API를 통해 음성으로 변환하여 스피커로 출력합니다.
    *   **상태 업데이트**: 대화 내용에 따라 `GlobalState`의 식물 표정 및 행동을 업데이트합니다.
*   **`CircuitController`**: 식물 센서 데이터를 주기적으로 읽어오고(현재는 임시값, 추후 실제 센서 연동 필요) `GlobalState`를 업데이트합니다. 또한, 필요에 따라 급수 펌프와 같은 하드웨어를 제어하는 로직을 포함할 수 있습니다.
*   **`Dashboard`**: Flask 웹 서버를 구동하여 웹 대시보드를 제공합니다. 웹 브라우저에서 `GlobalState`의 최신 센서 데이터를 주기적으로 요청하여 표시합니다.

이러한 구조를 통해 각 기능이 독립적으로 작동하면서도 `GlobalState`를 통해 유기적으로 연결되어 Planty 시스템의 효율적인 운영을 가능하게 합니다.

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