# FastCampus LMS Crawler v2.0 🚀

현대적인 UI/UX와 FastAPI를 활용한 FastCampus LMS 크롤링 도구입니다.

## ✨ 특징

- **🎨 2024-2025 UI/UX 트렌드** - 다크 테마, 글래스모피즘, 부드러운 애니메이션
- **⚡ FastAPI 기반** - 고성능 비동기 웹 API
- **🔄 실시간 업데이트** - WebSocket을 통한 실시간 로그 및 진행상황
- **📊 프로그레스 추적** - 시각적 진행률 표시
- **📁 다양한 파일 형식** - CSV, Excel, JSON, XML 지원
- **📱 반응형 디자인** - 모바일 및 데스크톱 최적화
- **🛡️ 오류 처리** - 강력한 예외 처리 및 사용자 피드백

## 🛠️ 기술 스택

### Backend
- **FastAPI** - 현대적인 파이썬 웹 프레임워크
- **WebSocket** - 실시간 통신
- **Selenium** - 웹 크롤링
- **Pandas** - 데이터 처리

### Frontend
- **Vanilla JavaScript** - 의존성 없는 순수 JS
- **CSS3** - 글래스모피즘 및 애니메이션
- **Font Awesome** - 아이콘
- **Inter & JetBrains Mono** - 모던 폰트

## 📦 설치 및 실행

### 1. 환경 준비

```bash
# Python 3.8 이상 필요
python --version

# 가상환경 생성 (권장)
python -m venv venv

# 가상환경 활성화
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 2. 의존성 설치

```bash
# 프로젝트 디렉토리로 이동
cd fastcampus-crawler-api

# 패키지 설치
pip install -r requirements.txt
```

### 3. 서버 실행

```bash
# 개발 서버 실행
python main.py

# 또는 uvicorn 직접 실행
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 브라우저에서 접속

```
http://localhost:8000
```

## 🎯 사용법

### 기본 사용법

1. **시험 ID 입력** - FastCampus LMS URL에서 숫자 부분 입력
   ```
   예: https://lmsadmin-kdt.fastcampus.co.kr/exams/8532/detail
   → 시험 ID: 8532
   ```

2. **파일 형식 선택** - CSV, Excel, JSON, XML 중 선택

3. **크롤링 시작** - "크롤링 시작" 버튼 클릭

4. **실시간 모니터링** - 진행상황과 로그를 실시간으로 확인

5. **결과 다운로드** - 완료 후 생성된 파일 다운로드

### 고급 기능

- **실시간 로그**: 크롤링 과정을 실시간으로 모니터링
- **진행률 표시**: 시각적 프로그레스바와 퍼센트 표시
- **오류 처리**: 문제 발생 시 자세한 오류 메시지 제공
- **크롤링 중지**: 실행 중인 작업을 안전하게 중지
- **자동 재연결**: WebSocket 연결 끊김 시 자동 재연결

## 📂 프로젝트 구조

```
fastcampus-crawler-api/
├── main.py                 # FastAPI 메인 서버
├── crawler.py              # 크롤링 로직
├── requirements.txt        # 의존성 패키지
├── README.md              # 프로젝트 문서
├── static/                # 정적 파일
│   ├── index.html         # 메인 웹페이지
│   ├── style.css          # 스타일시트
│   ├── script.js          # JavaScript
│   └── downloads/         # 다운로드 파일 저장소
└── .gitignore             # Git 무시 파일
```

## 🔧 API 엔드포인트

### REST API

| 메서드 | 엔드포인트 | 설명 |
|--------|------------|------|
| `GET` | `/` | 메인 웹페이지 |
| `POST` | `/api/start-crawling` | 크롤링 시작 |
| `POST` | `/api/stop-crawling` | 크롤링 중지 |
| `GET` | `/api/status` | 현재 상태 조회 |
| `GET` | `/api/logs` | 로그 조회 |
| `GET` | `/api/download/{file_path}` | 파일 다운로드 |

### WebSocket

| 엔드포인트 | 설명 |
|------------|------|
| `/ws` | 실시간 로그 및 상태 업데이트 |

## 🎨 UI/UX 특징

### 2024-2025 디자인 트렌드

- **🌙 다크 테마**: 눈의 피로를 줄이는 다크 색상 팔레트
- **💎 글래스모피즘**: 반투명 블러 효과로 깊이감 연출
- **🌈 그라데이션**: 생동감 있는 색상 전환
- **⚡ 마이크로 애니메이션**: 부드럽고 의미있는 인터랙션
- **📐 그리드 시스템**: 체계적인 레이아웃 구성

### 색상 팔레트

```css
Primary: #6366f1 (Indigo)
Secondary: #8b5cf6 (Purple)  
Accent: #06b6d4 (Cyan)
Success: #10b981 (Emerald)
Warning: #f59e0b (Amber)
Error: #ef4444 (Red)
```

### 반응형 디자인

- **데스크톱**: 1200px 이상 - 풀 레이아웃
- **태블릿**: 768px~1199px - 적응형 레이아웃
- **모바일**: 480px~767px - 스택 레이아웃
- **작은 모바일**: 480px 미만 - 컴팩트 레이아웃

## 🚨 주의사항

1. **Chrome Driver**: Selenium WebDriver가 자동으로 설치됩니다.
2. **네트워크**: 안정적인 인터넷 연결이 필요합니다.
3. **권한**: 일부 시스템에서 실행 권한이 필요할 수 있습니다.
4. **메모리**: 대용량 데이터 처리 시 충분한 메모리가 필요합니다.

## 🔒 보안

- 파일 다운로드 경로 제한
- XSS 방지를 위한 입력 검증
- CORS 설정
- 에러 정보 제한적 노출

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 지원

문제가 있거나 제안사항이 있으시면 이슈를 생성해 주세요.

---

**Made with ❤️ using FastAPI + Modern Web Technologies** 