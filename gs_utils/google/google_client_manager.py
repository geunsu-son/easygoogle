from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.service_account import Credentials
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload
import pandas as pd
import re
import os
import io
import time
import glob
import inspect
import socket
import datetime
import decimal
from labs_modules import secret_key
from labs_modules.utils.utils import send_bot_message
import concurrent.futures

def retry_on_error(func):
    """API 요청 실패 시 .json 파일을 바꿔서 재시도하는 데코레이터"""
    def wrapper(self, *args, **kwargs):
        bot_message_list = [f"@geunsu.son `Google API 요청 횟수 초과로 작업 실패 - {func.__name__}`"]
        for attempt in range(self.max_attempts):
            try:
                return func(self, *args, **kwargs)
            except HttpError as e:
                error_message = f"⚠️ API quota error ({e.resp.status}) - retrying with next account... (attempt {attempt+1}/{self.max_attempts})\n - ℹ️ Error info: {e}"
                print(error_message)
                bot_message_list.append(error_message)
                self._build_next_service()
                time.sleep(1)
            except (TimeoutError, socket.timeout) as e:
                error_message = f"⚠️ Timeout error - retrying with next account... (attempt {attempt+1}/{self.max_attempts})\n - ℹ️ Error info: {e}"
                print(error_message)
                bot_message_list.append(error_message)
                self._build_next_service()
                time.sleep(1)
            except Exception as e:
                error_message = f"⚠️ Unknown error - retrying with next account...  (attempt {attempt+1}/{self.max_attempts})\n - ℹ️ Error info: {e}"
                print(error_message)
                bot_message_list.append(error_message)
                self._build_next_service()
                time.sleep(1)
        send_bot_message('\n'.join(bot_message_list), webhook_url=secret_key.WEBHOOK_URL_DISCORD)
        raise RuntimeError(f"🔥 작업 실패 - 최대 시도 횟수를 초과함. - {func.__name__}")
    return wrapper

class GoogleBaseManager:
    """구글 API 서비스의 기본 기능을 제공하는 클래스"""

    def __init__(self, service_name, version, scope, attempt_retry = 3, json_folder = None):
        """
        구글 API 서비스 초기화
        
        Args:
            service_name (str): 구글 API 서비스 이름
            version (str): API 버전
            scope (list): API 스코프
            attempt_retry (int, optional): 재시도 횟수. 기본값은 3
            json_folder (str, optional): 서비스 계정 키 파일이 있는 폴더 경로. 기본값은 None (labs_modules가 있는 폴더의 .secret 폴더)
        """
        if json_folder is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            json_folder = os.path.join(os.path.dirname(os.path.dirname(current_dir)), '.secret')

        json_folder = os.path.abspath(json_folder)
        self.json_files = glob.glob(os.path.join(json_folder, '*.json'))
        self.service_name = service_name
        self.version = version
        self.scope = scope

        if not self.json_files:
            raise FileNotFoundError(f"No .json files found in {json_folder}")

        # Pre-build services in parallel for faster startup, then rotate by swapping.
        _service_pool_list = self._initialize_service_pool_parallel(self.json_files)
        self._service_pool = {item["json_file"]: item for item in _service_pool_list}
        self.json_files = list(self._service_pool.keys())
        self.max_attempts = len(self.json_files) * attempt_retry

        if not self.json_files:
            raise RuntimeError(f"🔥 서비스 계정 초기화 실패 - 유효한 .json 파일이 없습니다. ({json_folder})")

        self.current_index = 0
        self.cycle_sleep_duration = 30  # Sleep duration in seconds after each full cycle
        self._build_next_service()

    def _initialize_service_pool_parallel(self, json_files):
        """
        서비스 계정별 Google API service를 미리 병렬 초기화하여 pool로 구성합니다.

        Returns:
            list[dict]: [{"json_file": str, "credentials": Credentials, "service": object}, ...]
        """
        def _build_for_json(json_file):
            credentials = Credentials.from_service_account_file(json_file, scopes=self.scope).with_subject(secret_key.DELEGATE_EMAIL)
            service = build(self.service_name, self.version, credentials=credentials)
            return {"json_file": json_file, "credentials": credentials, "service": service}

        if not json_files:
            return []

        max_workers = min(3, len(json_files))
        pool = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_by_json = {executor.submit(_build_for_json, jf): jf for jf in json_files}
            for future in concurrent.futures.as_completed(future_by_json):
                jf = future_by_json[future]
                try:
                    pool.append(future.result())
                except Exception as e:
                    print(f"⚠️ Service init failed for {os.path.basename(jf)}: {e}")

        pool.sort(key=lambda x: x["json_file"])
        return pool

    def _get_next_json(self):
        """
        다음 JSON 파일을 가져오고, 한 바퀴가 완료되면 대기 시간을 적용
        
        Returns:
            str: 다음 JSON 파일 경로
        """
        if self.current_index >= len(self.json_files):
            print(f"⏳ Cycle completed. Sleeping for {self.cycle_sleep_duration} seconds...")
            time.sleep(self.cycle_sleep_duration)
            self.current_index = 0

        json_file = self.json_files[self.current_index]
        self.current_index += 1
        return json_file

    def _build_next_service(self):
        """다음 서비스 계정으로 API 서비스 교체"""
        current_json = self._get_next_json()
        next_item = self._service_pool.get(current_json)
        if next_item is None:
            # Fallback: build on-demand if pool is missing the json file for any reason.
            self.credentials = Credentials.from_service_account_file(current_json, scopes=self.scope).with_subject(secret_key.DELEGATE_EMAIL)
            self.service = build(self.service_name, self.version, credentials=self.credentials)
        else:
            self.credentials = next_item["credentials"]
            self.service = next_item["service"]
        print(f"🔁 Switched to service account: {os.path.basename(current_json)}")

    def request_with_retry(self, func_callable):
        """
        API 요청 실패 시 재시도 로직을 구현합니다. 주어진 함수가 API 요청을 수행하고, 실패할 경우 최대 시도 횟수만큼 재시도합니다.
        각 클래스 내에 있는 함수는 일반적으로 재시도 데코레이터가 붙어있으므로 별도로 호출할 필요가 없습니다.
        하지만 클래스에 있는 함수가 아닌 경우 별도로 호출할 때 API 허용량 초과 오류가 발생할 수 있으므로 재시도 함수로 묶어주는 것을 권장합니다.

        Args:
            func_callable (callable): API 요청을 수행하는 함수. 이 함수는 서비스 객체를 인자로 받아야 합니다.

        Returns:
            dict: API 요청의 결과로 반환된 데이터.

        Raises:
            RuntimeError: 모든 계정에서 오류가 발생한 경우.
            
        * example 1: Google 스프레드시트에서 값 가져오기\n
            result = google_client_manager.request_with_retry(
                lambda service: service.spreadsheets().values().get(
                    spreadsheetId="your_spreadsheet_id", 
                    range="Sheet1!A1:Z",
                ).execute()
            )
            df = pd.DataFrame(result['values'][1:], columns=result['values'][0])

        * example 2: Google 스프레드시트에 값 업데이트\n
            result = google_client_manager.request_with_retry(
                lambda service: service.spreadsheets().values().update(
                    spreadsheetId='your_spreadsheet_id',
                    range='Sheet1!A1',
                    body={'values': [['입력할 값']]}
                ).execute()
            )
            print(f"업데이트된 셀 수: {result['updatedCells']}")

        """
        bot_message_list = [f"@geunsu.son `Google API 요청 횟수 초과로 작업 실패 - {func_callable.__name__}`"]
        for attempt in range(self.max_attempts):
            try:
                return func_callable(self.service)
            except HttpError as e:
                error_message = f"⚠️ API quota error ({e.resp.status}) - retrying with next account... (attempt {attempt+1}/{self.max_attempts})"
                print(error_message)
                bot_message_list.append(error_message)
                self._build_next_service()
                time.sleep(2)
            except (TimeoutError, socket.timeout) as e:
                error_message = f"⚠️ Timeout error - retrying with next account... (attempt {attempt+1}/{self.max_attempts})"
                print(error_message)
                bot_message_list.append(error_message)
                self._build_next_service()
                time.sleep(2)
            except Exception as e:
                error_message = f"⚠️ Unknown error - retrying with next account...  (attempt {attempt+1}/{self.max_attempts})\n - ℹ️ Error info: {e}"
                print(error_message)
                bot_message_list.append(error_message)
                self._build_next_service()
                time.sleep(2)
        send_bot_message('\n'.join(bot_message_list))
        raise RuntimeError(f"🔥 작업 실패 - 최대 시도 횟수를 초과함. - {func_callable.__name__}")

    @staticmethod
    def increment_month(ym):
        """
        주어진 연월을 다음 연월로 증가
        
        Args:
            ym (str): 연월 문자열 (예: '202401', '2401', 또는 '2024-01')
        
        Returns:
            str: 다음 연월 문자열 (예: '202402', '2024-02')
        
        Raises:
            RuntimeError: 날짜 패턴이 올바르지 않을 경우
        """
        if '-' in ym:
            year, month = [int(x) for x in ym.split('-')]
        else:
            year, month = divmod(int(ym), 100)

        if month == 12:
            year += 1
            month = 1
        else:
            month += 1

        if len(ym) > 5:
            re_ym = f"{year:04d}-{month:02d}" if '-' in ym else f"{year:04d}{month:02d}"
        elif len(ym) <= 5:
            re_ym = f"{year:02d}-{month:02d}" if '-' in ym else f"{year:02d}{month:02d}"
        else:
            raise RuntimeError(f"⚠️ {inspect.currentframe().f_code.co_name} | 날짜패턴 재확인")

        return re_ym

    @staticmethod
    def extract_spreadsheet_id(spreadsheet_url):
        """
        URL에서 파일 ID 추출
        
        Args:
            spreadsheet_url (str): 구글 스프레드시트 URL 또는 파일 ID
            
        Returns:
            str: 파일 ID
        """
        if "docs.google.com" in spreadsheet_url:
            return spreadsheet_url.split("/d/")[-1].split("/")[0]
        return spreadsheet_url
    
    @staticmethod
    def convert_sheetid_to_url(spreadsheet_id):
        """
        파일 id를 구글시트 링크로 변경경
        
        Args:
            spreadsheet_id (str): 구글 스프레드시트 ID
            
        Returns:
            str: 구글 스프레드시트 링크
        """
        return f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"

    @staticmethod
    def extract_googledrive_id(googledrive_url):
        """
        URL에서 파일 ID 추출
        
        Args:
            googledrive_url (str): 구글 드라이브 URL
            
        Returns:
            str: 파일 ID
        """
        if "drive.google.com" in googledrive_url:
            return googledrive_url.split("/folders/")[-1].split("/")[0]
        return googledrive_url
    
    @staticmethod
    def convert_googledrive_id_to_url(googledrive_id):
        """
        파일 id를 구글시트 링크로 변경경
        
        Args:
            googledrive_id (str): 구글 드라이브 ID
            
        Returns:
            str: 구글 드라이브 링크
        """
        return f"https://drive.google.com/drive/folders/{googledrive_id}"

    @staticmethod
    def convert_to_number(value):
        if isinstance(value, str):
            try:
                if '.' in value:
                    return float(value.replace(',', ''))
                else:
                    return int(value.replace(',', ''))
            except ValueError:
                return value
        return value
                
class GoogleDriveManager(GoogleBaseManager):
    """구글 드라이브 관리를 위한 클래스"""
    
    # 기본 설정 정의
    DEFAULT_SCOPES = [
        'https://www.googleapis.com/auth/drive',
    ]
    DEFAULT_SERVICE = 'drive'
    DEFAULT_VERSION = 'v3'
    
    def __init__(self, json_folder = None, scopes = None, version = None, service_name = None):
        """
        구글 드라이브 API 서비스 초기화
        
        Args:
            json_folder (str, optional): 서비스 계정 키 파일이 있는 폴더 경로
            scopes (list, optional): API 스코프 목록. 기본값은 None (DEFAULT_SCOPES 사용)
            version (str, optional): API 버전. 기본값은 None (DEFAULT_VERSION 사용)
            service_name (str, optional): 서비스 이름. 기본값은 None (DEFAULT_SERVICE 사용)
        """
        # 기본값 설정
        if scopes is None:
            scopes = self.DEFAULT_SCOPES
        if version is None:
            version = self.DEFAULT_VERSION
        if service_name is None:
            service_name = self.DEFAULT_SERVICE
            
        super().__init__(
            service_name=service_name,
            version=version,
            scope=scopes,
            json_folder=json_folder
        )

    # 파일 목록 검색 함수: 주어진 상위 폴더 ID 내의 모든 파일을 리스트로 반환합니다.
    def search_file_list_in_parent(self, parent_folder_id, pageSize=500):
        """
        주어진 상위 폴더 ID 내의 모든 파일을 리스트로 반환합니다.
        
        Args:
            parent_folder_id (str): 검색할 상위 폴더의 ID
            
        Returns:
            list: 검색된 파일의 리스트 (ID와 이름 포함)
        """
        parent_folder_id = self.extract_googledrive_id(parent_folder_id)
        query = f"'{parent_folder_id}' in parents"
        results = self.service.files().list(
            q=query,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
            fields="files(id, name, mimeType)",
            pageSize=pageSize
        ).execute()
        
        items = results.get("files", [])
        
        if not items:
            print(f"⚠️ No files found in the folder '{parent_folder_id}'.")
            return []
        else:
            print(f"✅ Found {len(items)} file(s) in the folder '{parent_folder_id}':")
            return items

    # 파일 또는 폴더 검색 함수: parent_folder_id 안에서 특정 이름의 파일 또는 폴더를 검색합니다.
    def search_item_in_parent(self, item_name, parent_folder_id, is_folder=True):
        """
        주어진 상위 폴더 ID 내에서 특정 이름의 파일 또는 폴더를 검색합니다.
        
        Args:
            item_name (str): 검색할 파일 또는 폴더의 이름
            parent_folder_id (str): 검색할 상위 폴더의 ID
            is_folder (bool): True이면 폴더를 검색하고, False이면 파일을 검색
            
        Returns:
            list: 찾은 파일 또는 폴더의 ID 리스트 또는 빈 리스트 (없을 경우)
        """

        parent_folder_id = self.extract_googledrive_id(parent_folder_id)
        mime_type = 'application/vnd.google-apps.folder' if is_folder else 'application/octet-stream'
        query = f"name='{item_name}' and mimeType='{mime_type}' and '{parent_folder_id}' in parents"
        results = self.service.files().list(
                q=query,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
                fields="files(id, name)",
                ).execute()
        items = results.get("files", [])

        if not items:
            item_type = "folder" if is_folder else "file"
            print(f"⚠️ {inspect.currentframe().f_code.co_name} | No {item_type}s found with the name '{item_name}' in the folder '{parent_folder_id}'.")
            return []
        else:
            item_type = "folder" if is_folder else "file"
            item_ids = [item['id'] for item in items]
            print(f"✅ Found {len(item_ids)} {item_type}(s): {', '.join([item['name'] for item in items])} (IDs: {', '.join(item_ids)})")
            return item_ids

    # 파일 다운로드 함수: 특정 폴더에 있는 모든 파일 다운로드
    def download_files_in_folder(self, folder_id, save_path):
        """
        주어진 폴더 ID 내의 모든 파일을 다운로드합니다.
        
        Args:
            folder_id (str): 다운로드할 파일이 있는 폴더의 ID
            save_path (str): 파일을 저장할 경로
            
        Returns:
            None
        """
        query = f"'{folder_id}' in parents"
        results = self.service.files().list(
                q=query,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
                fields="files(id, name)",
                ).execute()
        files = results.get('files', [])
        print(files)
        
        if not files:
            print(f"⚠️ {inspect.currentframe().f_code.co_name} | No files found in folder with ID '{folder_id}'.")
            return
        
        # 저장 경로가 없으면 생성
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        # 다운로드 시작
        for file in files:
            file_id = file['id']
            file_name = file['name']
            request = self.service.files().get_media(fileId=file_id)
            file_path = os.path.join(save_path, file_name)
            
            with io.FileIO(file_path, 'wb') as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    print(f"Downloading {file_name}: {int(status.progress() * 100)}% complete")
            print(f"📥 Downloaded file: {file_name} to {file_path}")
            
        print(f'✅ Done: {len(files)}개의 파일 다운로드 완료')

    def clone_file(self, file_id, new_title):
        """
        구글 스프레드시트를 복제하고 새 이름 지정
        
        Args:
            file_id (str): 복제할 스프레드시트 ID
            new_title (str): 새로운 스프레드시트 제목
            
        Returns:
            str: 복제된 파일의 ID 또는 None (실패 시)
        """
        break_point = 0
        while True:
            try:
                copied_file = self.service.files().copy(
                    fileId=file_id,
                    supportsAllDrives=True,
                    body={"name": new_title}
                ).execute()
                return copied_file['id']
            except HttpError as error:
                print(f"⚠️ {inspect.currentframe().f_code.co_name} | 파일 복제 중 오류 발생: {error}")
                break_point = break_point + 1
                time.sleep(10)
                if break_point == 5:
                    return None

    def rename_file(self, file_id, new_name):
        """
        구글 드라이브 파일 이름 변경
        Args:
            file_id (str): 이름을 변경할 파일 ID
            new_name (str): 새로운 파일 제목
        """
        try:
            self.service.files().update(fileId=self.extract_googledrive_id(file_id), body={"name": new_name}, supportsAllDrives=True).execute()
            print(f"✅ 파일 ID {file_id}: 이름 변경 완료 - 새 이름: {new_name}")
        except HttpError as error:
            print(f"⚠️ {inspect.currentframe().f_code.co_name} | 파일 이름 변경 중 오류 발생: {error}")

    def delete_file(self, file_id):
        """
        구글 드라이브 파일 삭제
        
        Args:
            file_id (str): 삭제할 파일 ID
        """
        try:
            self.service.files().delete(fileId=file_id).execute()
            print(f"✅ 파일 ID {file_id}: 삭제 완료")
        except HttpError as error:
            print(f"⚠️ {inspect.currentframe().f_code.co_name} | 파일 삭제 중 오류 발생: {error}")

    def create_folder(self, folder_name, parent_folder_id):
        """
        구글 드라이브에 폴더가 없으면 생성, 있으면 해당 폴더 ID 반환

        Args:
            folder_name (str): 생성할 폴더 이름
            parent_folder_id (str): 상위 폴더 ID
        Returns:
            str: 폴더 ID
        """
        query = (
            f"'{parent_folder_id}' in parents and "
            f"mimeType='application/vnd.google-apps.folder' and "
            f"name='{folder_name}' and trashed=false"
        )
        response = self.service.files().list(
            q=query,
            spaces='drive',
            includeItemsFromAllDrives=True,
            fields='files(id, name)',
            supportsAllDrives=True
        ).execute()
        files = response.get('files', [])
        if files:
            folder_id = files[0].get('id')
            print(f"✅ 폴더 '{folder_name}' 이미 존재 - ID: {folder_id}")
            return folder_id
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_folder_id],
        }
        folder = self.service.files().create(
            body=file_metadata, fields='id', supportsAllDrives=True
        ).execute()
        print(f"✅ 폴더 '{folder_name}' 생성 완료 - ID: {folder.get('id')}")
        return folder.get('id')

    def upload_file(self, file_path, parent_folder_id):
        """
        구글 드라이브에 파일을 업로드합니다.

        Args:
            file_path (str): 업로드할 파일 경로
            parent_folder_id (str): 상위 폴더 ID
        Returns:
            str: 업로드된 파일의 ID
        """
        file_name = os.path.basename(file_path)
        media = MediaFileUpload(file_path, resumable=True)
        file_metadata = {
            'name': file_name,
            'parents': [parent_folder_id],
        }
        file = self.service.files().create(
            body=file_metadata, media_body=media, fields='id', supportsAllDrives=True
        ).execute()
        print(f"✅ 파일 '{file_name}' 업로드 완료 - ID: {file.get('id')}")
        return file.get('id')

    def create_new_row(self, original_row, new_ym, new_file_id, new_title):
        """
        새로운 행 데이터 생성
        
        Args:
            original_row (pd.Series): 원본 행 데이터
            new_ym (str): 새로운 연월
            new_file_id (str): 새로운 파일 ID
            new_title (str): 새로운 파일 제목
            
        Returns:
            pd.Series: 새로운 행 데이터
        """
        new_row = original_row.copy()
        new_row['연월'] = new_ym
        new_row['URL or ID'] = new_file_id
        new_row['파일이름'] = new_title
        new_row['URL 전처리'] = f"https://docs.google.com/spreadsheets/d/{new_file_id}"

        preserve_columns = ['병원', '지점/데이터', '데이터', '프로그램']
        for col in preserve_columns:
            new_row[col] = original_row[col]
            
        return new_row
    
    @retry_on_error
    def update_data_with_clones(self, data, target_ym):
        """
        데이터에서 특정 연월의 스프레드시트를 복제하고 다음 연월로 정보 업데이트
        
        Args:
            data (pd.DataFrame): 병원지점별 데이터 업데이트용 URL 시트의 Data
            target_ym (str): 대상 연월 - 포맷: yyMM (예: '2411')

        Returns:
            pd.DataFrame: 업데이트된 데이터프레임
        """
        new_data = []
        target_ym_full = f"20{target_ym}"
        sheet_insert_ym = self.increment_month(target_ym)
        print(f'{target_ym} → {sheet_insert_ym} 월별 시트 복제 작업 시작!')
        
        for idx, row in data.iterrows():
            if str(row['연월']) == str(target_ym):
                try:
                    file_name = str(row['파일이름'])

                    if re.search(rf"{target_ym_full[:4]}-{target_ym_full[4:]}", file_name):
                        pattern = rf"{target_ym_full[:4]}-{target_ym_full[4:]}"
                        new_ym = self.increment_month(f"{target_ym_full[:4]}-{target_ym_full[4:]}")
                    elif re.search(rf"{target_ym_full}", file_name):
                        pattern = rf"{target_ym_full}"
                        new_ym = self.increment_month(target_ym_full)
                    elif re.search(rf"{target_ym}", file_name):
                        pattern = rf"{target_ym}"
                        new_ym = self.increment_month(target_ym)
                    else:
                        continue

                    new_title = re.sub(pattern, new_ym, file_name)
                    spreadsheet_id = self.extract_spreadsheet_id(row['URL 전처리'])
                    
                    if not spreadsheet_id:
                        print(f"행 {idx}: 유효하지 않은 URL 또는 ID")
                        continue
                    
                    new_file_id = self.clone_file(spreadsheet_id, new_title)
                    
                    if not new_file_id:
                        print(f'{new_title} 시트 생성에 실패했습니다.')
                        new_row = self.create_new_row(row, sheet_insert_ym, '시트생성 실패', new_title)
                        new_data.append(new_row)
                    else:
                        new_row = self.create_new_row(row, sheet_insert_ym, new_file_id, new_title)
                        new_data.append(new_row)
                        print(f"{file_name} => {new_title}: 파일 복제 및 데이터 업데이트 완료")
                
                except Exception as e:
                    print(f"{new_title} 처리 중 오류 발생: {str(e)}")
                    continue
        
        if new_data:
            return pd.concat([pd.DataFrame(new_data), data], ignore_index=True)
        else:
            print("복제된 데이터가 없습니다.")
            return data


class GoogleSheetManager(GoogleBaseManager):
    """구글 스프레드시트 관리를 위한 클래스"""
    
    # 기본 설정 정의
    DEFAULT_SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
    ]
    DEFAULT_SERVICE = 'sheets'
    DEFAULT_VERSION = 'v4'
    
    def __init__(self, json_folder = None, scopes = None, version = None, service_name = None):
        """
        구글 스프레드시트 API 서비스 초기화
        
        Args:
            json_folder (str, optional): 서비스 계정 키 파일이 있는 폴더 경로
            scopes (list, optional): API 스코프 목록. 기본값은 None (DEFAULT_SCOPES 사용)
            version (str, optional): API 버전. 기본값은 None (DEFAULT_VERSION 사용)
            service_name (str, optional): 서비스 이름. 기본값은 None (DEFAULT_SERVICE 사용)
        """
        # 기본값 설정
        if scopes is None:
            scopes = self.DEFAULT_SCOPES
        if version is None:
            version = self.DEFAULT_VERSION
        if service_name is None:
            service_name = self.DEFAULT_SERVICE
            
        super().__init__(
            service_name=service_name,
            version=version,
            scope=scopes,
            json_folder=json_folder
        )

    @retry_on_error
    def get_sheet_name_id_dict(self, spreadsheet_id):
        """
        구글 스프레드시트의 시트 이름과 sheetId를 dict로 반환합니다.
        Args:
            spreadsheet_id (str): 구글 스프레드시트 ID
        Returns:
            dict: {시트이름: sheetId, ...}
        """
        sheet_metadata = self.service.spreadsheets().get(spreadsheetId=self.extract_spreadsheet_id(spreadsheet_id)).execute()
        sheets = sheet_metadata.get('sheets', [])
        return {sheet['properties']['title']: sheet['properties']['sheetId'] for sheet in sheets}

    @retry_on_error
    def get_sheet_name_list(self, spreadsheet_url):
        """
        구글 스프레드시트의 시트 이름 리스트를 반환합니다.
        Args:
            spreadsheet_id (str): 구글 스프레드시트 ID
        Returns:
            list: 시트 이름 리스트
        """
        sheet_metadata = self.service.spreadsheets().get(spreadsheetId=self.extract_spreadsheet_id(spreadsheet_url)).execute()
        sheets = sheet_metadata.get('sheets', [])
        return [sheet['properties']['title'] for sheet in sheets]

    @retry_on_error
    def copy_sheet_format(
        self,
        spreadsheet_url: str,
        source_sheet_name: str,
        target_sheet_names: list,
        source_range: dict = None,
        target_range: dict = None,
    ):
        """
        구글 스프레드시트 내에서 한 시트의 서식을 여러 시트에 복사합니다.
        Args:
            spreadsheet_url (str): 구글 스프레드시트 ID (URL에서 추출)
            source_sheet_name (str): 서식을 복사할 시트 이름
            target_sheet_names (list): 서식을 붙여넣을 시트 이름 리스트
            source_range (dict, optional): 복사할 범위 (예: {"startRowIndex":0, "endRowIndex":80, "startColumnIndex":0, "endColumnIndex":50})
            target_range (dict, optional): 붙여넣을 범위 (없으면 source_range와 동일하게 적용)
        Returns:
            dict: 구글 API 응답
        """
        spreadsheet_id = self.extract_spreadsheet_id(spreadsheet_url)
        spreadsheet_url = self.convert_sheetid_to_url(spreadsheet_id)
        name_to_id = self.get_sheet_name_id_dict(spreadsheet_id)
        source_sheet_id = name_to_id.get(source_sheet_name)

        if source_sheet_id is None:
            raise ValueError(f"⚠️ {inspect.currentframe().f_code.co_name} | source_sheet_name '{source_sheet_name}'를 찾을 수 없습니다. - URL: {spreadsheet_url}")
        
        if source_range is None:
            source_range = {
                "sheetId": source_sheet_id,
                "startRowIndex": 0,
                "endRowIndex": 1000000,
                "startColumnIndex": 0,
                "endColumnIndex": 1000
            }
        else:
            source_range = dict(source_range)
            source_range["sheetId"] = source_sheet_id

        requests = []
        for target_name in target_sheet_names:
            target_sheet_id = name_to_id.get(target_name)
            if target_sheet_id is None:
                print(f"⚠️ {inspect.currentframe().f_code.co_name} | target_sheet_name '{target_name}'를 찾을 수 없습니다. - URL: {spreadsheet_url}")
                continue

            if target_range is None:
                dest_range = {k: v for k, v in source_range.items() if k != "sheetId"}
            else:
                dest_range = dict(target_range)
            
            dest_range["sheetId"] = target_sheet_id
            requests.append({
                "copyPaste": {
                    "source": source_range,
                    "destination": dest_range,
                    "pasteType": "PASTE_FORMAT"
                }
            })
        if not requests:
            raise ValueError(f"⚠️ {inspect.currentframe().f_code.co_name} | 복사할 대상 시트가 없습니다. - URL: {spreadsheet_url}")
        
        body = {"requests": requests}
        response = self.service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id, body=body
        ).execute()
        
        print(f"✅ 구글시트 서식 복사 및 붙여넣기 완료 - {spreadsheet_url}")
        return response

    @retry_on_error
    def copy_sheet_whole_values(
        self,
        spreadsheet_source_url: str,
        source_sheet_name: str,
        spreadsheet_target_url: str = None,
        target_sheet_name: str = None,
    ):
        """
        구글 스프레드시트에서 시트의 전체 값을 여러 시트에 복사합니다.
        ⚠️ 숫자의 경우 앞뒤에 명, 만, 억 등의 서식이 붙어있을 경우 문자로 복사됩니다.
        Args:
            spreadsheet_source_url (str): 구글 스프레드시트 ID (URL에서 추출)
            source_sheet_name (str): 서식을 복사할 시트 이름
            spreadsheet_target_url (str): 구글 스프레드시트 ID (URL에서 추출)
            target_sheet_name (str): 서식을 붙여넣을 시트 이름
        """

        if target_sheet_name == None:
            raise ValueError(f"⚠️ {inspect.currentframe().f_code.co_name} | target_sheet_name이 지정되지 않았습니다.")

        spreadsheet_source_id = self.extract_spreadsheet_id(spreadsheet_source_url)
        spreadsheet_source_url = self.convert_sheetid_to_url(spreadsheet_source_id)

        if spreadsheet_target_url == None:
            spreadsheet_target_url = spreadsheet_source_url

        spreadsheet_target_id = self.extract_spreadsheet_id(spreadsheet_target_url)
        spreadsheet_target_url = self.convert_sheetid_to_url(spreadsheet_target_id)

        # 보고서 복사 붙여넣기
        result = self.service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_source_id,
            range=f'{source_sheet_name}!A1:ZZZ'
        ).execute()
        values = result.get('values', [])
        values = [[self.convert_to_number(cell) for cell in row] for row in values]
        values_fillna = pd.DataFrame(values).values.tolist()
        # NaN 값을 빈 문자열로 변환
        values_fillna = [['' if pd.isna(cell) else cell for cell in row] for row in values_fillna]
        self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_target_id,
                range=f"{target_sheet_name}!A1",
                valueInputOption="USER_ENTERED",  # 또는 'RAW'
                body={"values": values_fillna},
            ).execute()
        
        print(f"✅ 구글시트 전체 값 복사 완료 - source_sheet_name: {source_sheet_name} => target_sheet_name: {target_sheet_name}, spreadsheet_url: {spreadsheet_target_url}")

    @retry_on_error
    def clear_and_set_worksheet(self, spreadsheet_url, sheet_name, df, cell_name='A1'):
        """
        워크시트를 초기화하고 주어진 데이터프레임으로 설정합니다.
        워크시트가 없는 경우 새로 생성합니다.

        Args:
            spreadsheet_url (str): Google 스프레드시트 문서의 URL 또는 ID
            sheet_name (str): 작업할 시트 탭의 이름
            df (pandas.DataFrame): 시트에 설정할 데이터프레임
        """
        # 파일 ID 추출
        spreadsheet_id = self.extract_spreadsheet_id(spreadsheet_url)
        spreadsheet_url = self.convert_sheetid_to_url(spreadsheet_id)
        
        try:
            # 시트 ID 가져오기
            sheet_metadata = self.service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            sheets = sheet_metadata.get('sheets', [])
            
            # 시트 존재 여부 확인
            sheet_id = None
            for sheet in sheets:
                if sheet['properties']['title'] == sheet_name:
                    sheet_id = sheet['properties']['sheetId']
                    break
            
            if sheet_id is None:
                # 새 시트 생성
                request = {
                    'addSheet': {
                        'properties': {
                            'title': sheet_name,
                            'gridProperties': {
                                'rowCount': 100,
                                'columnCount': 10
                            }
                        }
                    }
                }
                response = self.service.spreadsheets().batchUpdate(
                    spreadsheetId=spreadsheet_id,
                    body={'requests': [request]}
                ).execute()
                sheet_id = response['replies'][0]['addSheet']['properties']['sheetId']
            
            # 데이터프레임을 리스트로 변환
            df = df.apply(lambda col: col.astype(str) if col.apply(lambda x: isinstance(x, datetime.date)).any() else col)
            df = df.apply(lambda col: col.astype(float) if col.apply(lambda x: isinstance(x, decimal.Decimal)).any() else col)
            safe_df = df.where(pd.notnull(df), '')
            values = [safe_df.columns.tolist()] + safe_df.values.tolist()
            
            # 데이터 업데이트
            body = {
                'values': values
            }
        
            # 시트 전체 초기화 (간단하게)
            self.service.spreadsheets().values().batchClear(
                spreadsheetId=spreadsheet_id,
                body={
                    'ranges': [f'{sheet_name}!A:ZZZ']  # 전체 범위 지정
                }
            ).execute()
            
            self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=f'{sheet_name}!{cell_name}',
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            print(f"✅ 시트 초기화 및 데이터 입력 완료 (sheet_name: {sheet_name}, spreadsheet_url: {spreadsheet_url})")
            
        except Exception as e:
            print(f"⚠️ {inspect.currentframe().f_code.co_name}\n🔗 Spreadsheet URL: {spreadsheet_url} | Sheet Name: {sheet_name}\nℹ️ Error info: {str(e)}")
            raise

    @retry_on_error
    def get_dataframe_from_sheet(self, spreadsheet_url, sheet_name, skip_rows=0, range_name='A1:ZZZ'):
        """
        주어진 Google 스프레드시트 URL과 시트 이름을 사용하여 데이터를 불러와 Pandas DataFrame으로 변환합니다.

        Args:
            spreadsheet_url (str): Google 스프레드시트 문서의 URL 또는 ID
            sheet_name (str): 데이터를 불러올 시트 탭의 이름
            skip_rows (int, optional): 첫 번째 행을 건너뛸 행 수 (기본값: 0)
            range_name (str, optional): 데이터를 불러올 범위 (기본값: 'A1:ZZZ')

        Returns:
            pandas.DataFrame: 시트에서 가져온 데이터를 포함하는 데이터프레임
        """
        # 파일 ID 추출
        spreadsheet_id = self.extract_spreadsheet_id(spreadsheet_url)
        spreadsheet_url = self.convert_sheetid_to_url(spreadsheet_id)
        try:
            # 시트 메타데이터 가져오기
            sheet_metadata = self.service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            sheets = sheet_metadata.get('sheets', [])
            
            # 시트 존재 여부 확인
            sheet_exists = False
            for sheet in sheets:
                if sheet['properties']['title'] == sheet_name:
                    sheet_exists = True
                    break
            
            if not sheet_exists:
                # 시트1 또는 Sheet1 확인
                for sheet in sheets:
                    if sheet['properties']['title'] in ['시트1', 'Sheet1']:
                        sheet_name = sheet['properties']['title']
                        sheet_exists = True
                        break
            
            if not sheet_exists:
                raise ValueError(f"⚠️ {inspect.currentframe().f_code.co_name} | 시트 '{sheet_name}'를 찾을 수 없습니다. - URL: {spreadsheet_url}")
            
            # 데이터 가져오기
            result = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=f'{sheet_name}!{range_name}'  # 모든 데이터를 가져오기 위해 범위를 조정
            ).execute()
            values = result.get('values', [])
            if not values or len(values) == 1:  # 데이터가 없거나 컬럼명만 있는 경우 빈 데이터프레임 리턴
                return pd.DataFrame()
            
            # 첫 행을 컬럼명으로 사용
            headers = values[skip_rows]

            # 중복된 컬럼명이 있으면 '_1', '_2' 등을 추가하여 유니크하게 만듦
            from collections import Counter

            header_counts = Counter(headers)
            unique_headers = []
            header_seen = {}
            for h in headers:
                if header_counts[h] > 1:
                    header_seen[h] = header_seen.get(h, 0) + 1
                    unique_headers.append(f"{h}_{header_seen[h]}")
                else:
                    unique_headers.append(h)

            # 중복된 컬럼명이 있을 경우 경고 메시지 출력
            if any(count > 1 for count in header_counts.values()):
                duplicate_headers = [h for h in header_counts if header_counts[h] > 1]
                print(f"⚠️ 중복된 컬럼명 발견: {', '.join(duplicate_headers)} (총 {len(duplicate_headers)}개 중복됨)")

            data = values[skip_rows+1:]

            # 각 행의 길이를 헤더에 맞게 조정
            header_len = len(unique_headers)
            fixed_data = []
            max_row_len = max([len(row) for row in data])
            if max_row_len != header_len:
                print(f"⚠️ {inspect.currentframe().f_code.co_name} | 데이터와 컬럼명의 열 개수 상이")

                for row in data:
                    # 부족하면 빈 문자열로 채우기
                    if len(row) < header_len:
                        row = row + [''] * (header_len - len(row))
                    # 넘치면 자르기
                    elif len(row) > header_len:
                        row = row[:header_len]
                    fixed_data.append([self.convert_to_number(cell) for cell in row])
            else:
                fixed_data = [[self.convert_to_number(cell) for cell in row] for row in data]

            # 데이터프레임 생성
            df = pd.DataFrame(fixed_data, columns=unique_headers)
            print(f"📩 데이터 로드 완료 (행: {len(df)}, 열: {len(df.columns)}) (sheet_name: {sheet_name}, spreadsheet_url: {spreadsheet_url})")
            return df
            
        except Exception as e:
            print(f"⚠️ {inspect.currentframe().f_code.co_name}\n🔗 Spreadsheet URL: {spreadsheet_url} | Sheet Name: {sheet_name}\nℹ️ Error info: {str(e)}")
            raise

    @retry_on_error
    def insert_dataframe_to_worksheet(self, spreadsheet_url, sheet_name, df, cell_name='A1'):
        """
        워크시트를 초기화하고 주어진 데이터프레임으로 설정합니다.
        워크시트가 없는 경우 새로 생성합니다.

        Args:
            spreadsheet_url (str): Google 스프레드시트 문서의 URL 또는 ID
            sheet_name (str): 작업할 시트 탭의 이름
            df (pandas.DataFrame): 시트에 설정할 데이터프레임
        """
        # 파일 ID 추출
        spreadsheet_id = self.extract_spreadsheet_id(spreadsheet_url)
        spreadsheet_url = self.convert_sheetid_to_url(spreadsheet_id)
        
        try:
            # 시트 ID 가져오기
            sheet_metadata = self.service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            sheets = sheet_metadata.get('sheets', [])
            
            # 시트 존재 여부 확인
            sheet_id = None
            for sheet in sheets:
                if sheet['properties']['title'] == sheet_name:
                    sheet_id = sheet['properties']['sheetId']
                    break
            
            if sheet_id is None:
                # 새 시트 생성
                request = {
                    'addSheet': {
                        'properties': {
                            'title': sheet_name,
                            'gridProperties': {
                                'rowCount': 100,
                                'columnCount': 10
                            }
                        }
                    }
                }
                response = self.service.spreadsheets().batchUpdate(
                    spreadsheetId=spreadsheet_id,
                    body={'requests': [request]}
                ).execute()
                sheet_id = response['replies'][0]['addSheet']['properties']['sheetId']
            
            # 데이터프레임을 리스트로 변환
            df = df.apply(lambda col: col.astype(str) if col.apply(lambda x: isinstance(x, datetime.date)).any() else col)
            df = df.apply(lambda col: col.astype(float) if col.apply(lambda x: isinstance(x, decimal.Decimal)).any() else col)
            safe_df = df.where(pd.notnull(df), '')
            values = [safe_df.columns.tolist()] + safe_df.values.tolist()
            
            # 데이터 업데이트
            body = {
                'values': values
            }
            
            self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=f'{sheet_name}!{cell_name}',
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            print(f"✅ 시트 초기화 및 데이터 입력 완료 (sheet_name: {sheet_name}, spreadsheet_url: {spreadsheet_url})")
            
        except Exception as e:
            print(f"⚠️ {inspect.currentframe().f_code.co_name}\n🔗 Spreadsheet URL: {spreadsheet_url} | Sheet Name: {sheet_name}\nℹ️ Error info: {str(e)}")
            raise