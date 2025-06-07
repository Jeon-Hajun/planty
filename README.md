# Planty - 스마트 반려식물 프로젝트

라즈베리파이를 이용한 스마트 반려식물 관리 시스템입니다.

## 구현할 기능
- AI 어시스턴스 planty
  - 음성 인식 (ASR)
  - 자연어 처리 (LLM)
  - 음성 합성 (TTS)

## 기술 스택
### ASR (음성 인식)
- Whisper tiny 모델 사용
- PyAudio를 통한 마이크 입력 처리
- 라즈베리파이에서 CPU 기반 실행

### LLM (자연어 처리)
- OpenAI API (GPT-4)
- 대화형 AI 비서 구현
- 식물 관리 관련 명령어 처리

### TTS (음성 합성)
- Google Cloud TTS 사용
- 자연스러운 한국어 음성 출력
- 라즈베리파이 스피커 출력

## 개발 환경
- 하드웨어: 라즈베리파이
- OS: Raspberry Pi OS
- Python 3.x
- 가상환경 사용 권장

## 유의사항
- 라즈베리파이 환경에 최적화된 코드 작성
- 리소스 사용량 최소화 (CPU, 메모리)
- 오프라인 동작 가능한 기능 우선 구현
- Whisper 모델은 프로젝트에 포함
- GitHub를 통한 버전 관리
- planty.py에 인공지능 비서 클래스 planty 를 만들어서 각 기능을 구현해라

## 설치 방법
1. 시스템 패키지 설치
```bash
sudo apt-get update
sudo apt-get install portaudio19-dev python3-pyaudio
```

2. Python 패키지 설치
```bash
pip install -r requirements.txt
```

## API 키 설정 방법

### 1. OpenAI API 키 설정
1. [OpenAI API 키 발급 페이지](https://platform.openai.com/api-keys)에서 API 키를 발급받습니다.
2. 프로젝트 루트 디렉토리에 `.env` 파일을 생성합니다.
3. `.env` 파일에 다음 내용을 추가합니다:
```
OPENAI_API_KEY=your_openai_api_key_here
```

### 2. Google Cloud TTS API 키 설정
1. [Google Cloud Console](https://console.cloud.google.com/)에서 프로젝트를 생성합니다.
2. Text-to-Speech API를 활성화합니다.
3. 서비스 계정을 생성하고 JSON 키 파일을 다운로드합니다.
4. 다운로드한 JSON 키 파일을 프로젝트 루트 디렉토리의 `credentials` 폴더에 저장합니다.
5. `.env` 파일에 다음 내용을 추가합니다:
```
GOOGLE_APPLICATION_CREDENTIALS=credentials/your_credentials_file.json
```

### 주의사항
- `.env` 파일과 `credentials` 폴더는 절대로 GitHub에 커밋하지 마세요!
- `.gitignore` 파일에 다음 내용이 포함되어 있는지 확인하세요:
```
.env
credentials/
*.json
```

## 테스트 실행 방법

### TTS 모델 테스트
```bash
python test/test_tts_models.py
```

### SSML 기능 테스트
```bash
python test/test_tts_ssml.py
```

### 오디오 설정 테스트
```bash
python test/test_tts_audio_config.py
```

## 프로젝트 구조
```
Planty/
├── .env                    # API 키 설정 파일 (git에 포함되지 않음)
├── credentials/           # Google Cloud 인증 파일 (git에 포함되지 않음)
├── test/                 # 테스트 코드
│   ├── test_tts_models.py
│   ├── test_tts_ssml.py
│   └── test_tts_audio_config.py
├── planty.py             # 메인 코드
└── README.md
```