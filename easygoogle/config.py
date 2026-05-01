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
