"""Google API utility functions"""
import re


def extract_spreadsheet_id(spreadsheet_url):
    """
    Google Sheets URL에서 스프레드시트 ID를 추출합니다.
    
    Args:
        spreadsheet_url (str): Google Sheets URL 또는 ID
        
    Returns:
        str: 스프레드시트 ID
        
    Example:
        >>> url = "https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit"
        >>> extract_spreadsheet_id(url)
        '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
    """
    if 'docs.google.com/spreadsheets' in spreadsheet_url:
        match = re.search(r'/d/([a-zA-Z0-9-_]+)', spreadsheet_url)
        if match:
            return match.group(1)
    return spreadsheet_url


def convert_sheetid_to_url(spreadsheet_id):
    """
    스프레드시트 ID를 Google Sheets URL로 변환합니다.
    
    Args:
        spreadsheet_id (str): 스프레드시트 ID
        
    Returns:
        str: Google Sheets URL
        
    Example:
        >>> convert_sheetid_to_url("1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms")
        'https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit'
    """
    return f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"


def extract_googledrive_id(drive_url):
    """
    Google Drive URL에서 파일 ID를 추출합니다.
    
    Args:
        drive_url (str): Google Drive URL 또는 ID
        
    Returns:
        str: 파일 ID
        
    Example:
        >>> url = "https://drive.google.com/file/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/view"
        >>> extract_googledrive_id(url)
        '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
    """
    if 'drive.google.com' in drive_url:
        match = re.search(r'/d/([a-zA-Z0-9-_]+)', drive_url)
        if match:
            return match.group(1)
        match = re.search(r'id=([a-zA-Z0-9-_]+)', drive_url)
        if match:
            return match.group(1)
    return drive_url


def convert_googledrive_id_to_url(file_id):
    """
    파일 ID를 Google Drive URL로 변환합니다.
    
    Args:
        file_id (str): 파일 ID
        
    Returns:
        str: Google Drive URL
        
    Example:
        >>> convert_googledrive_id_to_url("1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms")
        'https://drive.google.com/file/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/view'
    """
    return f"https://drive.google.com/file/d/{file_id}/view"


def convert_to_number(value):
    """
    문자열을 숫자로 변환합니다. 변환할 수 없으면 원본을 반환합니다.
    
    Args:
        value: 변환할 값
        
    Returns:
        int, float, or original value: 변환된 숫자 또는 원본 값
        
    Example:
        >>> convert_to_number("123")
        123
        >>> convert_to_number("123.45")
        123.45
        >>> convert_to_number("abc")
        'abc'
    """
    if isinstance(value, str):
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            return value
    return value
