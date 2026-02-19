"""
Batch download example for pybaiduphoto.

This example demonstrates how to batch download photos.
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


def example_batch_download_individual():
    """Example: Download photos individually."""
    download_dir = "./downloads"
    os.makedirs(download_dir, exist_ok=True)
    
    print("Getting photos...")
    items = api.get_self_All(typeName='Item')
    
    print(f"Found {len(items)} photos")
    print(f"Downloading to: {download_dir}")
    
    for i, item in enumerate(items[:10]):  # Download first 10 as example
        try:
            print(f"  [{i+1}/{min(10, len(items))}] Downloading: {item}")
            item.download(DirPath=download_dir)
        except Exception as e:
            print(f"  Error: {e}")


def example_batch_download_zip():
    """Example: Download photos as a ZIP file."""
    print("Getting photos...")
    items = api.get_self_All(typeName='Item')
    
    if not items:
        print("No photos found")
        return
    
    # Take first 20 photos for the zip
    items_to_download = items[:20]
    
    print(f"Creating download link for {len(items_to_download)} photos...")
    zip_name = "my_photos.zip"
    
    download_url = api.get_batchDownloadLink(items=items_to_download, zipname=zip_name)
    
    print(f"\nDownload URL: {download_url}")
    print("\nCopy the URL to your browser to download the ZIP file.")
    print("Note: The link may expire after some time.")


def example_download_album():
    """Example: Download all photos from an album."""
    download_dir = "./album_downloads"
    os.makedirs(download_dir, exist_ok=True)
    
    # Get first album
    albums = api.get_self_1page(typeName='Album')
    if not albums['items']:
        print("No albums found")
        return
    
    album = albums['items'][0]
    print(f"Downloading from album: {album.getName()}")
    
    # Get all photos in the album
    photos = album.get_sub_All()
    print(f"Found {len(photos)} photos in album")
    
    for i, photo in enumerate(photos):
        try:
            print(f"  [{i+1}/{len(photos)}] Downloading...")
            photo.download(DirPath=download_dir)
        except Exception as e:
            print(f"  Error: {e}")


if __name__ == '__main__':
    print("=" * 60)
    print("pybaiduphoto Batch Download Examples")
    print("=" * 60)
    
    # Uncomment the example you want to run
    # example_batch_download_individual()
    # example_batch_download_zip()
    # example_download_album()
