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


def test_discord_webhook():
    """Discord webhook 설정"""
    from gs_utils.config import config
    
    os.environ['GS_UTILS_DISCORD_WEBHOOK'] = 'https://discord.webhook'
    config.reload()
    
    assert config.get_discord_webhook() == 'https://discord.webhook'
    
    # Clean up
    os.environ.pop('GS_UTILS_DISCORD_WEBHOOK', None)


def test_config_file_yaml():
    """YAML 설정 파일 로드"""
    from gs_utils.config import Config
    
    # pyyaml이 없으면 스킵
    try:
        import yaml
    except ImportError:
        pytest.skip("pyyaml not installed")
    
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
        
        # 환경변수 제거
        os.environ.pop('GS_UTILS_JSON_FOLDER', None)
        os.environ.pop('GS_UTILS_DELEGATE_EMAIL', None)
        os.environ.pop('GS_UTILS_MAX_RETRIES', None)
        os.environ.pop('GS_UTILS_DISCORD_WEBHOOK', None)
        
        # 새 Config 인스턴스로 reload
        test_config = Config()
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
    
    # pyyaml이 없으면 환경변수 테스트만
    try:
        import yaml
        has_yaml = True
    except ImportError:
        has_yaml = False
    
    if has_yaml:
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
    else:
        # pyyaml 없이 환경변수만 테스트
        os.environ['GS_UTILS_JSON_FOLDER'] = '/env/path'
        
        test_config = Config()
        test_config.reload()
        
        # override가 환경변수보다 우선
        assert test_config.get_json_folder('/override/path') == '/override/path'
        
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
