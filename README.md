# 🔷 EasyGoogle

**Simple and powerful Python wrapper for Google APIs**

Easy-to-use interfaces for Google Drive and Google Sheets with simplified authentication, friendly error messages, and flexible configuration.

```python
from easygoogle import Drive, Sheets

# 3 lines to start. Zero configuration hassle.
drive = Drive()
sheets = Sheets()
drive.clone_file(file_id='...', new_title='My Copy')
```

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 🚀 Quick Start

### Installation

```bash
# From PyPI (coming soon)
pip install easygoogle

# From GitHub
pip install git+https://github.com/geunsu-son/easygoogle.git

# Local development
git clone https://github.com/geunsu-son/easygoogle.git
cd easygoogle
pip install -e .
```

### Configuration (Choose One Method)

#### Method 1: Environment Variables (Recommended)
```bash
export GS_UTILS_JSON_FOLDER="/path/to/credentials"
export GS_UTILS_DELEGATE_EMAIL="user@domain.com"  # Optional
```

#### Method 2: Config File (Optional)
```bash
# Create .easygoogle_config.yaml
cp .easygoogle_config.yaml.example .easygoogle_config.yaml
# Edit the file with your settings
```

#### Method 3: Code (Highest Priority)
```python
from easygoogle import GoogleDriveManager

manager = GoogleDriveManager(json_folder='/custom/path')
```

### First Run

```python
from easygoogle import GoogleDriveManager

# Initialize (uses config from env/file/code)
manager = GoogleDriveManager()

# Your JSON keys should be in the configured folder
# Default: .secret/ folder
```

---

## ✨ Why easygoogle?

### 🎯 Core Features

| Feature | Description | Class/Function |
|---------|-------------|----------------|
| 📁 **Google Drive** | File management, copy, delete, upload | `GoogleDriveManager` |
| 📊 **Google Sheets** | Read/write data, format copy, sheet management | `GoogleSheetManager` |
| 🔑 **Easy Auth** | Environment variables, config file, or code | Config system |
| 😊 **Friendly Errors** | Clear error messages with step-by-step solutions | Built-in |
| 🔄 **Auto Retry** | Automatic retry on API quota errors | `@retry_on_error` |
| 🔗 **Utilities** | URL/ID conversion, data transformation | Helper functions |

### 💪 Advantages over alternatives

| Library | easygoogle | gspread | PyDrive2 | google-api-python-client |
|---------|----------|---------|----------|--------------------------|
| **Drive + Sheets** | ✅ | ❌ Sheets only | ❌ Drive only | ✅ |
| **Easy Auth** | ✅ 3 methods | ❌ Complex | ❌ Complex | ❌ Low-level |
| **Friendly Errors** | ✅ Detailed | ❌ | ❌ | ❌ |
| **Config System** | ✅ Flexible | ❌ | ❌ | ❌ |
| **Learning Curve** | ⭐ Easy | ⭐⭐ Medium | ⭐⭐ Medium | ⭐⭐⭐⭐ Hard |

---

## 🧪 Example Usage

### Utility Functions

```python
from easygoogle import extract_spreadsheet_id, convert_sheetid_to_url

# Extract file ID from URL
file_id = extract_spreadsheet_id('https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms')
# Result: '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'

# Convert ID to URL
url = convert_sheetid_to_url(file_id)
# Result: 'https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit'
```

### Google Drive 관리

```python
from easygoogle import GoogleDriveManager

# Google Drive 매니저 초기화
drive_manager = GoogleDriveManager()

# 파일 복제
new_file_id = drive_manager.clone_file(
    file_id='원본_파일_ID',
    new_title='새_파일_이름'
)

# 폴더 생성
folder_id = drive_manager.create_folder(
    folder_name='새_폴더',
    parent_folder_id='상위_폴더_ID'
)

# 파일 업로드
uploaded_file_id = drive_manager.upload_file(
    file_path='로컬_파일_경로',
    parent_folder_id='폴더_ID'
)
```

### Google Sheets 관리

```python
from easygoogle import GoogleSheetManager, extract_spreadsheet_id

# Google Sheets 매니저 초기화
sheet_manager = GoogleSheetManager()

# 스프레드시트에서 데이터 읽기
spreadsheet_url = 'https://docs.google.com/spreadsheets/d/...'
df = sheet_manager.get_dataframe_from_sheet(
    spreadsheet_url=spreadsheet_url,
    sheet_name='Sheet1'
)

# 스프레드시트에 데이터 쓰기
import pandas as pd
data = pd.DataFrame({'A': [1, 2, 3], 'B': ['a', 'b', 'c']})
sheet_manager.clear_and_set_worksheet(
    spreadsheet_url=spreadsheet_url,
    sheet_name='Sheet1',
    df=data
)

# 시트 서식 복사
sheet_manager.copy_sheet_format(
    spreadsheet_url=spreadsheet_url,
    source_sheet_name='템플릿',
    target_sheet_names=['새시트1', '새시트2']
)
```

### Complete Example: Data Pipeline

```python
from easygoogle import Drive, Sheets
import pandas as pd

# Initialize managers
drive = Drive()
sheets = Sheets()

# Read data from Google Sheets
df = sheets.get_dataframe_from_sheet(
    spreadsheet_url='https://docs.google.com/spreadsheets/d/...',
    sheet_name='RawData'
)

# Process data
df_processed = df[df['status'] == 'active'].groupby('category').sum()

# Write results back
sheets.clear_and_set_worksheet(
    spreadsheet_url='https://docs.google.com/spreadsheets/d/...',
    sheet_name='Processed',
    df=df_processed
)

# Backup to Drive
drive.upload_file(
    file_path='backup.csv',
    parent_folder_id='your-folder-id'
)

print("✅ Pipeline completed!")
```

---

## 📁 Package Structure

```
easygoogle/
├── __init__.py              # Main exports
├── config.py                # Configuration system
└── google/
    ├── __init__.py          # Google API exports
    ├── google_client_manager.py  # Core managers
    └── utils.py             # Utility functions
```

### 🔧 Core Components

- **`GoogleDriveManager`**: Google Drive file/folder management
- **`GoogleSheetManager`**: Google Sheets data operations
- **`GoogleBaseManager`**: Base class for all Google API managers
- **`Config`**: Flexible configuration system
- **Utility functions**: URL/ID conversion, data transformation

---

## 🗺️ Roadmap

### ✅ Completed (v0.3.0)
- Google Drive management
- Google Sheets management  
- Flexible configuration system (env/file/code)
- Friendly error messages
- Automatic retry on quota errors
- Comprehensive tests (29/29 passing)

### 🚀 Coming Soon
- [ ] Google Calendar API support
- [ ] Google Docs API support
- [ ] Google Gmail API support
- [ ] Async/await support
- [ ] Batch operations optimization
- [ ] More examples and tutorials

### 💡 Ideas
- Google Meet API integration
- Google Forms API integration
- CLI tool for common operations

---

## 🔑 Google API Setup

Google Drive 및 Google Sheets 기능을 사용하려면 서비스 계정 JSON 키가 필요합니다.

### Quick Setup
```bash
# 1. Create credentials folder
mkdir -p .secret

# 2. Download JSON key from Google Cloud Console
# https://console.cloud.google.com → IAM → Service Accounts → Keys

# 3. Move the key file
mv ~/Downloads/your-service-account-key.json .secret/

# 4. Done! The package will auto-detect the keys
```

**Detailed setup guide**: See [GOOGLE_API_SETUP.md](GOOGLE_API_SETUP.md)

### Security Note
⚠️ **Never commit JSON keys to git!**
```bash
# Already in .gitignore
.secret/
.easygoogle_config.yaml
```

---

## 🙌 Author

손근수(geunsu-son)
데이터 기반 문제 해결을 즐기는 데이터 엔지니어

---

> PR, 아이디어, 개선 제안은 언제든지 환영합니다!
