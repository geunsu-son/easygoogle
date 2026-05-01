"""
EasyGoogle - Google Drive Example

This example demonstrates how to use the Drive manager for common operations.
"""
import sys
import os

# Add parent directory to path for local development
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from easygoogle import Drive

# Initialize Drive manager
# Credentials are loaded from:
# 1. json_folder parameter (if provided)
# 2. GS_UTILS_JSON_FOLDER environment variable
# 3. .easygoogle_config.yaml file
# 4. Default: .secret/ folder
drive = Drive()

# Example 1: List files in a folder
def list_files_example():
    """List all files in a specific folder"""
    folder_id = "your-folder-id-here"
    files = drive.list_files(folder_id=folder_id)
    
    print("Files in folder:")
    for file in files:
        print(f"  - {file['name']} (ID: {file['id']})")


# Example 2: Clone a file
def clone_file_example():
    """Create a copy of an existing file"""
    original_file_id = "your-file-id-here"
    new_title = "Copy of My Document"
    
    new_file_id = drive.clone_file(
        file_id=original_file_id,
        new_title=new_title
    )
    
    print(f"✅ File cloned successfully!")
    print(f"   New file ID: {new_file_id}")


# Example 3: Create a folder
def create_folder_example():
    """Create a new folder"""
    folder_name = "My New Folder"
    parent_folder_id = "parent-folder-id-here"  # Optional
    
    folder_id = drive.create_folder(
        folder_name=folder_name,
        parent_folder_id=parent_folder_id
    )
    
    print(f"✅ Folder created!")
    print(f"   Folder ID: {folder_id}")


# Example 4: Upload a file
def upload_file_example():
    """Upload a local file to Google Drive"""
    file_path = "path/to/local/file.txt"
    parent_folder_id = "target-folder-id-here"
    
    file_id = drive.upload_file(
        file_path=file_path,
        parent_folder_id=parent_folder_id
    )
    
    print(f"✅ File uploaded!")
    print(f"   File ID: {file_id}")


# Example 5: Delete a file
def delete_file_example():
    """Delete a file from Google Drive"""
    file_id = "file-id-to-delete"
    
    drive.delete_file(file_id=file_id)
    print(f"✅ File deleted!")


if __name__ == "__main__":
    print("🔷 EasyGoogle - Drive Examples\n")
    
    # Uncomment the examples you want to run
    # list_files_example()
    # clone_file_example()
    # create_folder_example()
    # upload_file_example()
    # delete_file_example()
    
    print("\n💡 Tip: Edit the file IDs in the code to test with your own files!")
