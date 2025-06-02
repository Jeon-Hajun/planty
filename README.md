# Planty - 스마트 반려식물 프로젝트

라즈베리파이를 이용한 스마트 반려식물 관리 시스템입니다.

## 기능
- 실시간 식물 상태 모니터링
- 자동 급수 시스템
- 웹 대시보드를 통한 원격 모니터링
- AI 비서 기능

## 설치 방법

1. 라즈베리파이 설정
```bash
# 시스템 업데이트
sudo apt-get update
sudo apt-get upgrade

# 필요한 패키지 설치
sudo apt-get install python3-pip
sudo apt-get install python3-venv
```

2. 가상환경 설정
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. SSH 설정
```bash
# SSH 활성화
sudo raspi-config
# Interface Options -> SSH -> Enable 선택
```

## 실행 방법
```bash
python app.py
```

## 하드웨어 연결
- 토양 수분 센서: GPIO 17
- DHT22 (온도/습도): GPIO 4
- 조도 센서: GPIO 18
- 워터펌프 릴레이: GPIO 23 