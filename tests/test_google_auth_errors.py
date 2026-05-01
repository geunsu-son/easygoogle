"""Tests for Google API authentication error handling"""
import pytest
import os
import tempfile
import shutil


def test_google_manager_no_json_folder():
    """Test error when .secret folder doesn't exist"""
    from gs_utils import GoogleDriveManager
    
    # This should raise FileNotFoundError with helpful message
    with pytest.raises(FileNotFoundError) as exc_info:
        manager = GoogleDriveManager()
    
    error_msg = str(exc_info.value)
    
    # Check that error message contains helpful information
    assert "Google API 인증 키 폴더를 찾을 수 없습니다" in error_msg
    assert ".secret" in error_msg
    assert "해결 방법" in error_msg
    assert "mkdir" in error_msg
    assert "Google Cloud Console" in error_msg


def test_google_manager_empty_json_folder():
    """Test error when folder exists but has no JSON files"""
    from gs_utils import GoogleDriveManager
    
    # Create temporary empty folder
    with tempfile.TemporaryDirectory() as temp_dir:
        with pytest.raises(FileNotFoundError) as exc_info:
            manager = GoogleDriveManager(json_folder=temp_dir)
        
        error_msg = str(exc_info.value)
        
        # Check that error message contains helpful information
        assert "JSON 키 파일을 찾을 수 없습니다" in error_msg
        assert temp_dir in error_msg
        assert "해결 방법" in error_msg
        assert ".json 확장자" in error_msg
        assert "서비스 계정 키 발급" in error_msg


def test_google_manager_invalid_json():
    """Test error when JSON file is invalid"""
    from gs_utils import GoogleSheetManager
    
    # Create temporary folder with invalid JSON
    with tempfile.TemporaryDirectory() as temp_dir:
        invalid_json_path = os.path.join(temp_dir, "invalid.json")
        with open(invalid_json_path, 'w') as f:
            f.write('{"invalid": "json"}')
        
        # Should raise RuntimeError when trying to initialize
        with pytest.raises(RuntimeError) as exc_info:
            manager = GoogleSheetManager(json_folder=temp_dir)
        
        error_msg = str(exc_info.value)
        assert "서비스 계정 초기화 실패" in error_msg


def test_google_manager_custom_folder():
    """Test that custom json_folder parameter works"""
    from gs_utils import GoogleDriveManager
    
    custom_path = "/custom/path/to/keys"
    
    # Should raise error about folder not existing
    with pytest.raises(FileNotFoundError) as exc_info:
        manager = GoogleDriveManager(json_folder=custom_path)
    
    error_msg = str(exc_info.value)
    assert custom_path in error_msg


def test_error_message_format_folder_not_found():
    """Test that error message for folder not found is well formatted"""
    from gs_utils import GoogleBaseManager
    
    # Create a temporary instance to access the method
    class TestManager(GoogleBaseManager):
        def __init__(self):
            pass  # Don't call parent __init__
    
    manager = TestManager()
    error_msg = manager._format_json_folder_not_found_error("/test/path")
    
    # Check message structure
    assert "╔" in error_msg  # Has box drawing
    assert "╚" in error_msg
    assert "/test/path" in error_msg
    assert "📂" in error_msg  # Has emoji icons
    assert "✅" in error_msg
    assert "❌" in error_msg
    assert "mkdir" in error_msg
    assert "https://console.cloud.google.com" in error_msg


def test_error_message_format_no_json_files():
    """Test that error message for no JSON files is well formatted"""
    from gs_utils import GoogleBaseManager
    
    # Create a temporary instance to access the method
    class TestManager(GoogleBaseManager):
        def __init__(self):
            pass  # Don't call parent __init__
    
    manager = TestManager()
    error_msg = manager._format_no_json_files_error("/test/path")
    
    # Check message structure
    assert "╔" in error_msg  # Has box drawing
    assert "╚" in error_msg
    assert "/test/path" in error_msg
    assert "📂" in error_msg  # Has emoji icons
    assert "✅" in error_msg
    assert "❌" in error_msg
    assert ".json 확장자" in error_msg
    assert "서비스 계정" in error_msg
    assert "https://console.cloud.google.com" in error_msg
