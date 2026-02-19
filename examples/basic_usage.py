"""
Basic usage example for pybaiduphoto.

This example demonstrates how to:
1. Initialize the API with cookies
2. Get all photos/videos
3. Download photos
4. Create an album
5. Upload files to an album
"""

from pybaiduphoto import API

# Option 1: Use cookies from browser_cookie3
# import browser_cookie3
# api = API(cookies=browser_cookie3.chrome())

# Option 2: Provide cookies manually
cookies = {
    'BAIDUID': 'YOUR_BAIDUID_HERE',
    'STOKEN': 'YOUR_STOKEN_HERE',
    'BDUSS_BFESS': 'YOUR_BDUSS_HERE',
    # ... add other cookies as needed
}
api = API(cookies=cookies)


def example_get_all_photos():
    """Example: Get all photos/videos from your Baidu Photo account."""
    print("Getting all photos...")
    items = api.get_self_All(typeName='Item')
    print(f"Found {len(items)} items")
    
    # Display first 3 items
    for i, item in enumerate(items[:3]):
        print(f"  {i+1}. {item}")


def example_download_photos():
    """Example: Download photos to local directory."""
    import os
    
    # Create download directory
    download_dir = "./downloads"
    os.makedirs(download_dir, exist_ok=True)
    
    # Get first page of photos
    page = api.get_self_1page(typeName='Item')
    items = page['items']
    
    print(f"Downloading {len(items)} photos to {download_dir}...")
    for item in items[:5]:  # Download first 5 as example
        try:
            item.download(DirPath=download_dir)
            print(f"  Downloaded: {item}")
        except Exception as e:
            print(f"  Error downloading {item}: {e}")


def example_create_album():
    """Example: Create a new album."""
    album_name = "My Test Album"
    print(f"Creating album: {album_name}")
    
    album = api.createNewAlbum(Name=album_name)
    print(f"Created: {album}")
    print(f"  ID: {album.getID()}")
    print(f"  TID: {album._getTID()}")
    
    return album


def example_add_to_album(album):
    """Example: Add photos to an album."""
    # Get some photos
    page = api.get_self_1page(typeName='Item')
    items = page['items'][:3]  # Take first 3 photos
    
    print(f"Adding {len(items)} photos to album...")
    album.append(items)
    print(f"Added to album: {album.getName()}")


def example_album_operations(album):
    """Example: Perform album operations."""
    # Rename album
    new_name = "My Renamed Album"
    print(f"Renaming album to: {new_name}")
    album.rename(new_name)
    print(f"New name: {album.getName()}")
    
    # Set album notice
    notice = "This is a test album created by pybaiduphoto"
    print(f"Setting notice: {notice}")
    album.setNotice(notice)
    
    # Get photos in the album
    print("Getting photos in the album...")
    album_photos = album.get_sub_1page()
    print(f"Found {len(album_photos['items'])} photos")


def example_get_person_albums():
    """Example: Get all person albums (face recognition)."""
    print("Getting person albums...")
    persons = api.get_self_All(typeName='Person')
    print(f"Found {len(persons)} persons")
    
    for person in persons[:3]:
        print(f"  {person}")
        # Get photos for this person
        photos = person.get_sub_1page()
        print(f"    Photos: {len(photos['items'])}")


def example_get_location_albums():
    """Example: Get all location albums."""
    print("Getting location albums...")
    locations = api.get_self_All(typeName='Location')
    print(f"Found {len(locations)} locations")
    
    for location in locations[:3]:
        print(f"  {location}")


def example_search_albums():
    """Example: Search for albums by keyword."""
    keyword = "travel"
    print(f"Searching for albums with keyword: {keyword}")
    
    result = api.albumSearch(keyword=keyword, limit=10)
    albums = result['items']
    
    print(f"Found {len(albums)} albums")
    for album in albums:
        print(f"  {album}")


if __name__ == '__main__':
    print("=" * 60)
    print("pybaiduphoto Basic Usage Examples")
    print("=" * 60)
    
    # Run examples (comment out what you don't need)
    try:
        example_get_all_photos()
        print()
        
        # example_download_photos()
        # print()
        
        # album = example_create_album()
        # print()
        
        # example_add_to_album(album)
        # print()
        
        # example_album_operations(album)
        # print()
        
        # example_get_person_albums()
        # print()
        
        # example_get_location_albums()
        # print()
        
        # example_search_albums()
        
    except Exception as e:
        print(f"\nError: {e}")
        print("\nNote: Make sure you have provided valid cookies in the cookies dictionary.")
