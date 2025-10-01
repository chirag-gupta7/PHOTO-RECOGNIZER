# 🖼️ AI Image Analyzer

A powerful, interactive web application that analyzes photos using artificial intelligence to identify objects, extract metadata, and provide detailed insights about images. Built with Flask, Python, and modern web technologies.

## 📺 Demo Video

[![AI Image Analyzer Demo](https://img.youtube.com/vi/iQtsDFo8u_E/maxresdefault.jpg)](https://youtu.be/iQtsDFo8u_E)

*Click the image above to watch a full demonstration of the AI Image Analyzer application*

## 📋 Table of Contents

- [Features](#-features)
- [Quick Start](#-quick-start)
- [Technology Stack](#️-technology-stack)
- [Project Structure](#-project-structure)
- [Core Components](#-core-components)
- [Usage Guide](#-usage-guide)
- [API Integration](#-api-integration-details)
- [Configuration](#-configuration-options)
- [Troubleshooting](#-troubleshooting)
- [Security](#-security-considerations)
- [Browser Compatibility](#-browser-compatibility)
- [Future Enhancements](#-future-enhancements)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features
### 🤖 AI-Powered Image Classification
- **Object Detection**: Identifies objects, people, animals, vehicles, and more
- **Multi-Label Classification**: Recognizes multiple subjects in a single image
- **Confidence Scoring**: Provides accuracy percentages for each prediction
- **Category Grouping**: Organizes results by type (person, animal, food, landscape, etc.)

### 📊 Comprehensive Metadata Analysis
- **EXIF Data Extraction**: Camera settings, lens information, date/time
- **Technical Specifications**: File size, dimensions, format, color mode
- **Color Analysis**: Dominant colors, brightness, contrast, color histograms
- **Camera Information**: Make, model, exposure settings, GPS data
- **Image Processing**: Thumbnail generation, hash calculation

### 🎨 Modern User Interface
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Dark/Light Mode**: Toggle between themes with persistent preference
- **Drag & Drop**: Easy file upload with visual feedback
- **Progressive Enhancement**: Smooth animations and transitions
- **Interactive Tabs**: Organized metadata display with categorized tabs

### 🔧 Advanced Technical Features
- **Real-time Processing**: Live image preview and instant analysis
- **Error Handling**: Graceful error messages with fallback options
- **API Integration**: Seamless connection to Hugging Face AI models
- **Performance Monitoring**: Request timing and processing metrics
- **File Validation**: Comprehensive file type and size checking
## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Hugging Face API key (free to obtain)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/chirag-gupta7/PHOTO-RECOGNIZER.git
   cd PHOTO-RECOGNIZER
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   Create a `.env` file in the project root:
   ```env
   HUGGING_FACE_API_URL=https://api-inference.huggingface.co/models/google/vit-base-patch16-224
   HUGGING_FACE_API_KEY=hf_your_actual_api_key_here
   FLASK_ENV=development
   FLASK_DEBUG=True
   ```

4. **Get your Hugging Face API key:**
   - Visit [Hugging Face](https://huggingface.co)
   - Create a free account
   - Go to Settings → Access Tokens
   - Create a new token and copy it to your `.env` file

5. **Run the application:**
   ```bash
   python photo_check.py
   ```

6. **Open your browser:**
   The application will automatically open at `http://localhost:81`
## 🛠️ Technology Stack

### Backend Technologies
- **Flask 2.0.1**: Web framework for Python
- **Pillow (PIL) 9.0.0**: Image processing library
- **NumPy 1.21.0**: Numerical computing for color analysis
- **Requests 2.26.0**: HTTP library for API calls
- **Python-dotenv 0.19.0**: Environment variable management

### Frontend Technologies
- **HTML5**: Semantic markup with modern standards
- **CSS3**: Custom properties, Grid, Flexbox, animations
- **JavaScript (ES6+)**: Modern JavaScript with async/await
- **Font Awesome 6.0**: Icon library for UI elements
- **Google Fonts**: Poppins font family

### AI/ML Integration
- **Hugging Face Transformers**: Pre-trained vision models
- **Vision Transformer (ViT)**: Google's ViT-base-patch16-224 model
- **Image Classification**: Multi-class object recognition
- **API Integration**: RESTful API communication
## 📁 Project Structure

```
PHOTO-RECOGNIZER/
├── photo_check.py          # Main Flask application
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables (create this)
├── README.md              # This file
├── static/
│   ├── css/
│   │   └── style.css      # Main stylesheet with themes
│   └── js/
│       └── script.js      # Frontend JavaScript logic
└── templates/
    └── index.html         # Main HTML template
```


## 🔧 Core Components

### 1. Flask Application (`photo_check.py`)

**Main Features:**
- File Upload Handler: Processes image uploads with validation
- API Integration: Connects to Hugging Face models
- Metadata Extraction: Comprehensive EXIF and image analysis
- Error Handling: Robust error management with user-friendly messages
- Health Check: API status monitoring endpoint

**Key Functions:**
```python
def get_image_metadata(image_bytes)    # Extract comprehensive metadata
def query_huggingface_api(image_bytes) # Connect to AI models
def process_api_response(response)     # Handle API responses
def format_predictions(predictions)    # Format AI predictions
def extract_image_insights(predictions, metadata) # Generate insights
```

### 2. Frontend Interface (`templates/index.html`)

**Components:**
- Upload Area: Drag & drop with visual feedback
- Image Preview: Real-time image display
- Results Display: Organized prediction results
- Metadata Tabs: Categorized technical information
- Theme Toggle: Dark/light mode switcher

### 3. Styling (`static/css/style.css`)

**Features:**
- CSS Custom Properties: Dynamic theming system
- Responsive Design: Mobile-first approach
- Animations: Smooth transitions and hover effects
- Color Schemes: Carefully crafted light/dark themes
- Component Library: Reusable UI components

### 4. Interactive Logic (`static/js/script.js`)

**Functionality:**
- File Handling: Drag & drop and click-to-upload
- API Communication: Fetch API for backend requests
- UI Updates: Dynamic content rendering
- Error Management: User-friendly error displays
- Theme Persistence: Local storage for preferences
## 🎯 Usage Guide

### Basic Usage
1. **Upload Image**: Drag & drop or click to select an image file
2. **Analyze**: Click "Analyze Image" to process the photo
3. **View Results**: See AI predictions with confidence scores
4. **Explore Metadata**: Click "Show Detailed Information" for technical details

### Supported Formats
- JPEG (`.jpg`, `.jpeg`)
- PNG (`.png`)
- GIF (`.gif`)
- BMP (`.bmp`)
- WEBP (`.webp`)

### File Size Limits
- **Maximum**: 16MB per image
- **Recommended**: Under 5MB for optimal performance
## 🔍 API Integration Details

### Hugging Face Models
The application uses Google's Vision Transformer (ViT) model:
- **Model**: `google/vit-base-patch16-224`
- **Type**: Image classification
- **Classes**: 1000+ ImageNet categories
- **Input**: 224x224 pixel images
- **Output**: Probability scores for each class

### API Configuration
```python
# Environment variables
API_URL = "https://api-inference.huggingface.co/models/google/vit-base-patch16-224"
API_KEY = "hf_your_actual_api_key_here"

# Request headers
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/octet-stream"
}
```

### Error Handling
- **503 Service Unavailable**: Model loading, retry after delay
- **401 Unauthorized**: Invalid API key
- **400 Bad Request**: Invalid image format
- **Network Errors**: Connection timeout handling
### 📊 Metadata Analysis Features

#### EXIF Data Extraction
**Camera Information:**
- Make/Model: Camera manufacturer and model
- Lens: Lens model and specifications
- Exposure: Shutter speed, aperture, ISO
- Date/Time: Photo capture timestamp
- GPS: Location data if available

**Technical Details:**
- Dimensions: Width x Height in pixels
- File Size: Size in KB/MB
- Format: JPEG, PNG, etc.
- Color Mode: RGB, RGBA, etc.

#### Color Analysis
**Advanced Color Processing:**
- Dominant Colors: K-means clustering approach
- Average Color: RGB and HEX values
- Brightness: Percentage and category
- Contrast: Standard deviation analysis
- Color Histogram: RGB distribution

#### Image Processing
**Metadata Enhancement:**
- Thumbnail Generation: 200x200 preview
- Hash Calculation: MD5 and SHA256
- Aspect Ratio: Calculated ratio
- Processing Time: Performance metrics


### 🎨 UI/UX Features

#### Responsive Design
- **Mobile-First**: Optimized for smartphones
- **Tablet Support**: Adapted layouts for tablets
- **Desktop Enhancement**: Full-featured desktop experience

#### Theme System
```css
/* CSS Custom Properties */
:root {
    --primary: #4285f4;
    --secondary: #34a853;
    --accent: #fbbc05;
    --text-dark: #333333;
    --bg-light: #f8f9fa;
    /* ... more variables */
}

/* Dark Mode Override */
body.dark-mode {
    --text-dark: #e0e0e0;
    --bg-light: #121212;
    /* ... dark theme values */
}
```

#### Animations
- **Fade In**: Smooth content appearance
- **Progress Bars**: Animated confidence scores
- **Hover Effects**: Interactive element feedback
- **Loading States**: Visual processing indicators
## 🔧 Configuration Options

### Environment Variables
```env
# Required
HUGGING_FACE_API_URL=<model_endpoint>
HUGGING_FACE_API_KEY=<your_api_key>

# Optional
FLASK_ENV=development
FLASK_DEBUG=True
```

### Flask Configuration
```python
# Application Settings
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.run(host='0.0.0.0', port=81, debug=FLASK_DEBUG)
```

### Model Configuration
You can easily switch to different Hugging Face models:
```python
# Alternative models
API_URL = "https://api-inference.huggingface.co/models/microsoft/resnet-50"
API_URL = "https://api-inference.huggingface.co/models/facebook/detr-resnet-50"
```


### 🚀 Performance Optimization

#### Backend Optimizations
- **Thumbnail Generation**: Reduced image size for faster processing
- **Concurrent Processing**: Parallel metadata extraction
- **Caching**: Response caching for repeated requests
- **Error Recovery**: Graceful degradation on API failures

#### Frontend Optimizations
- **Lazy Loading**: Images loaded on demand
- **Debounced Requests**: Prevent duplicate API calls
- **Local Storage**: Theme preferences persistence
- **Efficient DOM Updates**: Minimal reflow/repaint

## 🐛 Troubleshooting

### Common Issues

#### 1. API Key Problems
**Problem**: "Invalid API key" error

**Solution**:
- Check your `.env` file exists
- Verify API key format starts with `hf_`
- Ensure no extra spaces in the key

#### 2. Model Loading
**Problem**: "Model is currently loading" message

**Solution**:
- Wait 2-3 minutes for model to initialize
- Try again after delay
- Check Hugging Face service status

#### 3. File Upload Issues
**Problem**: "File too large" or "Unsupported format"

**Solution**:
- Ensure file is under 16MB
- Use supported formats (JPEG, PNG, GIF, BMP, WEBP)
- Check file isn't corrupted

#### 4. Dark Mode Not Working
**Problem**: Theme toggle not functioning

**Solution**:
- Clear browser cache
- Enable JavaScript
- Check browser console for errors

### Debug Mode
Enable debug mode for detailed error messages:
```env
FLASK_DEBUG=True
```


## � Future Enhancements

### Planned Features
- **Batch Processing**: Multiple image analysis
- **History**: Previous analysis results
- **Export**: Download results as PDF/JSON
- **Custom Models**: User-uploaded model support
- **Advanced Filters**: Image enhancement tools

### Technical Improvements
- **Database**: Result persistence
- **Caching**: Redis/Memcached integration
- **Authentication**: User accounts
- **API Rate Limiting**: Request throttling
- **Containerization**: Docker support

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

### Getting Help
- **Issues**: Report bugs on GitHub
- **Questions**: Check documentation first
- **Feature Requests**: Submit enhancement proposals

### Developer Contact
- **GitHub**: [@chirag-gupta7](https://github.com/chirag-gupta7)
- **Instagram**: [@chirag_gupta._.1](https://instagram.com/chirag_gupta._.1)

## 🙏 Acknowledgments

- **Hugging Face**: AI model hosting and inference
- **Google**: Vision Transformer model
- **Flask Community**: Web framework
- **Font Awesome**: Icon library
- **Google Fonts**: Typography

## 📊 Project Statistics

- **Languages**: Python, JavaScript, HTML, CSS
- **Framework**: Flask
- **AI Models**: Vision Transformer
- **UI Library**: Custom CSS + Font Awesome
- **File Size**: ~50KB total
- **Dependencies**: 5 Python packages
- **Browser Support**: 95%+ modern browsers

---

**Made with ❤️ by [Chirag Gupta](https://github.com/chirag-gupta7)**

*This project demonstrates the power of combining modern web technologies with artificial intelligence to create intuitive, user-friendly applications.*
