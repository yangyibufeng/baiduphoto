"""
Upload example for pybaiduphoto.

This example demonstrates how to upload files to Baidu Photo.
"""

from pybaiduphoto import API
import os

# Initialize API with cookies
cookies = {
    'BAIDUID': 'YOUR_BAIDUID_HERE',
    'STOKEN': 'YOUR_STOKEN_HERE',
    'BDUSS_BFESS': 'YOUR_BDUSS_HERE',
}
api = API(cookies=cookies)


def example_upload_single_file():
    """Example: Upload a single file."""
    file_path = "test_image.jpg"
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        print("Please create a test image file named 'test_image.jpg'")
        return
    
    print(f"Uploading file: {file_path}")
    result = api.upload_1file(filePath=file_path)
    print(f"Upload result: {result}")


def example_upload_to_album():
    """Example: Upload a file to a specific album."""
    file_path = "test_image.jpg"
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    
    # Get or create an album
    albums = api.get_self_1page(typeName='Album')
    if albums['items']:
        album = albums['items'][0]
    else:
        album = api.createNewAlbum(Name="Upload Test Album")
    
    print(f"Uploading to album: {album.getName()}")
    result = api.upload_1file(filePath=file_path, album=album)
    print(f"Upload result: {result}")


def example_upload_multiple_files():
    """Example: Upload multiple files."""
    files_to_upload = [
        "image1.jpg",
        "image2.jpg",
        "image3.jpg",
    ]
    
    for file_path in files_to_upload:
        if os.path.exists(file_path):
            print(f"Uploading: {file_path}")
            try:
                api.upload_1file(filePath=file_path)
                print(f"  Success!")
            except Exception as e:
                print(f"  Error: {e}")
        else:
            print(f"  File not found: {file_path}")


if __name__ == '__main__':
    print("=" * 60)
    print("pybaiduphoto Upload Examples")
    print("=" * 60)
    
    # Uncomment the example you want to run
    # example_upload_single_file()
    # example_upload_to_album()
    # example_upload_multiple_files()