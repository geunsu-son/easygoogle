"""
gs_utils - Simple and powerful Python wrapper for Google APIs

This library provides easy-to-use interfaces for Google Drive and Google Sheets,
with simplified authentication and friendly error messages.

Quick Start:
    >>> from gs_utils import GoogleDriveManager, GoogleSheetManager
    >>> 
    >>> # Initialize managers
    >>> drive = GoogleDriveManager()
    >>> sheets = GoogleSheetManager()
    >>> 
    >>> # Use them!
    >>> drive.clone_file(file_id='...', new_title='Copy')
    >>> df = sheets.get_dataframe_from_sheet(spreadsheet_url='...')

Documentation: https://github.com/geunsu-son/gs_utils
"""

from .__version__ import __version__
from .google import (
    GoogleBaseManager, 
    GoogleDriveManager, 
    GoogleSheetManager, 
    retry_on_error,
    extract_spreadsheet_id,
    convert_sheetid_to_url,
    convert_to_number,
    extract_googledrive_id,
    convert_googledrive_id_to_url
)

__all__ = [
    '__version__',
    'GoogleBaseManager',
    'GoogleDriveManager',
    'GoogleSheetManager',
    'retry_on_error',
    'extract_spreadsheet_id',
    'convert_sheetid_to_url',
    'convert_to_number',
    'extract_googledrive_id',
    'convert_googledrive_id_to_url'
]
