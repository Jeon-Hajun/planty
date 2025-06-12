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

# 시스템 의존성 설치
echo -e "\n${GREEN}1. 시스템 의존성 설치 중...${NC}"
sudo apt-get update
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    portaudio19-dev \
    python3-pyaudio \
    mpg123 \
    libatlas-base-dev \
    libblas-dev \
    liblapack-dev \
    libopenblas-dev

# 가상환경 생성
echo -e "\n${GREEN}2. Python 가상환경 생성 중...${NC}"
python3 -m venv .venv
source .venv/bin/activate

# pip 업그레이드
echo -e "\n${GREEN}3. pip 업그레이드 중...${NC}"
pip install --upgrade pip

# Python 패키지 설치
echo -e "\n${GREEN}4. Python 패키지 설치 중...${NC}"
pip install -r requirements.txt

# 오디오 장치 설정
echo -e "\n${GREEN}5. 오디오 장치 설정 중...${NC}"
if [ ! -f ~/.asoundrc ]; then
    echo "pcm.!default {
    type hw
    card 0
    device 0
}

ctl.!default {
    type hw
    card 0
}" > ~/.asoundrc
fi

# 권한 설정
echo -e "\n${GREEN}6. 권한 설정 중...${NC}"
sudo usermod -a -G audio $USER
sudo usermod -a -G gpio $USER

echo -e "\n${BLUE}설치가 완료되었습니다!${NC}"
echo -e "\n다음 단계:"
echo -e "1. ${GREEN}source .venv/bin/activate${NC}"
echo -e "2. Google Cloud TTS 인증 파일을 ${GREEN}credentials/google_credentials.json${NC}에 복사"
echo -e "3. ${GREEN}python src/main.py${NC}로 실행"
echo -e "4. 시스템을 재시작하거나 로그아웃 후 다시 로그인해주세요." 