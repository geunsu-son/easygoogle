"""
EasyGoogle - Simple and powerful Python wrapper for Google APIs

This library provides easy-to-use interfaces for Google Drive and Google Sheets,
with simplified authentication and friendly error messages.

Quick Start:
    >>> from easygoogle import Drive, Sheets
    >>> 
    >>> # Initialize managers
    >>> drive = Drive()
    >>> sheets = Sheets()
    >>> 
    >>> # Use them!
    >>> drive.clone_file(file_id='...', new_title='Copy')
    >>> df = sheets.get_dataframe_from_sheet(spreadsheet_url='...')

Documentation: https://github.com/geunsu-son/easygoogle
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

# Shorter aliases for convenience
Drive = GoogleDriveManager
Sheets = GoogleSheetManager

__all__ = [
    '__version__',
    # Main classes
    'GoogleBaseManager',
    'GoogleDriveManager',
    'GoogleSheetManager',
    # Convenient aliases
    'Drive',
    'Sheets',
    # Utilities
    'retry_on_error',
    'extract_spreadsheet_id',
    'convert_sheetid_to_url',
    'convert_to_number',
    'extract_googledrive_id',
    'convert_googledrive_id_to_url'
]
