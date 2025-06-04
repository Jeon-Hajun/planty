#!/bin/bash

# 현재 디렉토리가 Planty인지 확인
if [ ! -d ".git" ]; then
    echo "Planty 디렉토리로 이동합니다..."
    cd planty
fi

# 현재 변경사항 저장
echo "현재 변경사항을 저장합니다..."
git stash

# 최신 변경사항 가져오기
echo "최신 코드를 가져옵니다..."
git pull

# 가상환경 활성화
echo "가상환경을 활성화합니다..."
source venv/bin/activate

# 패키지 업데이트
echo "필요한 패키지를 업데이트합니다..."
pip install -r requirements.txt

echo "업데이트가 완료되었습니다!"
echo "프로그램을 실행하려면: python planty.py" 