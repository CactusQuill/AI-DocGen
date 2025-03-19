# AI-DocGen 📸 - Automated Process Documentation Tool


![AI-DocGen Logo](images/logo.png)



AI-DocGen is a powerful Python-based tool that automatically generates professional documentation from screen recordings. It uses AI to detect steps, analyze screenshots, and create detailed documentation in multiple formats.

## 🌟 Features

- **Automated Screen Recording**: Capture your process with high-quality screen recording
- **Smart Step Detection**: Automatically identifies distinct steps in your workflow
- **AI-Powered Descriptions**: Generates detailed descriptions for each step using Google's Gemini Vision API
- **Multiple Output Formats**: Generate documentation in PDF, HTML, or Markdown
- **Interactive UI**: User-friendly Streamlit interface for easy recording and configuration
- **Customizable Sensitivity**: Adjust step detection parameters to match your needs
- **Professional Output**: Clean, well-formatted documentation with images and descriptions

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- FFmpeg (for video processing)
- Google Cloud account with Gemini Vision API access

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/CactusQuill/AI-DocGen.git
   cd AI-DocGen
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install FFmpeg:
   - Windows: Download from [FFmpeg website](https://ffmpeg.org/download.html) and add to PATH
   - Linux: `sudo apt-get install ffmpeg`
   - Mac: `brew install ffmpeg`

5. Set up environment variables:
   - Create a `.env` file in the project root
   - Add your Gemini API key:
     ```
     GEMINI_API_KEY=your_api_key_here
     MODEL_NAME=gemini-vision-1.5
     ```

### Usage

1. Start the application:
   ```bash
   streamlit run app.py
   ```

2. In the web interface:
   - Click "Start Recording" to begin capturing your screen
   - Perform the process you want to document
   - Click "Stop Recording" when finished
   - Adjust step detection settings if needed
   - Generate documentation in your preferred format

## 🛠️ Configuration

### Step Detection Settings

- **Similarity Threshold** (0.0-1.0): Controls how different two frames need to be to be considered separate steps
- **Minimum Time Between Steps** (seconds): Minimum time that must pass between detected steps

### Output Formats

1. **PDF**
   - Professional layout with table of contents
   - Embedded images and formatted text
   - Page numbers and headers

2. **HTML**
   - Responsive design
   - Interactive table of contents
   - Print-friendly styling

3. **Markdown**
   - GitHub-compatible format
   - Easy to version control
   - Convertible to other formats

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Setup

1. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

2. Run tests:
   ```bash
   pytest
   ```

3. Check code style:
   ```bash
   flake8
   black .
   ```
4. Create file ~/.streamlit/config.toml for long time recording and upload biger viedo file.

content of file ~/.streamlit/config.toml:
```
[server]
# Set the maximum size of an uploaded file (in megabytes)
maxUploadSize = 1000  # Set the upload limit to 100MB (default is 200MB)

# Increase the maximum allowed memory usage (in megabytes)
# Default limit is typically 1GB (1024MB)
# Example of setting 2GB:

headless = true
```
## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google Gemini Vision API for AI-powered image analysis
- Streamlit for the amazing web interface framework
- FFmpeg for video processing capabilities
- All our contributors and users

## 📚 Documentation

For detailed documentation, visit our [Wiki](https://github.com/CactusQuill/AI-DocGen/wiki).

## 🐛 Troubleshooting

### Common Issues

1. **Video Playback Issues**
   - Ensure FFmpeg is properly installed
   - Check video codec compatibility
   - Try converting the video manually using FFmpeg

2. **Step Detection Problems**
   - Adjust similarity threshold
   - Increase minimum time between steps
   - Check if screen changes are significant enough

3. **API Issues**
   - Verify API key is correct
   - Check API quota and limits
   - Ensure internet connectivity

### Getting Help

- Open an [Issue](https://github.com/CactusQuill/AI-DocGen/issues)
- Check existing [Discussions](https://github.com/CactusQuill/AI-DocGen/discussions)
- Read our [FAQ](https://github.com/CactusQuill/AI-DocGen/wiki/FAQ)

## 🔄 Updates

- [X] Video file upload
- [X] Long time video recording

Stay updated with new releases:
- Watch this repository
- Follow our [Release Notes](https://github.com/CactusQuill/AI-DocGen/releases)

## 📊 Project Status

AI-DocGen is under active development. We're working on:
- [ ] Multi-monitor support
- [ ] Custom documentation templates
- [ ] Cloud storage integration
- [ ] Batch processing
- [ ] API endpoint for programmatic access

## 💡 Feature Requests

Have an idea? We'd love to hear it!
1. Check existing [Feature Requests](https://github.com/CactusQuill/AI-DocGen/labels/enhancement)
2. Open a new [Discussion](https://github.com/CactusQuill/AI-DocGen/discussions/new)
