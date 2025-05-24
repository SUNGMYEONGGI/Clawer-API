import asyncio
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import os
import json
import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString
from typing import Callable, Optional, Dict, Any
import uuid

class FastCampusLMSCrawler:
    def __init__(self):
        self.email = "help.edu@fastcampus.co.kr"
        self.password = "Camp1017!!"
        self.driver = None
        self.wait = None
        self.is_running = False
        self.current_exam_id = None
        self.collected_data = []
        self.log_messages = []
        self.session_id = None
        
    def _add_log(self, message: str):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.log_messages.append(log_entry)
        return log_entry

    def setup_driver(self):
        self._add_log("Selenium 드라이버 설정 시작...")
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        chrome_options.add_argument("--disable-features=TranslateUI")
        chrome_options.add_argument("--disable-ipc-flooding-protection")
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("prefs", {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "autofill.profile_enabled": False
        })
        
        # Render 환경에서 Chrome 바이너리 경로 설정
        chrome_bin = os.getenv('CHROME_BIN')
        if chrome_bin:
            chrome_options.binary_location = chrome_bin
            self._add_log(f"Chrome 바이너리 경로 설정: {chrome_bin}")
        
        try:
            # Render 환경에서는 Chrome이 시스템에 설치되어 있으므로 ChromeDriverManager 사용
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, 20)
            self._add_log("Selenium 드라이버 설정 완료.")
        except Exception as e:
            self._add_log(f"드라이버 설정 실패: {e}")
            # 드라이버 설정 실패시 None으로 설정하여 이후 로직에서 처리
            self.driver = None
            self.wait = None
            raise
        
    async def login_process(self, websocket=None):
        self._add_log("로그인 프로세스 시작...")
        if self.driver:
            try: 
                self.driver.quit()
                self._add_log("기존 드라이버 종료.")
            except: 
                pass
        
        self.setup_driver()
        
        # 드라이버 설정 실패 체크
        if self.driver is None:
            error_msg = "Chrome 드라이버 설정에 실패했습니다. Render 환경에서 Chrome이 설치되지 않았을 수 있습니다."
            self._add_log(error_msg)
            raise Exception(error_msg)
        
        try:
            self._add_log("로그인 페이지로 이동...")
            if websocket:
                await websocket.send_text(json.dumps({
                    "type": "log",
                    "message": self.log_messages[-1]
                }))
            
            self.driver.get("https://lmsadmin-kdt.fastcampus.co.kr/sign-in")
            site_select = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="site"]')))
            Select(site_select).select_by_index(0)
            self._add_log("사이트 선택 완료.")
            time.sleep(0.2)
            
            email_input = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="userName"]')))
            email_input.clear()
            email_input.send_keys(self.email)
            self._add_log("이메일 입력 완료.")
            
            password_input = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="password"]')))
            password_input.clear()
            password_input.send_keys(self.password)
            self._add_log("비밀번호 입력 완료.")
            
            login_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/main/section/div/form/button')))
            self.driver.execute_script("arguments[0].click();", login_button)
            self._add_log("로그인 버튼 클릭.")
            
            self.wait.until(lambda drv: drv.current_url != "https://lmsadmin-kdt.fastcampus.co.kr/sign-in")
            self._add_log("로그인 성공!")
            
            current_url = self.driver.current_url
            self.driver.execute_script("window.open('', '_blank');")
            time.sleep(0.2)
            
            if len(self.driver.window_handles) > 1:
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[-1])
            
            self.driver.get(current_url)
            self._add_log(f"새 탭에서 URL ({current_url})로 이동 완료.")
            time.sleep(1)
            return True
        except Exception as e:
            self._add_log(f"로그인 실패: {str(e)}")
            if self.driver:
                self.driver.quit()
            self.driver = None
            raise

    def _collect_data_item(self, student_name: str, blog_link: str):
        # None 체크 및 기본값 설정
        if student_name is None:
            student_name = "알 수 없는 학생"
        if blog_link is None:
            blog_link = ""
            
        self.collected_data.append({'수강자 이름': student_name, '블로그 링크': blog_link})
        self._add_log(f"데이터 수집: 이름={student_name}, 링크={blog_link[:30] if blog_link else '없음'}...")

    def export_data(self, exam_id: str, file_format: str = "csv") -> Optional[str]:
        if not self.collected_data:
            self._add_log("내보낼 데이터가 없습니다.")
            return None

        df = pd.DataFrame(self.collected_data)
        timestamp_str = time.strftime("%Y%m%d_%H%M%S")
        base_filename = f"exam_data_{exam_id}_{timestamp_str}"
        output_path = None

        try:
            if file_format == "csv":
                output_path = f"static/downloads/{base_filename}.csv"
                df.to_csv(output_path, index=False, encoding='utf-8-sig')
            elif file_format == "xlsx":
                output_path = f"static/downloads/{base_filename}.xlsx"
                df.to_excel(output_path, index=False, engine='openpyxl')
            elif file_format == "json":
                output_path = f"static/downloads/{base_filename}.json"
                df.to_json(output_path, orient='records', lines=False, indent=4, force_ascii=False)
            elif file_format == "xml":
                output_path = f"static/downloads/{base_filename}.xml"
                root = ET.Element("students")
                for _, row in df.iterrows():
                    student_elem = ET.SubElement(root, "student")
                    ET.SubElement(student_elem, "name").text = str(row['수강자 이름'])
                    ET.SubElement(student_elem, "blog_link").text = str(row['블로그 링크'])
                
                tree = ET.ElementTree(root)
                xml_str = ET.tostring(root, encoding='utf-8')
                pretty_xml_str = parseString(xml_str).toprettyxml(indent="  ")
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(pretty_xml_str)
            else:
                self._add_log(f"지원하지 않는 파일 형식: {file_format}")
                return None
                
            self._add_log(f"{output_path} 파일로 데이터 내보내기 완료.")
            return output_path
        except Exception as e:
            self._add_log(f"데이터 내보내기 중 오류 ({output_path}): {e}")
            return None

    async def crawl_exam_data(self, exam_id: str, websocket=None) -> int:
        self.current_exam_id = exam_id
        self.collected_data = []
        self.log_messages = []
        
        async def send_update(progress_value: float, message: str):
            self._add_log(message)
            if websocket:
                await websocket.send_text(json.dumps({
                    "type": "progress", 
                    "progress": progress_value,
                    "message": message
                }))
                await websocket.send_text(json.dumps({
                    "type": "log",
                    "message": self.log_messages[-1]
                }))

        base_url = "https://lmsadmin-kdt.fastcampus.co.kr/exams/"
        target_url = f"{base_url}{exam_id}/detail"
        
        await send_update(0, f"시험 ID {exam_id} 페이지로 이동 중: {target_url}")
        self.driver.get(target_url)
        time.sleep(1)
        
        total_count = 0
        try:
            pagination_element_xpath = '//*[@id="app"]/main/section/div/div[2]/div/div[2]/div[2]/span[2]'
            pagination_element = self.wait.until(EC.presence_of_element_located((By.XPATH, pagination_element_xpath)))
            pagination_text = pagination_element.text
            
            # None 체크 및 기본값 설정
            if pagination_text is None:
                pagination_text = "1"
            else:
                pagination_text = pagination_text.strip()
            
            # 빈 문자열 체크
            if not pagination_text:
                pagination_text = "1"
            
            if '/' in pagination_text:
                try:
                    total_count = int(pagination_text.split('/')[1].strip())
                except (ValueError, IndexError):
                    total_count = 1
            else:
                try:
                    total_count = int(pagination_text)
                except ValueError:
                    total_count = 1
            
            if total_count <= 0: 
                total_count = 1
            await send_update(0, f"총 {total_count}개 항목 확인.")
        except Exception as e_page:
            total_count = 1
            await send_update(0, f"페이지네이션 분석 실패 ({e_page}), 단일 항목 처리 시도.")
        
        collected_data_count_local = 0
        for i in range(total_count):
            if not self.is_running:
                await send_update((i + 1) / total_count, "크롤링이 중지되었습니다.")
                break
                
            current_progress_val = (i + 1) / total_count
            await send_update(current_progress_val, f"{i+1}/{total_count} 번째 항목 처리 시작...")
            
            try:
                student_name_element_xpath = '//*[@id="app"]/main/section/div/div[2]/div/div[2]/div[1]/strong'
                student_name_element = self.wait.until(EC.visibility_of_element_located((By.XPATH, student_name_element_xpath)))
                student_name = student_name_element.text
                
                # None 체크 및 기본값 설정
                if student_name is None:
                    student_name = f"학생_{i+1}"
                else:
                    student_name = student_name.strip()
                
                if not student_name:
                    student_name = f"학생_{i+1}"
                    
                await send_update(current_progress_val, f"이름: {student_name}")

                blog_link = ""
                try:
                    answer_view_button_xpath = '//*[@id="app"]/main/section/div/div[2]/div/div[4]/div/div/table/tbody/tr/td[6]/button'
                    answer_view_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, answer_view_button_xpath)))
                    self.driver.execute_script("arguments[0].click();", answer_view_button)
                    await send_update(current_progress_val, "과제 내용 보기 버튼 클릭.")
                    time.sleep(0.5)

                    blog_link_element_xpath = '//*[@id="modals"]/section/div/div/div/div[2]/ul/li[2]/div/p'
                    blog_link_element = self.wait.until(EC.visibility_of_element_located((By.XPATH, blog_link_element_xpath)))
                    blog_link = blog_link_element.text
                    
                    # None 체크 및 기본값 설정
                    if blog_link is None:
                        blog_link = ""
                    else:
                        blog_link = blog_link.strip()
                    
                    await send_update(current_progress_val, f"블로그 링크/내용 수집: {blog_link[:50]}...")
                    
                    close_modal_xpath_1 = '//*[@id="modals"]/section/div/div/div/div[1]/button'
                    close_modal_button_1 = self.wait.until(EC.element_to_be_clickable((By.XPATH, close_modal_xpath_1)))
                    self.driver.execute_script("arguments[0].click();", close_modal_button_1)
                    await send_update(current_progress_val, "첫 번째 모달 닫기.")
                    time.sleep(0.5)
                except TimeoutException:
                    await send_update(current_progress_val, f"{student_name}: 블로그 링크 수집 중 Timeout (항목 없음 가능성)")
                except Exception as e_blog:
                    await send_update(current_progress_val, f"{student_name}: 블로그 링크 수집 중 오류 - {e_blog}")

                self._collect_data_item(student_name, blog_link)
                collected_data_count_local += 1

                try:
                    close_modal_xpath_2 = '//*[@id="modals"]/section[2]/div/div/section/div/button[2]'
                    close_modal_button_2 = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, close_modal_xpath_2)))
                    self.driver.execute_script("arguments[0].click();", close_modal_button_2)
                    await send_update(current_progress_val, "두 번째 모달 닫기.")
                    time.sleep(0.5)
                except TimeoutException:
                    pass
                except Exception as e_modal2:
                    await send_update(current_progress_val, f"{student_name}: 두 번째 모달 닫기 중 오류 - {e_modal2}")

                if i < total_count - 1:
                    next_button_xpath = '//*[@id="app"]/main/section/div/div[2]/div/div[2]/div[2]/button[2]'
                    next_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, next_button_xpath)))
                    self.driver.execute_script("arguments[0].click();", next_button)
                    await send_update(current_progress_val, "다음 항목으로 이동.")
                    time.sleep(1)
            except Exception as e_item:
                await send_update(current_progress_val, f"{i+1}번째 항목 처리 중 주 오류: {e_item}")
                if i < total_count - 1:
                    try:
                        next_button_xpath_err = '//*[@id="app"]/main/section/div/div[2]/div/div[2]/div[2]/button[2]'
                        if self.driver.find_elements(By.XPATH, next_button_xpath_err + "[not(@disabled)]"):
                            next_button_err = self.driver.find_element(By.XPATH, next_button_xpath_err)
                            self.driver.execute_script("arguments[0].click();", next_button_err)
                            await send_update(current_progress_val, "오류 후 다음 항목 강제 이동 시도.")
                            time.sleep(1)
                        else: 
                            await send_update(current_progress_val, "다음 버튼 비활성화 또는 없음. 중단.")
                            break
                    except Exception as e_next_err:
                        await send_update(current_progress_val, f"강제 이동 중 추가 오류({e_next_err}). 중단.")
                        break
                continue
        
        await send_update(1, f"크롤링 완료. 총 {collected_data_count_local}개 데이터 수집.")
        return collected_data_count_local

    def cleanup(self):
        self._add_log("클린업 프로세스 시작...")
        if self.driver:
            try:
                self.driver.quit()
                self._add_log("드라이버 종료 완료.")
            except Exception as e:
                self._add_log(f"드라이버 종료 중 오류: {e}")
        self.driver = None
        self.is_running = False
        self.current_exam_id = None

    def get_status(self) -> Dict[str, Any]:
        return {
            "is_running": self.is_running,
            "current_exam_id": self.current_exam_id,
            "collected_count": len(self.collected_data),
            "session_id": self.session_id
        }