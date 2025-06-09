#!/bin/bash

# 색상 정의
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 오류 발생 시 스크립트 중단
set -e

echo -e "${BLUE}Planty 설치를 시작합니다...${NC}"

# 라즈베리파이 확인
if ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    echo -e "${RED}이 스크립트는 라즈베리파이에서만 실행할 수 있습니다.${NC}"
    exit 1
fi

# 시스템 패키지 설치
echo -e "\n${GREEN}1. 시스템 패키지 설치 중...${NC}"
sudo apt-get update
sudo apt-get install -y mpg123 portaudio19-dev python3-pyaudio

# Python 가상환경 생성
echo -e "\n${GREEN}2. Python 가상환경 생성 중...${NC}"
python3 -m venv venv
source venv/bin/activate

# Python 패키지 설치
echo -e "\n${GREEN}3. Python 패키지 설치 중...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# credentials 디렉토리 생성
echo -e "\n${GREEN}4. credentials 디렉토리 생성 중...${NC}"
mkdir -p credentials

echo -e "\n${BLUE}설치가 완료되었습니다!${NC}"
echo -e "\n다음 단계:"
echo -e "1. ${GREEN}source venv/bin/activate${NC}"
echo -e "2. Google Cloud TTS 인증 파일을 ${GREEN}credentials/google_credentials.json${NC}에 복사"
echo -e "3. ${GREEN}python src/main.py${NC}로 실행" 