#!/bin/bash

# Chrome 설치 스크립트 for Render
echo "Chrome 설치 시작..."

# Chrome 디렉토리 생성
mkdir -p .render/chrome

# Chrome 다운로드 및 설치
cd .render/chrome
wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
wget -q https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip

# Chrome 압축 해제
ar x google-chrome-stable_current_amd64.deb
tar xf data.tar.xz

# ChromeDriver 압축 해제
unzip chromedriver_linux64.zip

# 실행 권한 부여
chmod +x opt/google/chrome/chrome
chmod +x chromedriver

# 심볼릭 링크 생성
ln -sf $(pwd)/opt/google/chrome/chrome chrome-linux/chrome
ln -sf $(pwd)/chromedriver chromedriver

echo "Chrome 설치 완료!"