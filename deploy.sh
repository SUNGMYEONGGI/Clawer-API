#!/bin/bash

# FastCampus Crawler 자동 배포 스크립트

echo "🚀 FastCampus Crawler 배포 시작..."

# Git 초기화 및 커밋
echo "📝 Git 초기화..."
if [ ! -d ".git" ]; then
    git init
fi

git add .
git commit -m "Deploy FastCampus Crawler v2.0"

# GitHub 저장소 확인
echo "📂 GitHub 저장소 URL을 입력하세요:"
read GITHUB_URL

if [ ! -z "$GITHUB_URL" ]; then
    git remote add origin $GITHUB_URL 2>/dev/null || git remote set-url origin $GITHUB_URL
    git branch -M main
    git push -u origin main
    echo "✅ GitHub에 코드 업로드 완료!"
    echo ""
    echo "🌐 이제 다음 플랫폼에서 배포하세요:"
    echo ""
    echo "1. Render (추천):"
    echo "   - https://render.com 접속"
    echo "   - 'New +' → 'Web Service'"
    echo "   - GitHub 저장소 연결: $GITHUB_URL"
    echo "   - Build Command: pip install -r requirements.txt"
    echo "   - Start Command: uvicorn main:app --host 0.0.0.0 --port \$PORT"
    echo ""
    echo "2. Railway:"
    echo "   - https://railway.app 접속"
    echo "   - 'New Project' → 'Deploy from GitHub repo'"
    echo ""
    echo "3. Fly.io:"
    echo "   - fly launch --name fastcampus-crawler-api"
    echo "   - fly deploy"
    echo ""
else
    echo "❌ GitHub URL이 필요합니다."
fi

echo "🎉 배포 준비 완료!" 