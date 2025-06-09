#!/bin/bash

# 색상 정의
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Planty 설치를 시작합니다...${NC}"

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

echo -e "\n${BLUE}설치가 완료되었습니다!${NC}"
echo -e "\n프로그램을 실행하려면:"
echo -e "1. ${GREEN}source venv/bin/activate${NC}"
echo -e "2. ${GREEN}python src/main.py${NC}" 