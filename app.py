import requests
import os
from urllib.parse import urlparse

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
        response = requests.get(url, stream=True)

        # Check if the request was successful
        if response.status_code == 200:
            # Save the image to the specified path
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"Image successfully saved to {save_path}")
            return True
        else:
            print(f"Failed to download image. Status code: {response.status_code}")
            return False

    except Exception as e:
        print(f"Error downloading image: {str(e)}")
        return False

# Example usage
if __name__ == "__main__":
    # Sample PNG image URL
    image_url = "https://cdn.prod.website-files.com/668026bd6ba918352b4b09d2/6687d1c2e1923ee490c98a8c_63bd4fbe30300e7af5468cf2_Sq7gKtXNKFSNqV24KPWKTsF2GujiCfqnu-mWhFjGBUk-p-800.png"
    download_image(image_url)
