#!/bin/bash

# Chrome 설치 스크립트 for Render (개선된 버전)
echo "Chrome 설치 시작..."

# 필요한 도구 설치
apt-get update -qq
apt-get install -y -qq wget gnupg

# Google Chrome 저장소 추가
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list

# 패키지 목록 업데이트
apt-get update -qq

# Google Chrome 설치
apt-get install -y -qq google-chrome-stable

# Chrome 버전 확인
google-chrome-stable --version || echo "Chrome 직접 설치 실패, 대체 방법 시도..."

# 대체 방법: Chrome 바이너리 직접 다운로드
if [ ! -f "/usr/bin/google-chrome-stable" ]; then
    echo "대체 Chrome 설치 방법 시도..."
    mkdir -p /opt/chrome
    cd /opt/chrome
    wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    dpkg -i google-chrome-stable_current_amd64.deb || apt-get install -f -y
fi

echo "Chrome 설치 완료!"
echo "Chrome 경로: $(which google-chrome-stable || echo '/opt/google/chrome/chrome')"