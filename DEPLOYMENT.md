# 🚀 배포 가이드

## 1. Render 배포 (추천) ⭐

### 단계별 가이드:

1. **GitHub에 코드 업로드**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

2. **Render 계정 생성**
   - https://render.com 접속
   - GitHub 계정으로 가입

3. **새 웹 서비스 생성**
   - "New +" → "Web Service"
   - GitHub 저장소 연결
   - 설정:
     - Name: `fastcampus-crawler-api`
     - Runtime: `Python 3`
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **환경 변수 설정**
   - `PYTHON_VERSION`: `3.11.0`

5. **배포 완료!** 🎉
   - URL: `https://fastcampus-crawler-api.onrender.com`

---

## 2. Railway 배포

### 단계별 가이드:

1. **Railway 계정 생성**
   - https://railway.app 접속
   - GitHub 계정으로 가입

2. **새 프로젝트 생성**
   - "New Project" → "Deploy from GitHub repo"
   - 저장소 선택

3. **자동 배포**
   - `railway.json` 파일이 자동으로 감지됨
   - 배포 완료까지 대기

4. **도메인 설정**
   - Settings → Domains → Generate Domain

---

## 3. Fly.io 배포

### 단계별 가이드:

1. **Fly CLI 설치**
   ```bash
   # macOS
   brew install flyctl
   
   # Windows
   pwsh -c "iwr https://fly.io/install.ps1 -useb | iex"
   
   # Linux
   curl -L https://fly.io/install.sh | sh
   ```

2. **로그인 및 앱 생성**
   ```bash
   fly auth login
   fly launch --name fastcampus-crawler-api
   ```

3. **배포**
   ```bash
   fly deploy
   ```

---

## 4. Replit 배포

### 단계별 가이드:

1. **Replit 계정 생성**
   - https://replit.com 접속

2. **GitHub에서 Import**
   - "Create Repl" → "Import from GitHub"
   - 저장소 URL 입력

3. **실행**
   - Run 버튼 클릭
   - 자동으로 공개 URL 생성

---

## 📋 배포 전 체크리스트

### 필수 파일 확인:
- ✅ `requirements.txt` - 의존성 패키지
- ✅ `main.py` - FastAPI 메인 파일
- ✅ `Dockerfile` - Docker 컨테이너 설정
- ✅ `render.yaml` - Render 설정
- ✅ `railway.json` - Railway 설정
- ✅ `fly.toml` - Fly.io 설정

### 환경 변수 설정:
- `PORT` - 서버 포트 (자동 설정됨)
- `PYTHON_VERSION` - Python 버전

### Chrome Driver 설정:
각 플랫폼에서 Chrome/Chromium 설치가 필요합니다.
Dockerfile에서 자동으로 처리됩니다.

---

## 🚨 주의사항

1. **무료 플랜 제한사항:**
   - Render: 15분 비활성 시 슬립 모드
   - Railway: 매월 $5 크레딧 제한
   - Fly.io: CPU/메모리 제한

2. **Selenium 이슈:**
   - 일부 플랫폼에서 Chrome 설치 문제 발생 가능
   - 헤드리스 모드 필수

3. **파일 저장:**
   - 임시 파일 시스템 사용
   - 재시작 시 파일 삭제됨

---

## 💡 권장사항

1. **Render 우선 사용** - 가장 안정적이고 쉬움
2. **GitHub Actions**로 자동 배포 설정
3. **환경 변수**로 민감한 정보 관리
4. **로그 모니터링** 활용

---

## 🔗 유용한 링크

- [Render Documentation](https://render.com/docs)
- [Railway Documentation](https://docs.railway.app)
- [Fly.io Documentation](https://fly.io/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/) 