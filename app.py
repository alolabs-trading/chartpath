from flask import Flask, send_from_directory, request, jsonify, redirect
import os
import requests
from urllib.parse import urlparse, quote
import uuid

app = Flask(__name__)

# Create chart directory if it doesn't exist
CHART_FOLDER = '/chart'
os.makedirs(CHART_FOLDER, exist_ok=True)

@app.route('/')
def home():
    # List all available images
    images = []
    if os.path.exists(CHART_FOLDER):
        images = [f for f in os.listdir(CHART_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))]
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Image Downloader & Viewer</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
            .form {{ margin-bottom: 30px; padding: 20px; background: #f5f5f5; border-radius: 8px; }}
            input[type="url"] {{ width: 70%; padding: 8px; margin-right: 10px; }}
            button {{ padding: 8px 16px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }}
            .images {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 20px; }}
            .image-card {{ border: 1px solid #ddd; padding: 10px; border-radius: 8px; text-align: center; }}
            .image-card img {{ max-width: 100%; height: 150px; object-fit: cover; }}
        </style>
    </head>
    <body>
        <h1>Image Downloader & Viewer</h1>
        
        <div class="form">
            <h3>Download New Image</h3>
            <form action="/download" method="post">
                <input type="url" name="image_url" placeholder="Enter image URL" required>
                <button type="submit">Download</button>
            </form>
        </div>

        <h3>Available Images ({len(images)})</h3>
        <div class="images">
    """
    
    if images:
        for image in images:
            html += f"""
            <div class="image-card">
                <img src="/chart/{quote(image)}" alt="{image}">
                <p>{image}</p>
                <a href="/chart/{quote(image)}" target="_blank">View Full Size</a>
            </div>
            """
    else:
        html += "<p>No images downloaded yet. Use the form above to download an image.</p>"
    
    html += """
        </div>
    </body>
    </html>
    """
    
    return html

@app.route('/download', methods=['POST'])
def download_image():
    try:
        image_url = request.form.get('image_url')
        if not image_url:
            return jsonify({"error": "Missing image URL"}), 400
        
        # Generate a unique filename
        parsed_url = urlparse(image_url)
        original_filename = os.path.basename(parsed_url.path)
        
        if not original_filename:
            # If no filename in URL, create one with UUID
            file_extension = '.png'  # default extension
            original_filename = f"image_{uuid.uuid4().hex[:8]}{file_extension}"
        else:
            # Ensure the file has an extension
            if '.' not in original_filename:
                original_filename += '.png'
        
        # Clean filename (remove query parameters if any)
        filename = original_filename.split('?')[0]
        save_path = os.path.join(CHART_FOLDER, filename)
        
        # Download the image
        response = requests.get(image_url, stream=True, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Check if the request was successful
        if response.status_code == 200:
            # Check if content is actually an image
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                return jsonify({"error": "URL does not point to an image"}), 400
            
            # Save the image
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
            
            return redirect('/')
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
    return send_from_directory(CHART_FOLDER, filename)

@app.route('/list')
def list_images():
    """API endpoint to list all downloaded images"""
    images = []
    if os.path.exists(CHART_FOLDER):
        images = [f for f in os.listdir(CHART_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))]
    
    return jsonify({
        "images": images,
        "count": len(images)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
