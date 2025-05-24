// FastCampus Crawler JavaScript

class CrawlerApp {
    constructor() {
        this.ws = null;
        this.isConnected = false;
        this.isRunning = false;
        this.currentSessionId = null;
        
        this.initializeElements();
        this.attachEventListeners();
        this.connectWebSocket();
    }

    initializeElements() {
        // Form elements
        this.crawlForm = document.getElementById('crawlForm');
        this.examIdInput = document.getElementById('examId');
        this.fileFormatSelect = document.getElementById('fileFormat');
        this.startBtn = document.getElementById('startBtn');
        this.stopBtn = document.getElementById('stopBtn');
        
        // Status elements
        this.connectionStatus = document.getElementById('connectionStatus');
        this.statusDot = this.connectionStatus.querySelector('.status-dot');
        this.statusText = this.connectionStatus.querySelector('span');
        
        // Progress elements
        this.progressSection = document.getElementById('progressSection');
        this.progressBar = document.getElementById('progressBar');
        this.progressText = document.getElementById('progressText');
        this.statusMessage = document.getElementById('statusMessage');
        
        // Results elements
        this.resultsSection = document.getElementById('resultsSection');
        this.resultInfo = document.getElementById('resultInfo');
        
        // Log elements
        this.logContainer = document.getElementById('logContainer');
        this.clearLogBtn = document.getElementById('clearLogBtn');
        
        // Overlay elements
        this.loadingOverlay = document.getElementById('loadingOverlay');
        this.notification = document.getElementById('notification');
    }

    attachEventListeners() {
        // Form submission
        this.crawlForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.startCrawling();
        });
        
        // Stop button
        this.stopBtn.addEventListener('click', () => {
            this.stopCrawling();
        });
        
        // Clear log button
        this.clearLogBtn.addEventListener('click', () => {
            this.clearLogs();
        });
        
        // Auto-focus exam ID input
        this.examIdInput.focus();
        
        // Input validation
        this.examIdInput.addEventListener('input', (e) => {
            const value = e.target.value;
            const isValid = /^\d+$/.test(value) && value.length > 0;
            
            if (value && !isValid) {
                e.target.style.borderColor = '#ef4444';
            } else {
                e.target.style.borderColor = '';
            }
        });
    }

    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        try {
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                this.isConnected = true;
                this.updateConnectionStatus(true);
                this.addLog('WebSocket 연결이 설정되었습니다.', 'success');
            };
            
            this.ws.onmessage = (event) => {
                this.handleWebSocketMessage(event.data);
            };
            
            this.ws.onclose = () => {
                this.isConnected = false;
                this.updateConnectionStatus(false);
                this.addLog('WebSocket 연결이 끊어졌습니다. 재연결 시도중...', 'warning');
                
                // 자동 재연결 (5초 후)
                setTimeout(() => {
                    if (!this.isConnected) {
                        this.connectWebSocket();
                    }
                }, 5000);
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket 오류:', error);
                this.addLog('WebSocket 연결 오류가 발생했습니다.', 'error');
            };
            
        } catch (error) {
            console.error('WebSocket 연결 실패:', error);
            this.addLog('WebSocket 연결을 설정할 수 없습니다.', 'error');
        }
    }

    handleWebSocketMessage(data) {
        try {
            const message = JSON.parse(data);
            
            switch (message.type) {
                case 'log':
                    this.addLog(message.message);
                    break;
                    
                case 'progress':
                    this.updateProgress(message.progress, message.message);
                    break;
                    
                case 'status':
                    this.updateStatus(message.message);
                    this.addLog(message.message, 'system');
                    break;
                    
                case 'complete':
                    this.handleCrawlingComplete(message);
                    break;
                    
                case 'error':
                    this.handleCrawlingError(message.message);
                    break;
                    
                case 'stopped':
                    this.handleCrawlingStopped(message.message);
                    break;
                    
                default:
                    console.log('알 수 없는 메시지 타입:', message.type);
            }
        } catch (error) {
            console.error('메시지 파싱 오류:', error);
        }
    }

    async startCrawling() {
        const examId = this.examIdInput.value.trim();
        const fileFormat = this.fileFormatSelect.value;
        
        if (!examId || !/^\d+$/.test(examId)) {
            this.showNotification('올바른 시험 ID(숫자)를 입력해주세요.', 'error');
            this.examIdInput.focus();
            return;
        }
        
        if (!this.isConnected) {
            this.showNotification('서버 연결이 필요합니다. 잠시 후 다시 시도해주세요.', 'warning');
            return;
        }
        
        try {
            this.setRunningState(true);
            this.showProgress();
            this.updateProgress(0, '크롤링 시작 준비중...');
            
            const response = await fetch('/api/start-crawling', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    exam_id: examId,
                    file_format: fileFormat
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || '크롤링 시작 실패');
            }
            
            const result = await response.json();
            this.currentSessionId = result.session_id;
            this.addLog(`크롤링이 시작되었습니다. (세션 ID: ${result.session_id})`, 'success');
            
        } catch (error) {
            console.error('크롤링 시작 오류:', error);
            this.addLog(`크롤링 시작 실패: ${error.message}`, 'error');
            this.showNotification(error.message, 'error');
            this.setRunningState(false);
            this.hideProgress();
        }
    }

    async stopCrawling() {
        try {
            const response = await fetch('/api/stop-crawling', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || '크롤링 중지 실패');
            }
            
            const result = await response.json();
            this.addLog(result.message, 'warning');
            this.showNotification('크롤링이 중지되었습니다.', 'warning');
            
        } catch (error) {
            console.error('크롤링 중지 오류:', error);
            this.addLog(`크롤링 중지 실패: ${error.message}`, 'error');
            this.showNotification(error.message, 'error');
        }
    }

    updateConnectionStatus(connected) {
        if (connected) {
            this.statusDot.classList.add('connected');
            this.statusText.textContent = '연결됨';
        } else {
            this.statusDot.classList.remove('connected');
            this.statusText.textContent = '연결 끊김';
        }
    }

    setRunningState(running) {
        this.isRunning = running;
        this.startBtn.disabled = running;
        this.stopBtn.disabled = !running;
        this.examIdInput.disabled = running;
        this.fileFormatSelect.disabled = running;
        
        if (running) {
            this.startBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i><span>실행중...</span>';
        } else {
            this.startBtn.innerHTML = '<i class="fas fa-play"></i><span>크롤링 시작</span>';
        }
    }

    showProgress() {
        this.progressSection.style.display = 'block';
        this.progressSection.classList.add('fade-in');
        this.hideResults();
    }

    hideProgress() {
        this.progressSection.style.display = 'none';
    }

    updateProgress(progress, message) {
        const percentage = Math.round(progress * 100);
        this.progressBar.style.width = `${percentage}%`;
        this.progressText.textContent = `${percentage}%`;
        this.statusMessage.textContent = message;
    }

    updateStatus(message) {
        this.statusMessage.textContent = message;
    }

    showResults() {
        this.resultsSection.style.display = 'block';
        this.resultsSection.classList.add('slide-up');
    }

    hideResults() {
        this.resultsSection.style.display = 'none';
    }

    handleCrawlingComplete(message) {
        this.setRunningState(false);
        this.updateProgress(1, message.message);
        this.addLog(message.message, 'success');
        this.showNotification(`크롤링 완료! ${message.collected_count}개 데이터 수집`, 'success');
        
        if (message.download_ready && message.filename) {
            this.displayResults(message.filename, message.collected_count);
        }
        
        setTimeout(() => {
            this.hideProgress();
        }, 2000);
    }

    handleCrawlingError(errorMessage) {
        this.setRunningState(false);
        this.hideProgress();
        this.addLog(errorMessage, 'error');
        this.showNotification(errorMessage, 'error');
    }

    handleCrawlingStopped(message) {
        this.setRunningState(false);
        this.hideProgress();
        this.addLog(message, 'warning');
    }

    displayResults(fileName, collectedCount) {
        const fileExtension = fileName.split('.').pop().toUpperCase();
        
        this.resultInfo.innerHTML = `
            <div class="result-card">
                <div class="result-details">
                    <h3><i class="fas fa-file-${this.getFileIcon(fileExtension)}"></i> ${fileName}</h3>
                    <p>수집된 데이터: ${collectedCount}개</p>
                    <p>파일 형식: ${fileExtension}</p>
                </div>
                <a href="/api/download" class="download-btn" download="${fileName}">
                    <i class="fas fa-download"></i>
                    다운로드
                </a>
            </div>
        `;
        
        this.showResults();
    }

    getFileIcon(extension) {
        const iconMap = {
            'CSV': 'csv',
            'XLSX': 'excel',
            'JSON': 'code',
            'XML': 'code'
        };
        return iconMap[extension] || 'alt';
    }

    addLog(message, type = 'info') {
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry ${type}`;
        logEntry.textContent = message;
        
        this.logContainer.appendChild(logEntry);
        this.logContainer.scrollTop = this.logContainer.scrollHeight;
        
        // 로그 개수 제한 (최대 100개)
        const logEntries = this.logContainer.querySelectorAll('.log-entry');
        if (logEntries.length > 100) {
            logEntries[0].remove();
        }
    }

    clearLogs() {
        this.logContainer.innerHTML = '<div class="log-entry system">로그가 삭제되었습니다.</div>';
    }

    showNotification(message, type = 'info') {
        const iconMap = {
            'success': 'fas fa-check-circle',
            'error': 'fas fa-exclamation-circle',
            'warning': 'fas fa-exclamation-triangle',
            'info': 'fas fa-info-circle'
        };
        
        this.notification.className = `notification ${type}`;
        this.notification.querySelector('.notification-icon').className = `notification-icon ${iconMap[type]}`;
        this.notification.querySelector('.notification-message').textContent = message;
        
        this.notification.style.display = 'block';
        
        // 5초 후 자동 숨김
        setTimeout(() => {
            this.notification.style.display = 'none';
        }, 5000);
    }

    showLoading(show = true) {
        this.loadingOverlay.style.display = show ? 'flex' : 'none';
    }
}

// 애플리케이션 초기화
document.addEventListener('DOMContentLoaded', () => {
    const app = new CrawlerApp();
    
    // 전역 에러 핸들러
    window.addEventListener('error', (event) => {
        console.error('Global error:', event.error);
        app.addLog(`스크립트 오류: ${event.error.message}`, 'error');
    });
    
    // 페이지 언로드 시 WebSocket 정리
    window.addEventListener('beforeunload', () => {
        if (app.ws) {
            app.ws.close();
        }
    });
    
    // 개발용 - 콘솔에서 앱 인스턴스 접근 가능
    window.crawlerApp = app;
});

// 유틸리티 함수들
const utils = {
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    
    formatTime(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = Math.floor(seconds % 60);
        
        if (hours > 0) {
            return `${hours}시간 ${minutes}분 ${secs}초`;
        } else if (minutes > 0) {
            return `${minutes}분 ${secs}초`;
        } else {
            return `${secs}초`;
        }
    },
    
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}; 