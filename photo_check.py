from flask import Flask, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv
import logging
from PIL import Image
from PIL.ExifTags import TAGS
import io
import time
import hashlib
import numpy as np
from datetime import datetime
import base64
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuration ---
load_dotenv()

# Environment variables
API_URL = os.getenv("HUGGING_FACE_API_URL")
API_KEY = os.getenv("HUGGING_FACE_API_KEY")
FLASK_ENV = os.getenv("FLASK_ENV", "development")
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"

# Validate required environment variables
if not API_URL or not API_KEY:
    logger.error("HUGGING_FACE_API_URL and HUGGING_FACE_API_KEY must be set in .env file")
    raise ValueError("HUGGING_FACE_API_URL and HUGGING_FACE_API_KEY must be set in .env file")

if API_KEY == "hf_your_actual_api_key_here" or API_KEY == "hf_your_new_api_key_here" or API_KEY.startswith("hf_") and len(API_KEY) < 30:
    logger.warning("Please replace the placeholder with your actual Hugging Face API key")

# Flask app configuration
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# --- Helper Functions ---
def get_image_metadata(image_bytes):
    """
    Extract detailed metadata from image
    """
    image_data = {}
    try:
        # Open image from bytes
        img = Image.open(io.BytesIO(image_bytes))
        
        # Basic image info
        image_data["format"] = img.format
        image_data["mode"] = img.mode
        image_data["width"], image_data["height"] = img.size
        image_data["aspect_ratio"] = round(img.width / img.height, 2)
        image_data["file_size"] = f"{len(image_bytes) / 1024:.2f} KB"
        image_data["file_size_bytes"] = len(image_bytes)
        
        # Generate a unique hash for the image
        image_data["hash"] = hashlib.md5(image_bytes).hexdigest()
        image_data["sha256"] = hashlib.sha256(image_bytes).hexdigest()[:16]  # Truncated for UI
        
        # Create a base64 thumbnail for display
        thumbnail = img.copy()
        thumbnail.thumbnail((200, 200))
        buffered = io.BytesIO()
        if thumbnail.mode in ("RGBA", "LA"):
            background = Image.new(thumbnail.mode[:-1], thumbnail.size, (255, 255, 255))
            background.paste(thumbnail, mask=thumbnail.split()[-1])
            thumbnail = background
        
        thumbnail.save(buffered, format="JPEG", quality=70)
        image_data["thumbnail"] = f"data:image/jpeg;base64,{base64.b64encode(buffered.getvalue()).decode('utf-8')}"
        
        # Try to extract EXIF data if available
        exif_data = {}
        if hasattr(img, '_getexif') and img._getexif():
            exif = img._getexif()
            for tag_id, value in exif.items():
                tag = TAGS.get(tag_id, tag_id)
                # Skip binary data which can't be JSON serialized
                if isinstance(value, bytes):
                    value = f"Binary data ({len(value)} bytes)"
                exif_data[tag] = str(value)
            
            # Extract common EXIF fields into separate keys
            image_data["date_taken"] = exif_data.get("DateTimeOriginal", "Not available")
            
            # Try to parse date in standard format
            try:
                if image_data["date_taken"] != "Not available":
                    dt = datetime.strptime(image_data["date_taken"], "%Y:%m:%d %H:%M:%S")
                    image_data["date_taken_formatted"] = dt.strftime("%B %d, %Y at %H:%M:%S")
                    image_data["date_taken_unix"] = int(dt.timestamp())
            except Exception as e:
                logger.warning(f"Date parsing error: {str(e)}")
            
            # Camera info
            image_data["camera_make"] = exif_data.get('Make', 'Unknown')
            image_data["camera_model"] = exif_data.get('Model', 'Unknown')
            image_data["camera"] = f"{image_data['camera_make']} {image_data['camera_model']}".strip()
            
            # Lens info if available
            if 'LensModel' in exif_data:
                image_data["lens"] = exif_data.get('LensModel')
            
            # Exposure settings
            if 'ExposureTime' in exif_data:
                image_data["exposure"] = exif_data.get('ExposureTime')
                # Try to convert to fraction
                try:
                    parts = image_data["exposure"].split('/')
                    if len(parts) == 2:
                        num = float(parts[0])
                        denom = float(parts[1])
                        if num == 1:
                            image_data["exposure_formatted"] = f"1/{int(denom)}s"
                        else:
                            image_data["exposure_formatted"] = f"{num/denom:.2f}s"
                except:
                    image_data["exposure_formatted"] = image_data["exposure"]
            
            # Aperture
            if 'FNumber' in exif_data:
                image_data["aperture"] = f"f/{exif_data.get('FNumber')}"
            
            # ISO
            if 'ISOSpeedRatings' in exif_data:
                image_data["iso"] = exif_data.get('ISOSpeedRatings')
            
            # Focal Length
            if 'FocalLength' in exif_data:
                image_data["focal_length"] = f"{exif_data.get('FocalLength')}mm"
            
            # GPS data if available
            gps_info = {}
            if 'GPSInfo' in exif_data:
                try:
                    gps_raw = exif_data.get('GPSInfo')
                    if isinstance(gps_raw, dict):
                        for key, val in gps_raw.items():
                            gps_info[key] = str(val)
                    image_data["gps_data"] = gps_info
                    
                    # Try to extract coordinates for map display
                    if 'GPSLatitude' in gps_raw and 'GPSLongitude' in gps_raw:
                        # This would require parsing the coordinates which can be complex
                        image_data["has_location"] = True
                except Exception as e:
                    logger.warning(f"GPS parsing error: {str(e)}")
        
        # Add EXIF data to image data
        if exif_data:
            image_data["exif"] = exif_data
        
        # Color analysis
        try:
            if img.mode == 'RGB':
                # Resize for faster processing
                img_small = img.resize((50, 50))
                pixels = list(img_small.getdata())
                r_values = [p[0] for p in pixels]
                g_values = [p[1] for p in pixels]
                b_values = [p[2] for p in pixels]
                
                # Average color
                r_avg = sum(r_values) // len(pixels)
                g_avg = sum(g_values) // len(pixels)
                b_avg = sum(b_values) // len(pixels)
                image_data["avg_color"] = f"rgb({r_avg},{g_avg},{b_avg})"
                image_data["avg_color_hex"] = f"#{r_avg:02x}{g_avg:02x}{b_avg:02x}"
                
                # Color histogram data for visualization
                r_hist = np.histogram(r_values, bins=8, range=(0,256))[0].tolist()
                g_hist = np.histogram(g_values, bins=8, range=(0,256))[0].tolist()
                b_hist = np.histogram(b_values, bins=8, range=(0,256))[0].tolist()
                
                image_data["color_histogram"] = {
                    "r": r_hist,
                    "g": g_hist,
                    "b": b_hist
                }
                
                # Dominant colors (simplified k-means-like approach)
                pixels_array = np.array(pixels)
                # Sample pixels to speed up processing
                sampled_pixels = pixels_array[::10]
                
                # Simple clustering for dominant colors
                dominant_colors = []
                min_distance = 30  # Minimum distance between colors
                
                for pixel in sampled_pixels:
                    r, g, b = pixel
                    
                    # Skip very dark or very light pixels
                    if sum([r, g, b]) < 30 or sum([r, g, b]) > 730:
                        continue
                        
                    new_color = True
                    for color in dominant_colors:
                        cr, cg, cb = color
                        # Euclidean distance in RGB space
                        distance = np.sqrt((r - cr)**2 + (g - cg)**2 + (b - cb)**2)
                        if distance < min_distance:
                            new_color = False
                            break
                    
                    if new_color and len(dominant_colors) < 5:
                        dominant_colors.append((r, g, b))
                
                image_data["dominant_colors"] = []
                for color in dominant_colors:
                    r, g, b = color
                    hex_color = f"#{r:02x}{g:02x}{b:02x}"
                    image_data["dominant_colors"].append({
                        "rgb": f"rgb({r},{g},{b})",
                        "hex": hex_color
                    })
                
                # Brightness analysis
                brightness = sum([r_avg, g_avg, b_avg]) / 3
                brightness_percent = round((brightness / 255) * 100)
                if brightness_percent < 30:
                    brightness_category = "Dark"
                elif brightness_percent < 70:
                    brightness_category = "Medium"
                else:
                    brightness_category = "Bright"
                
                image_data["brightness"] = brightness_percent
                image_data["brightness_category"] = brightness_category
                
                # Contrast estimation (simplified)
                std_dev = np.std([r_values, g_values, b_values])
                contrast_percent = min(round((std_dev / 128) * 100), 100)
                image_data["contrast"] = contrast_percent
                
        except Exception as e:
            logger.warning(f"Color analysis failed: {str(e)}")
        
        # Add creation timestamp
        image_data["analyzed_at"] = datetime.now().isoformat()
        
        return image_data
        
    except Exception as e:
        logger.error(f"Error extracting image metadata: {str(e)}")
        return {"error": f"Could not extract metadata: {str(e)}"}

def query_huggingface_api(image_bytes):
    """
    Query the Hugging Face API with image data
    """
    try:
        # Use proper content-type for image data
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/octet-stream"
        }
        
        # Time the API request for performance metrics
        start_time = time.time()
        
        response = requests.post(
            API_URL, 
            headers=headers, 
            data=image_bytes,
            timeout=30
        )
        
        # Calculate request time
        request_time = time.time() - start_time
        
        logger.info(f"API Response Status: {response.status_code}")
        logger.info(f"API Response Headers: {dict(response.headers)}")
        logger.info(f"API Request Time: {request_time:.2f} seconds")
        
        # Log response text for debugging 400 errors
        if response.status_code == 400:
            logger.error(f"400 Error Response: {response.text}")
        
        # Add request time to response object
        response.request_time = request_time
        
        return response
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {str(e)}")
        raise

def process_api_response(response):
    """
    Process and validate the API response
    """
    # Check status code
    if response.status_code == 503:
        return {
            "error": "Model is currently loading. Please try again in a few minutes.",
            "status_code": response.status_code
        }
    
    if response.status_code == 401:
        return {
            "error": "Invalid API key. Please check your Hugging Face API key.",
            "status_code": response.status_code
        }
    
    if response.status_code == 400:
        logger.error(f"400 Error details: {response.text}")
        return {
            "error": "Bad request. The image format or request structure is invalid.",
            "status_code": response.status_code,
            "details": response.text
        }
    
    if response.status_code != 200:
        return {
            "error": f"API request failed with status {response.status_code}",
            "status_code": response.status_code,
            "details": response.text
        }
    
    # Try to parse JSON response
    try:
        data = response.json()
        logger.info(f"Parsed API Response: {data}")
        
        # Check for API-level errors
        if isinstance(data, dict) and "error" in data:
            return {
                "error": f"API Error: {data['error']}",
                "status_code": response.status_code
            }
        
        # Add request time to the response if available
        if hasattr(response, 'request_time'):
            if isinstance(data, list):
                data = {"predictions": data, "request_time": response.request_time}
            elif isinstance(data, dict):
                data["request_time"] = response.request_time
        
        return data
        
    except ValueError as e:
        logger.error(f"JSON parsing failed: {str(e)}")
        return {
            "error": "Invalid JSON response from API",
            "status_code": response.status_code,
            "details": response.text
        }

def format_predictions(predictions):
    """
    Format predictions for display with enhanced categorization
    """
    if isinstance(predictions, dict) and "predictions" in predictions:
        # Extract predictions and metadata
        preds = predictions["predictions"]
        metadata = {k: v for k, v in predictions.items() if k != "predictions"}
        
        # Format predictions list
        formatted_results = []
        
        # For object detection models that return boxes
        if isinstance(preds, list) and len(preds) > 0 and isinstance(preds[0], dict) and "box" in preds[0]:
            # Handle object detection format
            for prediction in preds:
                label = prediction.get('label', 'Unknown')
                score = prediction.get('score', 0)
                box = prediction.get('box', {})
                
                formatted_results.append({
                    'label': str(label),
                    'score': float(score),
                    'percentage': f"{float(score) * 100:.2f}%",
                    'box': box,
                    'type': 'object'
                })
                
            # Sort by score
            formatted_results.sort(key=lambda x: x['score'], reverse=True)
            
            # Return with detection type
            return {"predictions": formatted_results, "metadata": metadata, "type": "object_detection"}
            
        # For classification models
        else:
            for prediction in preds:
                if isinstance(prediction, dict):
                    label = prediction.get('label', 'Unknown')
                    score = prediction.get('score', 0)
                    
                    # Handle potential None values
                    if label is None:
                        label = 'Unknown'
                    if score is None:
                        score = 0
                        
                    # Try to categorize prediction types
                    category = "general"
                    if any(word in label.lower() for word in ['person', 'man', 'woman', 'child', 'boy', 'girl']):
                        category = "person"
                    elif any(word in label.lower() for word in ['dog', 'cat', 'bird', 'animal', 'pet', 'wildlife']):
                        category = "animal"
                    elif any(word in label.lower() for word in ['food', 'fruit', 'vegetable', 'meal', 'dish']):
                        category = "food"
                    elif any(word in label.lower() for word in ['landscape', 'beach', 'mountain', 'forest', 'nature', 'outdoor']):
                        category = "landscape"
                    elif any(word in label.lower() for word in ['car', 'vehicle', 'truck', 'bus', 'transportation']):
                        category = "vehicle"
                        
                    formatted_results.append({
                        'label': str(label),
                        'score': float(score),
                        'percentage': f"{float(score) * 100:.2f}%",
                        'category': category
                    })
            
            # Sort by score
            formatted_results.sort(key=lambda x: x['score'], reverse=True)
            
            # Group by categories
            categories = {}
            for result in formatted_results:
                cat = result['category']
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(result)
            
            # Return with categorization
            return {
                "predictions": formatted_results, 
                "metadata": metadata, 
                "categories": categories,
                "type": "classification"
            }
    
    # Handle the case where predictions is directly a list
    elif isinstance(predictions, list):
        formatted_results = []
        for prediction in predictions:
            if isinstance(prediction, dict):
                label = prediction.get('label', 'Unknown')
                score = prediction.get('score', 0)
                
                # Handle potential None values
                if label is None:
                    label = 'Unknown'
                if score is None:
                    score = 0
                    
                formatted_results.append({
                    'label': str(label),
                    'score': float(score),
                    'percentage': f"{float(score) * 100:.2f}%"
                })
        
        return formatted_results
    
    # If it's something else, return as is
    return predictions

def extract_image_insights(predictions, metadata):
    """
    Extract human-readable insights from predictions and metadata
    """
    insights = []
    
    try:
        # Check if we have valid predictions
        if not predictions or not isinstance(predictions, list) or len(predictions) == 0:
            insights.append("No clear subjects were identified in this image.")
            return insights
            
        # Get top prediction
        top_prediction = predictions[0]
        top_label = top_prediction.get('label', '')
        top_score = top_prediction.get('score', 0)
        
        # Basic identification
        if top_score > 0.7:
            insights.append(f"This image primarily shows {top_label} ({top_prediction['percentage']}).")
        elif top_score > 0.5:
            insights.append(f"This image likely contains {top_label} ({top_prediction['percentage']}).")
        else:
            insights.append(f"This image might contain {top_label}, but I'm not very confident ({top_prediction['percentage']}).")
        
        # Multiple subjects
        if len(predictions) > 1:
            secondary_items = [p['label'] for p in predictions[1:4] if p['score'] > 0.3]
            if secondary_items:
                insights.append(f"Also visible: {', '.join(secondary_items)}.")
        
        # Technical insights
        if metadata:
            # Image quality insights
            if 'width' in metadata and 'height' in metadata:
                resolution = metadata['width'] * metadata['height']
                if resolution > 12_000_000:  # >12MP
                    insights.append("This is a high-resolution image with excellent detail.")
                elif resolution > 3_000_000:  # >3MP
                    insights.append("This image has good resolution suitable for standard viewing.")
                else:
                    insights.append("This image has relatively low resolution.")
            
            # Color insights
            if 'brightness_category' in metadata:
                if metadata['brightness_category'] == 'Dark':
                    insights.append("This is a predominantly dark image.")
                elif metadata['brightness_category'] == 'Bright':
                    insights.append("This is a bright, well-lit image.")
            
            # Camera insights
            if 'camera' in metadata and metadata['camera'] != "Unknown Unknown":
                if "iPhone" in metadata['camera'] or "Pixel" in metadata['camera']:
                    insights.append(f"This photo was taken with a {metadata['camera']} smartphone.")
                else:
                    insights.append(f"This photo was taken with a {metadata['camera']} camera.")
                    
            # Exposure settings
            camera_settings = []
            if 'exposure_formatted' in metadata:
                camera_settings.append(f"{metadata['exposure_formatted']} shutter speed")
            if 'aperture' in metadata:
                camera_settings.append(f"{metadata['aperture']}")
            if 'iso' in metadata:
                camera_settings.append(f"ISO {metadata['iso']}")
                
            if camera_settings:
                insights.append(f"Camera settings: {', '.join(camera_settings)}.")
                
            # Location data
            if 'has_location' in metadata and metadata['has_location']:
                insights.append("This image contains geographic location data.")
                
        return insights
        
    except Exception as e:
        logger.error(f"Error extracting insights: {str(e)}")
        return ["Could not generate insights for this image."]

# --- Flask Routes ---
@app.route('/')
def index():
    """
    Render the main page
    """
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    """
    Handle file upload and image classification
    """
    try:
        # Validate file upload
        if 'file1' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
            
        file = request.files['file1']
        
        if file.filename == '' or file.filename is None:
            return jsonify({"error": "No file selected"}), 400
        
        # Validate file type with better error handling
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
        
        # Check if filename contains a dot
        if '.' not in file.filename:
            return jsonify({
                "error": "File must have an extension. Supported types: " + ', '.join(allowed_extensions)
            }), 400
        
        file_extension = file.filename.rsplit('.', 1)[-1].lower()
        
        if not file_extension or file_extension not in allowed_extensions:
            return jsonify({
                "error": f"Unsupported file type: {file_extension}. Supported types: {', '.join(allowed_extensions)}"
            }), 400
        
        # Read image data
        image_bytes = file.read()
        
        if len(image_bytes) == 0:
            return jsonify({"error": "Empty file uploaded"}), 400
        
        logger.info(f"Processing file: {file.filename} ({len(image_bytes)} bytes)")
        logger.info(f"File extension: {file_extension}")
        
        # Get image metadata
        start_time = time.time()
        image_metadata = get_image_metadata(image_bytes)
        metadata_time = time.time() - start_time
        logger.info(f"Metadata extraction time: {metadata_time:.2f} seconds")
        
        # Add filename to metadata
        image_metadata["filename"] = file.filename
        
        try:
            # Query Hugging Face API
            response = query_huggingface_api(image_bytes)
            
            # Process API response
            result = process_api_response(response)
            
            # Check for errors
            if isinstance(result, dict) and "error" in result:
                error_msg = result["error"]
                logger.error(f"API error: {error_msg}")
                # Return the error with metadata for the frontend
                result["metadata"] = image_metadata
                return jsonify(result), 200  # Return 200 to let frontend handle the error display
            
            # Add metadata to result
            if isinstance(result, dict):
                result["metadata"] = image_metadata
            else:
                result = {"predictions": result, "metadata": image_metadata}
            
            # Format predictions
            formatted_result = format_predictions(result)
            
            # Extract insights
            if isinstance(formatted_result, dict) and "predictions" in formatted_result:
                insights = extract_image_insights(formatted_result["predictions"], image_metadata)
                formatted_result["insights"] = insights
            
            # Add additional processing info
            total_time = time.time() - start_time
            if isinstance(formatted_result, dict) and "metadata" in formatted_result:
                formatted_result["metadata"]["total_processing_time"] = f"{total_time:.2f} seconds"
                formatted_result["metadata"]["processing_time_seconds"] = total_time
            
            return jsonify(formatted_result)
        except Exception as api_error:
            logger.error(f"API request error: {str(api_error)}")
            logger.error(traceback.format_exc())
            
            # If API fails, still return metadata and a helpful error message
            error_response = {
                "error": "Failed to connect to the image classification service. Please check your API key and try again.",
                "metadata": image_metadata,
                "details": str(api_error)
            }
            return jsonify(error_response), 200  # Return 200 to let frontend handle the error
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": "An unexpected error occurred while processing your image.",
            "details": str(e)
        }), 500

@app.route('/health')
def health_check():
    """
    Health check endpoint
    """
    # Test API key validity
    api_key_status = "valid" if API_KEY and len(API_KEY) > 30 else "potentially_invalid"
    
    return jsonify({
        "status": "healthy",
        "api_url": API_URL,
        "api_key_status": api_key_status,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

# --- Error Handlers ---
@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "File too large. Maximum size is 16MB."}), 413

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({"error": "Internal server error"}), 500

# --- Run Application ---
if __name__ == '__main__':
    logger.info(f"Starting Flask app...")
    logger.info(f"API URL: {API_URL}")
    logger.info(f"Debug mode: {FLASK_DEBUG}")
    
    # Test API key format
    if API_KEY == "hf_your_actual_api_key_here" or len(API_KEY) < 30:
        logger.warning("⚠️ WARNING: You appear to be using a placeholder API key. The application may not work correctly.")
        logger.warning("Please replace it with a valid Hugging Face API key in your .env file.")
    
    app.run(
        host='0.0.0.0', 
        port=81, 
        debug=FLASK_DEBUG
    )