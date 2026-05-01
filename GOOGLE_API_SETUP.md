# 🔑 Google API 인증 설정 가이드

`gs_utils`의 Google API 관련 기능(`GoogleDriveManager`, `GoogleSheetManager`)을 사용하려면 Google Cloud 서비스 계정 키가 필요합니다.

이 가이드는 처음부터 끝까지 설정 방법을 안내합니다.

---

## 📋 목차

1. [빠른 시작](#빠른-시작)
2. [Google Cloud 서비스 계정 키 발급](#google-cloud-서비스-계정-키-발급)
3. [JSON 키 파일 배치](#json-키-파일-배치)
4. [사용 예제](#사용-예제)
5. [문제 해결](#문제-해결)

---

## 🚀 빠른 시작

이미 Google Cloud 서비스 계정 JSON 키 파일이 있다면:

```bash
# 1. 프로젝트 루트에 .secret 폴더 생성
mkdir -p .secret

# 2. JSON 키 파일을 .secret 폴더로 이동
mv ~/Downloads/your-service-account-key.json .secret/

# 3. Python 코드에서 사용
python3 -c "from gs_utils import GoogleDriveManager; print('✅ 설정 완료!')"
```

---

## 🔐 Google Cloud 서비스 계정 키 발급

### 1단계: Google Cloud Console 접속

[https://console.cloud.google.com](https://console.cloud.google.com) 접속

### 2단계: 프로젝트 생성 또는 선택

- 새 프로젝트 생성 또는 기존 프로젝트 선택
- 프로젝트 ID를 기억해두세요

### 3단계: API 활성화

사용하려는 API를 활성화해야 합니다:

#### Google Drive API
1. 좌측 메뉴 → **API 및 서비스** → **라이브러리**
2. "Google Drive API" 검색
3. **사용 설정** 클릭

#### Google Sheets API
1. 좌측 메뉴 → **API 및 서비스** → **라이브러리**
2. "Google Sheets API" 검색
3. **사용 설정** 클릭

### 4단계: 서비스 계정 생성

1. 좌측 메뉴 → **IAM 및 관리자** → **서비스 계정**
2. **+ 서비스 계정 만들기** 클릭
3. 서비스 계정 세부정보 입력:
   - **이름**: 예) `gs-utils-service-account`
   - **설명**: 예) `gs_utils 패키지용 서비스 계정`
4. **만들기 및 계속하기** 클릭
5. 역할 선택 (선택사항):
   - 기본적으로 역할 없이도 작동
   - 특정 권한이 필요하면 역할 추가
6. **완료** 클릭

### 5단계: JSON 키 생성

1. 생성된 서비스 계정 클릭
2. **키** 탭으로 이동
3. **키 추가** → **새 키 만들기**
4. **JSON** 선택
5. **만들기** 클릭
6. JSON 파일이 자동으로 다운로드됩니다

### 6단계: 서비스 계정에 권한 부여 (중요!)

서비스 계정은 자동으로 파일 접근 권한이 없습니다. 다음 중 하나를 수행하세요:

#### 방법 1: Google Drive/Sheets 파일 공유
1. Google Drive에서 접근하려는 파일/폴더를 우클릭
2. **공유** 클릭
3. JSON 키 파일의 `client_email` 주소 입력
   - 예: `gs-utils-service-account@your-project.iam.gserviceaccount.com`
4. **편집자** 권한 부여 (필요에 따라)
5. **보내기** 클릭

#### 방법 2: 도메인 전체 위임 (G Suite/Workspace 사용자)
1. G Suite 관리 콘솔에서 도메인 전체 위임 설정
2. 자세한 내용: [Google Workspace 도메인 전체 위임](https://developers.google.com/identity/protocols/oauth2/service-account#delegatingauthority)

---

## 📁 JSON 키 파일 배치

### 방법 1: 기본 경로 사용 (권장)

프로젝트 루트에 `.secret` 폴더를 만들고 JSON 파일을 넣으세요:

```bash
your-project/
├── .secret/
│   ├── service-account-1.json
│   └── service-account-2.json  # 여러 개 가능 (API 할당량 분산)
├── your_script.py
└── ...
```

**코드에서 사용:**
```python
from gs_utils import GoogleDriveManager

# json_folder 지정 안 하면 자동으로 .secret 폴더 사용
manager = GoogleDriveManager()
```

### 방법 2: 커스텀 경로 사용

원하는 경로에 JSON 파일을 배치하고 명시적으로 지정:

```python
from gs_utils import GoogleSheetManager

manager = GoogleSheetManager(json_folder='/path/to/your/credentials')
```

### ⚠️ 보안 주의사항

**절대 Git에 커밋하지 마세요!**

`.gitignore`에 다음을 추가:
```gitignore
# Google API credentials
.secret/
*.json

# 예외: 특정 설정 파일은 커밋 가능
!package.json
!tsconfig.json
```

---

## 💻 사용 예제

### Google Drive 관리

```python
from gs_utils import GoogleDriveManager

# 초기화
drive = GoogleDriveManager()

# 파일 복제
new_file_id = drive.clone_file(
    file_id='원본_파일_ID',
    new_title='복제된_파일_이름'
)

# 폴더 생성
folder_id = drive.create_folder(
    folder_name='새_폴더',
    parent_folder_id='상위_폴더_ID'
)

# 파일 업로드
uploaded_file_id = drive.upload_file(
    file_path='로컬_파일_경로',
    parent_folder_id='폴더_ID'
)
```

### Google Sheets 관리

```python
from gs_utils import GoogleSheetManager
import pandas as pd

# 초기화
sheets = GoogleSheetManager()

# 스프레드시트에서 데이터 읽기
df = sheets.get_dataframe_from_sheet(
    spreadsheet_url='https://docs.google.com/spreadsheets/d/...',
    sheet_name='Sheet1'
)

# 데이터 쓰기
data = pd.DataFrame({'A': [1, 2, 3], 'B': ['a', 'b', 'c']})
sheets.clear_and_set_worksheet(
    spreadsheet_url='https://docs.google.com/spreadsheets/d/...',
    sheet_name='Sheet1',
    df=data
)
```

### 커스텀 경로 사용

```python
from gs_utils import GoogleDriveManager

# 특정 폴더의 JSON 키 사용
manager = GoogleDriveManager(
    json_folder='/home/user/my-credentials'
)
```

---

## 🔧 문제 해결

### 에러 1: "Google API 인증 키 폴더를 찾을 수 없습니다"

**원인**: `.secret` 폴더가 없습니다.

**해결:**
```bash
mkdir -p .secret
mv ~/Downloads/your-service-account-key.json .secret/
```

### 에러 2: "JSON 키 파일을 찾을 수 없습니다"

**원인**: 폴더는 있지만 `.json` 파일이 없습니다.

**해결:**
```bash
# JSON 파일이 있는지 확인
ls -la .secret/*.json

# 없으면 JSON 키 파일을 이동
mv ~/Downloads/your-service-account-key.json .secret/
```

### 에러 3: "서비스 계정 초기화 실패"

**원인**: JSON 파일 형식이 올바르지 않습니다.

**해결:**
- Google Cloud Console에서 JSON 키를 다시 생성하세요
- 파일이 손상되지 않았는지 확인하세요
- 올바른 JSON 형식인지 확인: `python3 -m json.tool .secret/your-key.json`

### 에러 4: "Permission denied" 또는 "403 Forbidden"

**원인**: 서비스 계정에 파일 접근 권한이 없습니다.

**해결:**
1. Google Drive/Sheets에서 파일 공유
2. JSON 키의 `client_email` 주소로 공유
3. **편집자** 권한 부여

**client_email 확인 방법:**
```bash
# Linux/macOS
cat .secret/your-key.json | grep client_email

# 또는 Python
python3 -c "import json; print(json.load(open('.secret/your-key.json'))['client_email'])"
```

### 에러 5: "API has not been used" 또는 "API not enabled"

**원인**: Google Drive API 또는 Google Sheets API가 활성화되지 않았습니다.

**해결:**
1. [Google Cloud Console](https://console.cloud.google.com) 접속
2. **API 및 서비스** → **라이브러리**
3. 필요한 API 검색 및 **사용 설정**

### 여러 서비스 계정 사용 (API 할당량 분산)

API 할당량이 부족하면 여러 개의 서비스 계정을 사용할 수 있습니다:

```bash
.secret/
├── account-1.json
├── account-2.json
└── account-3.json
```

`gs_utils`는 자동으로 모든 JSON 파일을 로드하고 할당량 초과 시 다음 계정으로 전환합니다.

---

## 📚 추가 리소스

- [Google Cloud Service Accounts](https://cloud.google.com/iam/docs/service-accounts)
- [Google Drive API Python Quickstart](https://developers.google.com/drive/api/quickstart/python)
- [Google Sheets API Python Quickstart](https://developers.google.com/sheets/api/quickstart/python)
- [Service Account Keys](https://cloud.google.com/iam/docs/creating-managing-service-account-keys)

---

## 💡 팁

1. **여러 프로젝트에서 사용**
   - 각 프로젝트마다 `.secret` 폴더 생성
   - 또는 중앙 집중식 경로 사용: `json_folder='/home/user/.google-credentials'`

2. **환경 변수 사용**
   ```python
   import os
   from gs_utils import GoogleDriveManager
   
   creds_path = os.getenv('GOOGLE_CREDS_PATH', '.secret')
   manager = GoogleDriveManager(json_folder=creds_path)
   ```

3. **테스트 환경과 프로덕션 환경 분리**
   ```python
   import os
   
   if os.getenv('ENV') == 'production':
       manager = GoogleDriveManager(json_folder='/secure/prod/creds')
   else:
       manager = GoogleDriveManager(json_folder='.secret')
   ```

---

**작성일**: 2026-05-01  
**작성자**: geunsu-son / Cursor Cloud Agent
