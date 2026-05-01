"""
EasyGoogle - Google Sheets Example

This example demonstrates how to use the Sheets manager for common operations.
"""
import sys
import os

# Add parent directory to path for local development
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from easygoogle import Sheets
from easygoogle import extract_spreadsheet_id

# Initialize Sheets manager
# Credentials are loaded from:
# 1. json_folder parameter (if provided)
# 2. GS_UTILS_JSON_FOLDER environment variable
# 3. .easygoogle_config.yaml file
# 4. Default: .secret/ folder
sheets = Sheets()

# Example spreadsheet URL
spreadsheet_url = "https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit"


# Example 1: Read data from a sheet
def read_sheet_example():
    """Read data from a Google Sheet into a pandas DataFrame"""
    sheet_name = "Sheet1"
    
    df = sheets.get_dataframe_from_sheet(
        spreadsheet_url=spreadsheet_url,
        sheet_name=sheet_name
    )
    
    print(f"✅ Data loaded from '{sheet_name}':")
    print(df.head())
    return df


# Example 2: Write data to a sheet
def write_sheet_example():
    """Write a pandas DataFrame to a Google Sheet"""
    # Create sample data
    data = pd.DataFrame({
        "Name": ["Alice", "Bob", "Charlie"],
        "Age": [25, 30, 35],
        "City": ["Seoul", "Busan", "Incheon"]
    })
    
    sheet_name = "NewSheet"
    
    sheets.clear_and_set_worksheet(
        spreadsheet_url=spreadsheet_url,
        sheet_name=sheet_name,
        df=data
    )
    
    print(f"✅ Data written to '{sheet_name}':")
    print(data)


# Example 3: Get sheet names
def list_sheets_example():
    """List all sheet names in a spreadsheet"""
    sheet_names = sheets.get_sheet_name_list(spreadsheet_url)
    
    print("📋 Sheets in this spreadsheet:")
    for name in sheet_names:
        print(f"  - {name}")


# Example 4: Get sheet name-ID mapping
def get_sheet_ids_example():
    """Get a dictionary mapping sheet names to their IDs"""
    name_id_dict = sheets.get_sheet_name_id_dict(spreadsheet_url)
    
    print("📋 Sheet Names and IDs:")
    for name, sheet_id in name_id_dict.items():
        print(f"  {name}: {sheet_id}")


# Example 5: Copy sheet formatting
def copy_format_example():
    """Copy formatting from one sheet to others"""
    source_sheet = "Template"
    target_sheets = ["Report1", "Report2", "Report3"]
    
    sheets.copy_sheet_format(
        spreadsheet_url=spreadsheet_url,
        source_sheet_name=source_sheet,
        target_sheet_names=target_sheets
    )
    
    print(f"✅ Formatting copied from '{source_sheet}' to:")
    for sheet in target_sheets:
        print(f"  - {sheet}")


# Example 6: Extract spreadsheet ID from URL
def extract_id_example():
    """Extract the spreadsheet ID from a URL"""
    url = "https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit"
    
    spreadsheet_id = extract_spreadsheet_id(url)
    print(f"📋 Spreadsheet ID: {spreadsheet_id}")


# Example 7: Complete data pipeline
def data_pipeline_example():
    """Complete example: Read, process, and write back"""
    # Read data
    df = sheets.get_dataframe_from_sheet(
        spreadsheet_url=spreadsheet_url,
        sheet_name="RawData"
    )
    
    # Process data (example: filter and aggregate)
    df_processed = df[df['status'] == 'active'].groupby('category').sum()
    
    # Write results
    sheets.clear_and_set_worksheet(
        spreadsheet_url=spreadsheet_url,
        sheet_name="ProcessedData",
        df=df_processed
    )
    
    print("✅ Data pipeline completed!")
    print(f"   Input rows: {len(df)}")
    print(f"   Output rows: {len(df_processed)}")


if __name__ == "__main__":
    print("🔷 EasyGoogle - Sheets Examples\n")
    
    # Uncomment the examples you want to run
    # read_sheet_example()
    # write_sheet_example()
    # list_sheets_example()
    # get_sheet_ids_example()
    # copy_format_example()
    # extract_id_example()
    # data_pipeline_example()
    
    print("\n💡 Tip: Update the spreadsheet_url variable with your own Google Sheet URL!")
