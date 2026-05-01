# 🔨 Config 시스템 구현 가이드

**기반**: CONFIG_DESIGN_PROPOSAL.md의 **방안 3: 하이브리드**  
**목표**: `labs_modules` 의존성 제거 + 유연한 설정 시스템

---

## 📋 구현 체크리스트

### Phase 1: Config 모듈 생성
- [ ] `gs_utils/config.py` 생성
- [ ] Config 클래스 구현
- [ ] 환경변수 지원
- [ ] 설정 파일 지원 (선택적)
- [ ] 단위 테스트 작성

### Phase 2: GoogleBaseManager 수정
- [ ] Config import 추가
- [ ] `__init__()` 파라미터 추가
- [ ] Config 우선순위 적용
- [ ] `labs_modules` 의존성 제거
- [ ] 하위 호환성 테스트

### Phase 3: 문서화
- [ ] CONFIG.md 사용 가이드
- [ ] README.md 업데이트
- [ ] 예제 설정 파일
- [ ] 마이그레이션 가이드

### Phase 4: 배포
- [ ] 모든 테스트 통과
- [ ] Git 커밋 & PR
- [ ] 버전 업데이트 (0.2.0 → 0.3.0)

---

## 📁 파일 구조

```
gs_utils/
├── __init__.py
├── __version__.py
├── config.py                    # NEW
├── decorators.py
├── google/
│   ├── __init__.py
│   ├── google_client_manager.py  # MODIFIED
│   └── utils.py
└── ...

.gs_utils_config.yaml.example     # NEW (선택적 템플릿)
```

---

## 💻 구현 코드

### 1. gs_utils/config.py (NEW)

```python
"""
gs_utils 설정 관리

우선순위:
1. 코드에서 직접 지정 (가장 높음)
2. 환경변수 (GS_UTILS_*)
3. 설정 파일 (.gs_utils_config.yaml) - 선택적
4. 기본값 (가장 낮음)

사용 예시:
    >>> from gs_utils.config import config
    >>> 
    >>> # 환경변수로 설정
    >>> import os
    >>> os.environ['GS_UTILS_JSON_FOLDER'] = '/custom/path'
    >>> 
    >>> # Config 객체 사용
    >>> json_folder = config.get_json_folder()
"""
import os
from typing import Optional, Dict, Any
from pathlib import Path


class Config:
    """
    gs_utils 설정 관리 클래스
    
    이 클래스는 싱글톤 패턴으로 구현되어 
    애플리케이션 전체에서 하나의 인스턴스만 사용됩니다.
    """
    
    _instance = None
    _config_data: Optional[Dict[str, Any]] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """초기화 시 설정 파일 로드 시도"""
        if Config._config_data is None:
            Config._config_data = self._load_config_file()
    
    def get_json_folder(self, override: Optional[str] = None) -> str:
        """
        Google API JSON 키 파일 폴더 경로
        
        Args:
            override: 직접 지정한 경로 (최우선)
            
        Returns:
            JSON 키 파일 폴더 경로
            
        우선순위:
            1. override 파라미터
            2. 환경변수 GS_UTILS_JSON_FOLDER
            3. 설정 파일의 google.json_folder
            4. 기본값 '.secret'
        """
        if override is not None:
            return override
        
        # 환경변수
        env_val = os.getenv('GS_UTILS_JSON_FOLDER')
        if env_val:
            return env_val
        
        # 설정 파일
        if self._config_data:
            file_val = self._config_data.get('google', {}).get('json_folder')
            if file_val:
                return file_val
        
        # 기본값
        return '.secret'
    
    def get_delegate_email(self, override: Optional[str] = None) -> Optional[str]:
        """
        G Suite 도메인 전체 위임 이메일
        
        Args:
            override: 직접 지정한 이메일 (최우선)
            
        Returns:
            위임 이메일 또는 None
            
        우선순위:
            1. override 파라미터
            2. 환경변수 GS_UTILS_DELEGATE_EMAIL
            3. 설정 파일의 google.delegate_email
            4. None (기본값)
        """
        if override is not None:
            return override
        
        # 환경변수
        env_val = os.getenv('GS_UTILS_DELEGATE_EMAIL')
        if env_val:
            return env_val
        
        # 설정 파일
        if self._config_data:
            return self._config_data.get('google', {}).get('delegate_email')
        
        return None
    
    def get_discord_webhook(self, override: Optional[str] = None) -> Optional[str]:
        """
        Discord Webhook URL (에러 알림용)
        
        Args:
            override: 직접 지정한 URL (최우선)
            
        Returns:
            Webhook URL 또는 None
            
        우선순위:
            1. override 파라미터
            2. 환경변수 GS_UTILS_DISCORD_WEBHOOK
            3. 설정 파일의 notifications.discord_webhook
            4. None (기본값)
        """
        if override is not None:
            return override
        
        # 환경변수
        env_val = os.getenv('GS_UTILS_DISCORD_WEBHOOK')
        if env_val:
            return env_val
        
        # 설정 파일
        if self._config_data:
            return self._config_data.get('notifications', {}).get('discord_webhook')
        
        return None
    
    def get_max_retries(self, override: Optional[int] = None) -> int:
        """
        API 재시도 최대 횟수
        
        Args:
            override: 직접 지정한 횟수 (최우선)
            
        Returns:
            재시도 횟수 (기본값 3)
        """
        if override is not None:
            return override
        
        # 환경변수
        env_val = os.getenv('GS_UTILS_MAX_RETRIES')
        if env_val:
            try:
                return int(env_val)
            except ValueError:
                pass
        
        # 설정 파일
        if self._config_data:
            file_val = self._config_data.get('google', {}).get('max_retries')
            if file_val is not None:
                return int(file_val)
        
        # 기본값
        return 3
    
    def _load_config_file(self) -> Dict[str, Any]:
        """
        설정 파일 로드 (.gs_utils_config.yaml)
        
        Returns:
            설정 딕셔너리 (없으면 빈 딕셔너리)
        """
        # 설정 파일 경로 (환경변수로 지정 가능)
        config_path = os.getenv('GS_UTILS_CONFIG', '.gs_utils_config.yaml')
        
        if not os.path.exists(config_path):
            return {}
        
        try:
            # pyyaml이 있으면 사용 (선택적 의존성)
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return data if data else {}
        except ImportError:
            # yaml 없으면 무시 (환경변수로 대체 가능)
            return {}
        except Exception as e:
            print(f"⚠️ Failed to load config file '{config_path}': {e}")
            return {}
    
    def reload(self):
        """설정 파일 다시 로드"""
        Config._config_data = self._load_config_file()
    
    def get_all(self) -> Dict[str, Any]:
        """
        현재 적용된 모든 설정 반환 (디버깅용)
        
        Returns:
            설정 딕셔너리
        """
        return {
            'google': {
                'json_folder': self.get_json_folder(),
                'delegate_email': self.get_delegate_email(),
                'max_retries': self.get_max_retries(),
            },
            'notifications': {
                'discord_webhook': self.get_discord_webhook(),
            }
        }


# 싱글톤 인스턴스 (전역에서 사용)
config = Config()
```

---

### 2. gs_utils/google/google_client_manager.py (MODIFIED)

#### 변경 부분 1: Import 수정

```python
# BEFORE
try:
    from labs_modules import secret_key
    from labs_modules.utils.utils import send_bot_message
    HAS_LABS_MODULES = True
except ImportError:
    HAS_LABS_MODULES = False
    secret_key = None
    send_bot_message = None
```

```python
# AFTER
from gs_utils.config import config

# Discord 알림은 선택적 기능
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
```

#### 변경 부분 2: __init__() 수정

```python
# BEFORE
def __init__(self, service_name, version, scope, attempt_retry=3, json_folder=None):
    if json_folder is None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_folder = os.path.join(os.path.dirname(os.path.dirname(current_dir)), '.secret')
```

```python
# AFTER
def __init__(self, service_name, version, scope, 
             attempt_retry=None, 
             json_folder=None,
             delegate_email=None,
             discord_webhook=None):
    """
    구글 API 서비스 초기화
    
    Args:
        service_name: 구글 API 서비스 이름
        version: API 버전
        scope: API 스코프
        attempt_retry: 재시도 횟수 (기본값: 환경변수 또는 3)
        json_folder: JSON 키 파일 폴더 (기본값: 환경변수 또는 '.secret')
        delegate_email: G Suite 도메인 전체 위임 이메일 (선택)
        discord_webhook: Discord webhook URL (선택)
    """
    # Config 시스템 사용
    json_folder = config.get_json_folder(json_folder)
    self.delegate_email = config.get_delegate_email(delegate_email)
    self.discord_webhook = config.get_discord_webhook(discord_webhook)
    
    if attempt_retry is None:
        attempt_retry = config.get_max_retries()
    
    # ... 기존 코드 계속
```

#### 변경 부분 3: 서비스 계정 초기화 수정

```python
# BEFORE
def _build_for_json(json_file):
    credentials = Credentials.from_service_account_file(json_file, scopes=self.scope)
    if HAS_LABS_MODULES and secret_key and hasattr(secret_key, 'DELEGATE_EMAIL'):
        credentials = credentials.with_subject(secret_key.DELEGATE_EMAIL)
    service = build(self.service_name, self.version, credentials=credentials)
    return {"json_file": json_file, "credentials": credentials, "service": service}
```

```python
# AFTER
def _build_for_json(json_file):
    credentials = Credentials.from_service_account_file(json_file, scopes=self.scope)
    
    # 도메인 전체 위임 (선택적)
    if self.delegate_email:
        credentials = credentials.with_subject(self.delegate_email)
    
    service = build(self.service_name, self.version, credentials=credentials)
    return {"json_file": json_file, "credentials": credentials, "service": service}
```

#### 변경 부분 4: Discord 알림 수정

```python
# BEFORE
if HAS_LABS_MODULES and send_bot_message and secret_key:
    send_bot_message('\n'.join(bot_message_list), webhook_url=secret_key.WEBHOOK_URL_DISCORD)
```

```python
# AFTER
if self.discord_webhook and HAS_REQUESTS:
    self._send_discord_notification('\n'.join(bot_message_list))
```

#### 신규 메서드 추가

```python
def _send_discord_notification(self, message: str):
    """Discord webhook으로 알림 전송"""
    if not self.discord_webhook or not HAS_REQUESTS:
        return
    
    try:
        import requests
        payload = {'content': message}
        requests.post(self.discord_webhook, json=payload, timeout=5)
    except Exception as e:
        print(f"⚠️ Discord notification failed: {e}")
```

---

### 3. 예제 설정 파일

#### .gs_utils_config.yaml.example

```yaml
# gs_utils 설정 파일 예시
# 이 파일을 .gs_utils_config.yaml로 복사하여 사용하세요

# Google API 설정
google:
  # JSON 키 파일이 있는 폴더 경로
  json_folder: ".secret"
  
  # G Suite 도메인 전체 위임 이메일 (선택사항)
  # G Suite/Workspace 사용자만 필요
  delegate_email: "user@yourdomain.com"
  
  # API 재시도 최대 횟수
  max_retries: 3

# 알림 설정 (선택사항)
notifications:
  # Discord webhook URL
  # API 에러 발생 시 알림을 받으려면 설정하세요
  discord_webhook: "https://discord.com/api/webhooks/YOUR_WEBHOOK_URL"

# 주의사항:
# 1. 이 파일은 .gitignore에 추가하세요
# 2. 민감한 정보(webhook URL 등)는 환경변수 사용을 권장합니다
# 3. 환경변수가 설정 파일보다 우선순위가 높습니다
```

---

## 🧪 테스트 코드

### tests/test_config.py (NEW)

```python
"""Tests for config system"""
import os
import pytest
import tempfile


def test_config_singleton():
    """Config는 싱글톤이어야 함"""
    from gs_utils.config import Config, config
    
    config1 = Config()
    config2 = Config()
    
    assert config1 is config2
    assert config1 is config


def test_json_folder_default():
    """기본 json_folder는 '.secret'"""
    from gs_utils.config import config
    
    # 환경변수 초기화
    os.environ.pop('GS_UTILS_JSON_FOLDER', None)
    config.reload()
    
    assert config.get_json_folder() == '.secret'


def test_json_folder_env():
    """환경변수가 기본값보다 우선"""
    from gs_utils.config import config
    
    os.environ['GS_UTILS_JSON_FOLDER'] = '/custom/path'
    config.reload()
    
    assert config.get_json_folder() == '/custom/path'
    
    # Clean up
    os.environ.pop('GS_UTILS_JSON_FOLDER', None)


def test_json_folder_override():
    """직접 지정이 환경변수보다 우선"""
    from gs_utils.config import config
    
    os.environ['GS_UTILS_JSON_FOLDER'] = '/env/path'
    config.reload()
    
    assert config.get_json_folder('/override/path') == '/override/path'
    
    # Clean up
    os.environ.pop('GS_UTILS_JSON_FOLDER', None)


def test_delegate_email_none_by_default():
    """기본값은 None"""
    from gs_utils.config import config
    
    os.environ.pop('GS_UTILS_DELEGATE_EMAIL', None)
    config.reload()
    
    assert config.get_delegate_email() is None


def test_delegate_email_env():
    """환경변수로 설정 가능"""
    from gs_utils.config import config
    
    os.environ['GS_UTILS_DELEGATE_EMAIL'] = 'test@example.com'
    config.reload()
    
    assert config.get_delegate_email() == 'test@example.com'
    
    # Clean up
    os.environ.pop('GS_UTILS_DELEGATE_EMAIL', None)


def test_max_retries_default():
    """기본 재시도 횟수는 3"""
    from gs_utils.config import config
    
    os.environ.pop('GS_UTILS_MAX_RETRIES', None)
    config.reload()
    
    assert config.get_max_retries() == 3


def test_max_retries_env():
    """환경변수로 재시도 횟수 변경"""
    from gs_utils.config import config
    
    os.environ['GS_UTILS_MAX_RETRIES'] = '5'
    config.reload()
    
    assert config.get_max_retries() == 5
    
    # Clean up
    os.environ.pop('GS_UTILS_MAX_RETRIES', None)


def test_config_file_yaml():
    """YAML 설정 파일 로드"""
    from gs_utils.config import Config
    
    # 임시 설정 파일 생성
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("""
google:
  json_folder: "/file/path"
  delegate_email: "file@example.com"
  max_retries: 7
notifications:
  discord_webhook: "https://discord.webhook"
""")
        config_path = f.name
    
    try:
        # 설정 파일 경로 지정
        os.environ['GS_UTILS_CONFIG'] = config_path
        
        # 새 Config 인스턴스로 reload
        test_config = Config()
        test_config.reload()
        
        # 환경변수가 없으면 파일에서 읽음
        os.environ.pop('GS_UTILS_JSON_FOLDER', None)
        os.environ.pop('GS_UTILS_DELEGATE_EMAIL', None)
        os.environ.pop('GS_UTILS_MAX_RETRIES', None)
        os.environ.pop('GS_UTILS_DISCORD_WEBHOOK', None)
        
        test_config.reload()
        
        assert test_config.get_json_folder() == "/file/path"
        assert test_config.get_delegate_email() == "file@example.com"
        assert test_config.get_max_retries() == 7
        assert test_config.get_discord_webhook() == "https://discord.webhook"
        
    finally:
        # Clean up
        os.unlink(config_path)
        os.environ.pop('GS_UTILS_CONFIG', None)


def test_priority_order():
    """우선순위 테스트: override > env > file > default"""
    from gs_utils.config import Config
    
    # 설정 파일 생성
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("google:\n  json_folder: '/file/path'\n")
        config_path = f.name
    
    try:
        os.environ['GS_UTILS_CONFIG'] = config_path
        os.environ['GS_UTILS_JSON_FOLDER'] = '/env/path'
        
        test_config = Config()
        test_config.reload()
        
        # 환경변수가 파일보다 우선
        assert test_config.get_json_folder() == '/env/path'
        
        # override가 환경변수보다 우선
        assert test_config.get_json_folder('/override/path') == '/override/path'
        
    finally:
        os.unlink(config_path)
        os.environ.pop('GS_UTILS_CONFIG', None)
        os.environ.pop('GS_UTILS_JSON_FOLDER', None)


def test_get_all():
    """get_all()로 현재 설정 확인"""
    from gs_utils.config import config
    
    os.environ['GS_UTILS_JSON_FOLDER'] = '/test/path'
    config.reload()
    
    all_config = config.get_all()
    
    assert 'google' in all_config
    assert all_config['google']['json_folder'] == '/test/path'
    assert 'notifications' in all_config
    
    # Clean up
    os.environ.pop('GS_UTILS_JSON_FOLDER', None)
```

---

## 📖 사용 가이드

### CONFIG.md (NEW)

```markdown
# 🔧 gs_utils 설정 가이드

## 설정 방법

gs_utils는 3가지 방법으로 설정할 수 있습니다:

### 1. 환경변수 (권장)

```bash
# Google API 설정
export GS_UTILS_JSON_FOLDER="/path/to/credentials"
export GS_UTILS_DELEGATE_EMAIL="user@domain.com"
export GS_UTILS_MAX_RETRIES="5"

# 알림 설정
export GS_UTILS_DISCORD_WEBHOOK="https://discord.com/api/webhooks/..."
```

### 2. 설정 파일

프로젝트 루트에 `.gs_utils_config.yaml` 파일 생성:

```yaml
google:
  json_folder: ".secret"
  delegate_email: "user@domain.com"
  max_retries: 3

notifications:
  discord_webhook: "https://..."
```

### 3. 코드에서 직접

```python
from gs_utils import GoogleDriveManager

manager = GoogleDriveManager(
    json_folder='/custom/path',
    delegate_email='user@domain.com',
    discord_webhook='https://...'
)
```

## 우선순위

```
코드에서 직접 > 환경변수 > 설정 파일 > 기본값
```

## 보안

⚠️ **중요**: 민감한 정보는 환경변수 사용을 권장합니다.

```gitignore
# .gitignore에 추가
.gs_utils_config.yaml
.env
```
```

---

## 🚀 배포 계획

### 버전 업데이트

- **현재**: v0.2.0
- **다음**: v0.3.0 (Breaking Changes 없음, 새 기능 추가)

### Breaking Changes 없음

기존 코드는 그대로 작동:

```python
# 기존 코드 - 여전히 작동 ✅
manager = GoogleDriveManager()
manager = GoogleDriveManager(json_folder='/custom')
```

### 새로운 기능

```python
# 새로운 기능 ✅
manager = GoogleDriveManager(
    delegate_email='user@domain.com',
    discord_webhook='https://...'
)
```

---

## ✅ 완료 체크리스트

구현 전 확인:
- [x] 설계 문서 작성
- [x] 구현 가이드 작성
- [ ] 사용자 피드백 받기
- [ ] 구현 승인

구현 후 확인:
- [ ] 코드 구현
- [ ] 테스트 작성 및 통과
- [ ] 문서 작성
- [ ] PR 생성
- [ ] 리뷰 및 머지

---

**다음 단계**: 사용자 피드백 및 승인 후 구현 시작

**예상 작업 시간**: 약 1-2시간
