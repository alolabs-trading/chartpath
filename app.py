from flask import Flask, send_from_directory, jsonify
import os
import requests
from urllib.parse import urlparse

app = Flask(__name__)

# Create chart directory if it doesn't exist
os.makedirs('/chart', exist_ok=True)

@app.route('/')
def home():
    return jsonify({
        "message": "Image download service is running",
        "endpoints": {
            "download_image": "POST /download with {'url': 'image_url'}",
            "serve_image": "GET /chart/filename.png"
        }
    })

@app.route('/download', methods=['POST'])
def download_image():
    try:
        # Get URL from request JSON
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({"error": "Missing 'url' in request body"}), 400
        
        url = data['url']
        
        # Get the filename from the URL
        filename = os.path.basename(urlparse(url).path)
        if not filename.lower().endswith('.png'):
            filename += '.png'
            
        # Full path for saving the file
        save_path = os.path.join('/chart', filename)
        
        # Download the image
        response = requests.get(url, stream=True, timeout=10)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Save the image to the specified path
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            
            return jsonify({
                "message": "Image successfully downloaded",
                "filename": filename,
                "serve_url": f"/chart/{filename}"
            }), 200
        else:
            return jsonify({
                "error": f"Failed to download image. Status code: {response.status_code}"
            }), 400
            
    except Exception as e:
        return jsonify({
            "error": f"Error downloading image: {str(e)}"
        }), 500

@app.route('/chart/<path:filename>')
def serve_image(filename):
    return send_from_directory('/chart', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
