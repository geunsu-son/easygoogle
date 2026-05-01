# 🔧 easygoogle Config 시스템 설계 제안서

**작성일**: 2026-05-01  
**목적**: `secret_key.py` 의존성 제거 및 유연한 config 시스템 구축

---

## 📊 현재 상황 분석

### 현재 구조

```python
# easygoogle/google/google_client_manager.py

try:
    from labs_modules import secret_key
    from labs_modules.utils.utils import send_bot_message
    HAS_LABS_MODULES = True
except ImportError:
    HAS_LABS_MODULES = False
    secret_key = None
```

### 사용 위치

1. **WEBHOOK_URL_DISCORD**: Discord webhook으로 에러 알림 전송
2. **DELEGATE_EMAIL**: G Suite 도메인 전체 위임용 이메일
3. **(추론) JSON_FOLDER_PATH**: JSON 키 파일 폴더 경로

### 문제점

❌ **외부 의존성**: `labs_modules`라는 외부 패키지에 의존  
❌ **유연성 부족**: 다른 사용자가 config를 커스터마이즈하기 어려움  
❌ **명확하지 않은 설정**: 어떤 설정이 가능한지 문서화되지 않음  
❌ **테스트 어려움**: Mock 설정이 복잡함

---

## 🎯 목표

### 필수 요구사항

1. ✅ **외부 의존성 제거**: `labs_modules` 의존성 제거
2. ✅ **유연한 설정**: 환경변수, 파일, 코드 등 다양한 방법 지원
3. ✅ **하위 호환성**: 기존 코드가 계속 작동
4. ✅ **명확한 문서**: 설정 방법을 명확히 문서화
5. ✅ **테스트 용이성**: 테스트 시 쉽게 Mock 가능

### 선택 요구사항

- 🎯 환경별 설정 (dev, staging, prod)
- 🎯 설정 검증 (validation)
- 🎯 기본값 제공

---

## 💡 설계 방안 (3가지)

### 방안 1: 환경변수 기반 (Simple & Standard) ⭐ 추천

가장 표준적이고 간단한 방법.

#### 구조

```python
# easygoogle/config.py
import os

class Config:
    """easygoogle 설정 관리"""
    
    # Google API 설정
    GOOGLE_JSON_FOLDER = os.getenv('GS_UTILS_JSON_FOLDER', '.secret')
    GOOGLE_DELEGATE_EMAIL = os.getenv('GS_UTILS_DELEGATE_EMAIL', None)
    
    # 알림 설정
    DISCORD_WEBHOOK_URL = os.getenv('GS_UTILS_DISCORD_WEBHOOK', None)
    
    # 재시도 설정
    MAX_RETRY_ATTEMPTS = int(os.getenv('GS_UTILS_MAX_RETRIES', '3'))
    
    @classmethod
    def from_file(cls, config_path):
        """파일에서 설정 로드"""
        # .env 파일이나 .ini 파일 지원
        pass
```

#### 사용 예시

```bash
# 환경변수로 설정
export GS_UTILS_JSON_FOLDER="/path/to/credentials"
export GS_UTILS_DELEGATE_EMAIL="user@domain.com"
export GS_UTILS_DISCORD_WEBHOOK="https://discord.com/api/webhooks/..."
```

```python
# Python 코드에서 사용
from easygoogle import GoogleDriveManager

# 환경변수 자동 적용
manager = GoogleDriveManager()

# 또는 직접 지정 (우선순위 높음)
manager = GoogleDriveManager(
    json_folder='/custom/path',
    delegate_email='user@domain.com'
)
```

#### 장점

✅ **표준적**: 12-Factor App 원칙 준수  
✅ **간단함**: 추가 파일 불필요  
✅ **Docker/K8s 친화적**: ConfigMap, Secret 쉽게 연동  
✅ **보안**: 민감 정보를 코드에서 분리  
✅ **환경별 설정 용이**: dev/prod 환경 분리 쉬움

#### 단점

❌ 많은 설정이 필요하면 환경변수가 많아짐  
❌ 타입 검증이 런타임에 발생

---

### 방안 2: Config 파일 기반 (Flexible & Organized)

설정이 많고 복잡할 때 적합.

#### 구조

```python
# .easygoogle_config.yaml (프로젝트 루트)
google:
  json_folder: ".secret"
  delegate_email: "user@domain.com"
  max_retries: 3

notifications:
  discord_webhook: "https://discord.com/api/webhooks/..."
  
logging:
  level: "INFO"
  file: "easygoogle.log"
```

```python
# easygoogle/config.py
import yaml
import os

class Config:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """설정 파일 로드 (우선순위: 명시적 경로 > 현재 디렉토리 > 기본값)"""
        config_path = os.getenv('GS_UTILS_CONFIG', '.easygoogle_config.yaml')
        
        if os.path.exists(config_path):
            with open(config_path) as f:
                self._config = yaml.safe_load(f)
        else:
            self._config = self._get_defaults()
    
    def get(self, path, default=None):
        """점 표기법으로 설정 접근: config.get('google.json_folder')"""
        keys = path.split('.')
        value = self._config
        for key in keys:
            value = value.get(key, {})
        return value or default
```

#### 사용 예시

```python
from easygoogle.config import Config

config = Config()
json_folder = config.get('google.json_folder', '.secret')
```

#### 장점

✅ **구조화**: 계층적 설정 관리  
✅ **가독성**: YAML/JSON으로 설정 명확  
✅ **그룹화**: 관련 설정을 함께 관리  
✅ **주석 가능**: YAML에 주석으로 설명 추가

#### 단점

❌ 추가 의존성 (pyyaml)  
❌ 파일 관리 필요 (.gitignore 등)  
❌ 환경변수보다 복잡

---

### 방안 3: 하이브리드 (Environment + File + Code)

환경변수와 파일을 모두 지원하며 우선순위 적용.

#### 우선순위

```
1. 코드에서 직접 지정 (가장 높음)
   ↓
2. 환경변수
   ↓
3. 설정 파일 (.easygoogle_config.yaml)
   ↓
4. 기본값 (가장 낮음)
```

#### 구조

```python
# easygoogle/config.py
import os
from typing import Optional
from pathlib import Path

class Config:
    """
    easygoogle 설정 관리 클래스
    
    우선순위:
    1. 직접 지정
    2. 환경변수 (GS_UTILS_*)
    3. 설정 파일 (.easygoogle_config.yaml)
    4. 기본값
    """
    
    _instance = None
    _config_file = None
    
    def __init__(self):
        if Config._config_file is None:
            Config._config_file = self._load_config_file()
    
    def get_json_folder(self, override: Optional[str] = None) -> str:
        """JSON 키 폴더 경로 가져오기"""
        if override:
            return override
        
        # 환경변수 확인
        env_val = os.getenv('GS_UTILS_JSON_FOLDER')
        if env_val:
            return env_val
        
        # 설정 파일 확인
        if self._config_file:
            file_val = self._config_file.get('google', {}).get('json_folder')
            if file_val:
                return file_val
        
        # 기본값
        return '.secret'
    
    def get_delegate_email(self, override: Optional[str] = None) -> Optional[str]:
        """G Suite 도메인 전체 위임 이메일"""
        if override:
            return override
        
        env_val = os.getenv('GS_UTILS_DELEGATE_EMAIL')
        if env_val:
            return env_val
        
        if self._config_file:
            return self._config_file.get('google', {}).get('delegate_email')
        
        return None
    
    def get_discord_webhook(self) -> Optional[str]:
        """Discord webhook URL"""
        env_val = os.getenv('GS_UTILS_DISCORD_WEBHOOK')
        if env_val:
            return env_val
        
        if self._config_file:
            return self._config_file.get('notifications', {}).get('discord_webhook')
        
        return None
    
    def _load_config_file(self) -> dict:
        """설정 파일 로드"""
        config_path = os.getenv('GS_UTILS_CONFIG', '.easygoogle_config.yaml')
        
        if not os.path.exists(config_path):
            return {}
        
        try:
            import yaml
            with open(config_path) as f:
                return yaml.safe_load(f) or {}
        except ImportError:
            # yaml 없으면 무시
            return {}
        except Exception as e:
            print(f"⚠️ Config file load failed: {e}")
            return {}

# 싱글톤 인스턴스
config = Config()
```

#### 사용 예시

```python
from easygoogle import GoogleDriveManager
from easygoogle.config import config

# 방법 1: 환경변수
# export GS_UTILS_JSON_FOLDER="/path/to/creds"
manager = GoogleDriveManager()

# 방법 2: 설정 파일
# .easygoogle_config.yaml 생성
manager = GoogleDriveManager()

# 방법 3: 코드에서 직접 (우선순위 최고)
manager = GoogleDriveManager(json_folder='/custom/path')
```

#### 장점

✅ **유연성 최대**: 모든 방법 지원  
✅ **명확한 우선순위**: 예측 가능한 동작  
✅ **하위 호환성**: 기존 코드 그대로 작동  
✅ **점진적 마이그레이션**: 단계적으로 전환 가능

#### 단점

❌ 복잡도 증가  
❌ 디버깅 시 어느 소스에서 값이 왔는지 추적 필요

---

## 📋 비교표

| 항목 | 환경변수 | 파일 | 하이브리드 |
|------|----------|------|------------|
| **복잡도** | ⭐ 낮음 | ⭐⭐ 중간 | ⭐⭐⭐ 높음 |
| **유연성** | ⭐⭐ 중간 | ⭐⭐⭐ 높음 | ⭐⭐⭐⭐ 최고 |
| **표준성** | ⭐⭐⭐⭐ 매우 높음 | ⭐⭐⭐ 높음 | ⭐⭐⭐ 높음 |
| **Docker/K8s** | ⭐⭐⭐⭐ 최적 | ⭐⭐ 보통 | ⭐⭐⭐ 좋음 |
| **설정 많을 때** | ⭐⭐ 불편 | ⭐⭐⭐⭐ 편함 | ⭐⭐⭐⭐ 편함 |
| **보안** | ⭐⭐⭐⭐ 우수 | ⭐⭐⭐ 좋음 | ⭐⭐⭐⭐ 우수 |
| **학습 곡선** | ⭐⭐⭐⭐ 쉬움 | ⭐⭐⭐ 보통 | ⭐⭐ 어려움 |
| **추가 의존성** | ❌ 없음 | ✅ pyyaml | ⚠️ 선택적 |

---

## 🎯 추천 방안

### 🏆 **방안 3: 하이브리드** (환경변수 + 파일 + 코드)

#### 선정 이유

1. **유연성**: 모든 사용 케이스 커버
   - 개인 개발자: 파일로 설정
   - DevOps: 환경변수로 관리
   - 테스트: 코드에서 직접 지정

2. **하위 호환성**: 기존 `json_folder` 파라미터 그대로 유지

3. **점진적 전환**: 기존 코드 변경 없이 새 기능 추가

4. **표준 준수**: 12-Factor App + 일반적인 Python 패턴

#### 구현 단계

**Phase 1: Config 모듈 추가 (하위 호환)**
```python
# easygoogle/config.py 추가
# GoogleBaseManager 내부적으로만 사용
# 외부 API 변경 없음
```

**Phase 2: 문서화**
```markdown
# 설정 방법 가이드 작성
# 예제 설정 파일 제공
```

**Phase 3: labs_modules 의존성 제거**
```python
# 조건부 import 제거
# config 시스템으로 완전 전환
```

---

## 🚀 구현 예시

### 최소 변경 구현

```python
# easygoogle/config.py (NEW)
import os

class Config:
    """설정 관리"""
    
    @staticmethod
    def get_json_folder(override=None):
        return override or os.getenv('GS_UTILS_JSON_FOLDER', '.secret')
    
    @staticmethod
    def get_delegate_email(override=None):
        return override or os.getenv('GS_UTILS_DELEGATE_EMAIL')
    
    @staticmethod
    def get_discord_webhook():
        return os.getenv('GS_UTILS_DISCORD_WEBHOOK')

config = Config()
```

```python
# easygoogle/google/google_client_manager.py (MODIFIED)
from easygoogle.config import config

class GoogleBaseManager:
    def __init__(self, service_name, version, scope, 
                 attempt_retry=3, 
                 json_folder=None,
                 delegate_email=None):  # NEW parameter
        
        # Config 시스템 사용 (우선순위: 파라미터 > 환경변수 > 기본값)
        json_folder = config.get_json_folder(json_folder)
        self.delegate_email = config.get_delegate_email(delegate_email)
        
        # ... 기존 코드
```

### 하위 호환성

```python
# 기존 코드 그대로 작동 ✅
manager = GoogleDriveManager()

# 새로운 방법도 지원 ✅
os.environ['GS_UTILS_JSON_FOLDER'] = '/custom/path'
manager = GoogleDriveManager()

# 직접 지정도 여전히 작동 ✅
manager = GoogleDriveManager(json_folder='/another/path')
```

---

## 📝 마이그레이션 가이드

### 사용자 관점

#### Before (labs_modules 사용)
```python
# labs_modules/secret_key.py
DELEGATE_EMAIL = "user@domain.com"
WEBHOOK_URL_DISCORD = "https://..."
```

#### After (easygoogle config)

**방법 1: 환경변수**
```bash
export GS_UTILS_DELEGATE_EMAIL="user@domain.com"
export GS_UTILS_DISCORD_WEBHOOK="https://..."
```

**방법 2: 설정 파일**
```yaml
# .easygoogle_config.yaml
google:
  delegate_email: "user@domain.com"
notifications:
  discord_webhook: "https://..."
```

**방법 3: 코드에서**
```python
from easygoogle import GoogleDriveManager

manager = GoogleDriveManager(
    delegate_email="user@domain.com"
)
```

### 개발자 관점 (패키지 내부)

1. `easygoogle/config.py` 생성
2. `GoogleBaseManager.__init__()` 수정
3. `retry_on_error` 데코레이터 수정
4. 테스트 추가
5. 문서 업데이트

---

## 🔒 보안 고려사항

### ✅ 좋은 예

```bash
# 환경변수 (Git에 커밋되지 않음)
export GS_UTILS_DISCORD_WEBHOOK="https://..."
```

```yaml
# .easygoogle_config.yaml (gitignore에 추가)
notifications:
  discord_webhook: "https://..."
```

### ❌ 나쁜 예

```python
# 코드에 직접 하드코딩 (보안 위험!)
manager = GoogleDriveManager(
    delegate_email="user@domain.com"  # ⚠️ 코드에 노출
)
```

### .gitignore 추가

```gitignore
# easygoogle config
.easygoogle_config.yaml
.easygoogle_config.yml
.easygoogle_config.json

# Environment files
.env
.env.local
```

---

## 📚 참고 자료

- [The Twelve-Factor App - Config](https://12factor.net/config)
- [Python dotenv](https://github.com/theskumar/python-dotenv)
- [dynaconf](https://www.dynaconf.com/)
- [python-decouple](https://github.com/henriquebastos/python-decouple)

---

## ✅ 다음 단계

### 즉시 실행 가능
1. ✅ 설계 리뷰 및 피드백
2. ⏭️ 구현 승인 시 개발 시작

### 구현 후
1. Config 모듈 구현
2. GoogleBaseManager 수정
3. 테스트 추가
4. 문서 작성
5. PR 생성

---

**질문사항**:
1. 어떤 방안을 선호하시나요? (환경변수 / 파일 / 하이브리드)
2. 추가로 관리하고 싶은 설정이 있나요?
3. 기존 `labs_modules` 의존성을 완전히 제거해도 될까요?

---

**작성자**: Cursor Cloud Agent  
**날짜**: 2026-05-01
