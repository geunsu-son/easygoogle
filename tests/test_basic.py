"""Basic tests for gs_utils package"""
import pytest


def test_import_package():
    """Test that gs_utils can be imported"""
    import gs_utils
    assert gs_utils is not None


def test_version():
    """Test that version is defined"""
    import gs_utils
    assert hasattr(gs_utils, '__version__')
    assert isinstance(gs_utils.__version__, str)
    assert len(gs_utils.__version__) > 0


def test_import_decorators():
    """Test that decorators can be imported"""
    from gs_utils import time_tracker
    assert time_tracker is not None


def test_import_google_managers():
    """Test that Google managers can be imported"""
    from gs_utils import (
        GoogleBaseManager,
        GoogleDriveManager,
        GoogleSheetManager
    )
    assert GoogleBaseManager is not None
    assert GoogleDriveManager is not None
    assert GoogleSheetManager is not None


def test_import_utility_functions():
    """Test that utility functions can be imported"""
    from gs_utils import (
        retry_on_error,
        extract_spreadsheet_id,
        convert_sheetid_to_url,
        convert_to_number,
        extract_googledrive_id,
        convert_googledrive_id_to_url
    )
    assert retry_on_error is not None
    assert extract_spreadsheet_id is not None
    assert convert_sheetid_to_url is not None
    assert convert_to_number is not None
    assert extract_googledrive_id is not None
    assert convert_googledrive_id_to_url is not None


def test_time_tracker_decorator():
    """Test time_tracker decorator works"""
    from gs_utils import time_tracker
    import time
    
    @time_tracker
    def sample_function():
        time.sleep(0.1)
        return "completed"
    
    result = sample_function()
    assert result == "completed"


def test_extract_spreadsheet_id():
    """Test extract_spreadsheet_id function"""
    from gs_utils import extract_spreadsheet_id
    
    # Test with full URL
    url = "https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit"
    result = extract_spreadsheet_id(url)
    assert result == "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
    
    # Test with ID only
    file_id = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
    result = extract_spreadsheet_id(file_id)
    assert result == file_id


def test_convert_sheetid_to_url():
    """Test convert_sheetid_to_url function"""
    from gs_utils import convert_sheetid_to_url
    
    file_id = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
    result = convert_sheetid_to_url(file_id)
    expected = "https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit"
    assert result == expected


def test_convert_to_number():
    """Test convert_to_number function"""
    from gs_utils import convert_to_number
    
    # Test integer string
    assert convert_to_number("123") == 123
    
    # Test float string
    assert convert_to_number("123.45") == 123.45
    
    # Test non-numeric string
    assert convert_to_number("abc") == "abc"
    
    # Test empty string
    assert convert_to_number("") == ""


def test_extract_googledrive_id():
    """Test extract_googledrive_id function"""
    from gs_utils import extract_googledrive_id
    
    # Test with full URL
    url = "https://drive.google.com/file/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/view"
    result = extract_googledrive_id(url)
    assert result == "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
    
    # Test with ID only
    file_id = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
    result = extract_googledrive_id(file_id)
    assert result == file_id


def test_convert_googledrive_id_to_url():
    """Test convert_googledrive_id_to_url function"""
    from gs_utils import convert_googledrive_id_to_url
    
    file_id = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
    result = convert_googledrive_id_to_url(file_id)
    expected = "https://drive.google.com/file/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/view"
    assert result == expected
