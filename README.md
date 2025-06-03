# Planty - 스마트 반려식물 프로젝트

라즈베리파이를 이용한 스마트 반려식물 관리 시스템입니다.

## 구현할 기능
- AI 비서 기능
  - 음성 인식 (ASR)
  - 자연어 처리 (LLM)
  - 음성 합성 (TTS)
- 실시간 식물 상태 모니터링
- 자동 급수 시스템
- 웹 대시보드를 통한 원격 모니터링

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

## 하드웨어 연결
- 마이크: USB 마이크 또는 GPIO 마이크 모듈
- 스피커: 3.5mm 오디오 출력 또는 GPIO 스피커 모듈
- 토양 수분 센서: GPIO 17
- DHT22 (온도/습도): GPIO 4
- 조도 센서: GPIO 18
- 워터펌프 릴레이: GPIO 23
