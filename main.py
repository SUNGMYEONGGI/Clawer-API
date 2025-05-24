from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import asyncio
import json
import os
import uuid
from typing import Dict, List
from crawler import FastCampusLMSCrawler
import uvicorn

# 요청 모델들
class CrawlRequest(BaseModel):
    exam_id: str
    file_format: str = "csv"

class StatusResponse(BaseModel):
    is_running: bool
    current_exam_id: str = None
    collected_count: int = 0
    session_id: str = None

# FastAPI 앱 생성
app = FastAPI(
    title="FastCampus LMS Crawler API",
    description="FastCampus LMS 시험 데이터 크롤링 API",
    version="2.0.0"
)

# 정적 파일 서빙
app.mount("/static", StaticFiles(directory="static"), name="static")

# 필요한 디렉토리 생성 (static만)
def ensure_directories():
    """필요한 디렉토리들을 생성"""
    directories = ["static"]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

# 앱 시작 시 디렉토리 생성
ensure_directories()

# 글로벌 크롤러 인스턴스 및 연결 관리
crawler_instance = FastCampusLMSCrawler()
active_connections: List[WebSocket] = []

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # 연결이 끊어진 경우 리스트에서 제거
                if connection in self.active_connections:
                    self.active_connections.remove(connection)

manager = ConnectionManager()

@app.get("/", response_class=HTMLResponse)
async def read_index():
    """메인 페이지 반환"""
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    except FileNotFoundError:
        return HTMLResponse("<h1>index.html 파일을 찾을 수 없습니다.</h1>")

@app.get("/favicon.ico")
async def favicon():
    """Favicon 반환 (404 오류 방지)"""
    # 간단한 빈 아이콘을 반환하여 404 오류 방지
    return FileResponse("static/favicon.ico") if os.path.exists("static/favicon.ico") else ""

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 연결 관리"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # 클라이언트로부터 메시지를 받을 수 있지만, 주로 서버에서 클라이언트로 전송
            pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/api/start-crawling")
async def start_crawling(request: CrawlRequest, background_tasks: BackgroundTasks):
    """크롤링 시작"""
    if crawler_instance.is_running:
        raise HTTPException(status_code=400, detail="이미 크롤링이 실행 중입니다.")
    
    if not request.exam_id.isdigit():
        raise HTTPException(status_code=400, detail="올바른 시험 ID(숫자)를 입력하세요.")
    
    # 세션 ID 생성
    session_id = str(uuid.uuid4())
    crawler_instance.session_id = session_id
    crawler_instance.is_running = True
    
    # 백그라운드에서 크롤링 실행
    background_tasks.add_task(run_crawling_task, request.exam_id, request.file_format)
    
    return {
        "message": "크롤링이 시작되었습니다.",
        "session_id": session_id,
        "exam_id": request.exam_id
    }

async def run_crawling_task(exam_id: str, file_format: str):
    """백그라운드에서 실행되는 크롤링 태스크"""
    websocket = None
    if manager.active_connections:
        websocket = manager.active_connections[0] if manager.active_connections else None
    
    try:
        # 로그인 프로세스
        await manager.broadcast(json.dumps({
            "type": "status",
            "message": "로그인 프로세스 시작..."
        }))
        
        await crawler_instance.login_process(websocket)
        
        await manager.broadcast(json.dumps({
            "type": "status", 
            "message": "로그인 성공. 크롤링 시작..."
        }))
        
        # 크롤링 실행
        collected_count = await crawler_instance.crawl_exam_data(exam_id, websocket)
        
        # 파일 생성 (메모리에서)
        if collected_count > 0:
            await manager.broadcast(json.dumps({
                "type": "status",
                "message": f"{file_format.upper()} 형식으로 파일 생성 중..."
            }))
            
            try:
                file_data = crawler_instance.export_data(exam_id, file_format)
                
                if file_data:
                    content, filename, media_type = file_data
                    # 파일 데이터를 세션에 임시 저장
                    crawler_instance.temp_file_data = {
                        "content": content,
                        "filename": filename,
                        "media_type": media_type
                    }
                    
                    await manager.broadcast(json.dumps({
                        "type": "complete",
                        "message": f"크롤링 완료! {collected_count}개 데이터 수집 ({file_format.upper()} 파일 생성 완료)",
                        "download_ready": True,
                        "filename": filename,
                        "collected_count": collected_count
                    }))
                else:
                    # 더 자세한 에러 정보를 로그에서 가져오기
                    recent_logs = crawler_instance.log_messages[-5:] if crawler_instance.log_messages else []
                    error_details = " / ".join(recent_logs) if recent_logs else "알 수 없는 오류"
                    
                    await manager.broadcast(json.dumps({
                        "type": "error",
                        "message": f"파일 생성에 실패했습니다. 형식: {file_format.upper()}, 상세: {error_details}"
                    }))
            except Exception as export_error:
                await manager.broadcast(json.dumps({
                    "type": "error", 
                    "message": f"파일 생성 중 예외 발생: {str(export_error)} (형식: {file_format.upper()})"
                }))
        else:
            await manager.broadcast(json.dumps({
                "type": "error",
                "message": "수집된 데이터가 없습니다."
            }))
            
    except Exception as e:
        await manager.broadcast(json.dumps({
            "type": "error",
            "message": f"크롤링 중 오류: {str(e)}"
        }))
    finally:
        crawler_instance.cleanup()

@app.post("/api/stop-crawling")
async def stop_crawling():
    """크롤링 중지"""
    if not crawler_instance.is_running:
        raise HTTPException(status_code=400, detail="실행 중인 크롤링이 없습니다.")
    
    crawler_instance.is_running = False
    crawler_instance.cleanup()
    
    await manager.broadcast(json.dumps({
        "type": "stopped",
        "message": "크롤링이 중지되었습니다."
    }))
    
    return {"message": "크롤링이 중지되었습니다."}

@app.get("/api/status", response_model=StatusResponse)
async def get_status():
    """현재 상태 조회"""
    status = crawler_instance.get_status()
    return StatusResponse(**status)

@app.get("/api/download")
async def download_file():
    """메모리에서 직접 파일 다운로드"""
    if not hasattr(crawler_instance, 'temp_file_data') or not crawler_instance.temp_file_data:
        raise HTTPException(status_code=404, detail="다운로드할 파일이 없습니다. 먼저 크롤링을 완료하세요.")
    
    file_data = crawler_instance.temp_file_data
    
    from fastapi.responses import Response
    return Response(
        content=file_data["content"],
        media_type=file_data["media_type"],
        headers={"Content-Disposition": f"attachment; filename={file_data['filename']}"}
    )

@app.get("/api/logs")
async def get_logs():
    """최근 로그 조회"""
    return {
        "logs": crawler_instance.log_messages[-50:],  # 최근 50개 로그
        "count": len(crawler_instance.log_messages)
    }

# 서버 시작 함수
def start_server():
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    start_server()