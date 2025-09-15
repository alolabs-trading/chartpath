import requests
import os
from urllib.parse import urlparse
import time

def download_image(url, save_folder="/chart"):
    try:
        # Create the chart folder if it doesn't exist
        os.makedirs(save_folder, exist_ok=True)
        
        # Get the filename from the URL
        filename = os.path.basename(urlparse(url).path)
        if not filename.lower().endswith('.png'):
            filename += '.png'
            
        # Full path for saving the file
        save_path = os.path.join(save_folder, filename)
        
        # Download the image
        response = requests.get(url, stream=True, timeout=10)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Save the image to the specified path
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"Image successfully saved to {save_path}")
            
            # List contents of the chart folder
            print(f"Contents of {save_folder}:")
            for item in os.listdir(save_folder):
                print(f"- {item}")
            return True
        else:
            print(f"Failed to download image. Status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error downloading image: {str(e)}")
        return False

if __name__ == "__main__":
    # Use a real PNG image URL (public domain image from Unsplash)
    image_url = "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?fm=png"
    download_image(image_url)
    print("Script completed, keeping process alive...")
    while True:
        time.sleep(60)  # Sleep for 60 seconds to keep the process running
