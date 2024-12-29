# Automated Documentation Generator

![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Roadmap](#roadmap)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Overview

The **Automated Documentation Generator** is a tool designed to streamline the creation of comprehensive documentation by recording your workflow, capturing significant steps, and generating contextual descriptions automatically. By leveraging screen recording, image processing, and advanced Language Models (LLMs), this solution transforms your recorded activities into structured, easy-to-understand documentation with minimal manual effort.

![Demo](path/to/demo/image.png)

## Features

- **Screen Recording:** Capture your entire workflow with high-quality screen recordings.
- **Step Detection:** Automatically identify significant actions and changes within the recorded video.
- **Screenshot Capture:** Extract and save screenshots at each identified step.
- **Contextual Descriptions:** Generate detailed descriptions for each step using Groq's LLM APIs.
- **Image Processing:** Enhance and analyze screenshots for better documentation quality.
- **Documentation Compilation:** Assemble screenshots and descriptions into structured formats like Markdown, HTML, or PDF.
- **Cross-Platform Support:** Compatible with major operating systems including Windows, macOS, and Linux.
- **Customizable Templates:** Define and use custom templates for documentation layout and styling.
- **API Integration:** Seamlessly integrate with Groq's text and image processing APIs.

## Roadmap

### Phase 1: Project Setup

1. **Initialize Repository**
   - Set up a Git repository for version control.
   - Configure project structure with directories for source code, assets, and documentation.

2. **Environment Setup**
   - Install necessary development tools and dependencies.
   - Set up virtual environments or containerization as needed.

3. **Configuration Management**
   - Create configuration files for API endpoints, model names, and API keys.
   - Ensure sensitive information is secured using environment variables.

### Phase 2: Screen Recording Module

1. **Implement Screen Recording**
   - Integrate screen recording functionality using libraries like OBS Studio or platform-specific APIs.
   - Provide options to start, pause, and stop recordings.

2. **Optimize Recording Settings**
   - Ensure high-quality recordings with minimal performance impact.
   - Support various screen resolutions and frame rates.

### Phase 3: Video Processing and Step Detection

1. **Frame Extraction**
   - Use FFmpeg or OpenCV to extract frames from the recorded video at defined intervals.

2. **Change Detection Algorithm**
   - Implement algorithms to detect significant changes between consecutive frames.
   - Utilize metrics like Structural Similarity Index (SSIM) to quantify changes.

3. **Step Identification**
   - Mark frames where significant changes occur as steps in the workflow.

### Phase 4: Screenshot Capture and Image Processing

1. **Extract Significant Frames**
   - Save screenshots from identified steps for documentation.

2. **Enhance Screenshots**
   - Use image processing tools to crop, annotate, or highlight important areas in screenshots.

### Phase 5: Integration with Groq's LLM APIs

1. **Configure Text Processing API**
   - Set up integration with Groq's Text API for generating step descriptions.
   - Use the specified endpoint and model:
     ```
     TEXT_API_END_POINT=https://api.groq.com/openai/v1
     TEXT_MODEL_NAME=llama3-70b-8192
     TEXT_API_KEYS=["gsk_wvwqWMlh4Iaw...w"]
     ```

2. **Configure Image Processing API**
   - Set up integration with Groq's Image API for processing screenshots.
   - Use the specified endpoint and model:
     ```
     IMAGE_API_END_POINT=https://api.groq.com/openai/v1
     IMAGE_MODEL_NAME=llava-v1.5-7b-4096-preview
     IMAGE_API_KEYS=["gsk_wvwqWMlh4Iaw...w"]
     ```

3. **Generate Descriptions**
   - Send prompts along with screenshots to the Text API to receive contextual descriptions.

4. **Handle API Responses**
   - Parse and store the generated descriptions for each step.

### Phase 6: Documentation Compilation

1. **Define Documentation Structure**
   - Choose the output format (Markdown, HTML, PDF).
   - Design templates for consistent layout and styling.

2. **Assemble Documentation**
   - Combine screenshots and descriptions into the chosen format.
   - Include sections like Introduction, Table of Contents, and individual steps.

3. **Export and Save**
   - Provide options to export documentation in various formats.
   - Save documentation to desired locations or integrate with documentation platforms.

### Phase 7: Testing and Quality Assurance

1. **Unit Testing**
   - Write tests for individual modules to ensure functionality.

2. **Integration Testing**
   - Test the interaction between different modules (recording, processing, API integration).

3. **User Acceptance Testing**
   - Gather feedback from users to refine features and improve usability.

### Phase 8: Deployment and Maintenance

1. **Deploy Application**
   - Package the application for distribution across supported platforms.

2. **Continuous Integration/Continuous Deployment (CI/CD)**
   - Set up CI/CD pipelines for automated testing and deployment.

3. **Maintenance and Updates**
   - Regularly update dependencies and improve features based on user feedback.

## Technologies Used

- **Programming Languages:** Python, JavaScript
- **Screen Recording:** OBS Studio, FFmpeg, OpenCV
- **Image Processing:** OpenCV, Pillow
- **Natural Language Processing:** Groq LLM APIs
- **Documentation Generation:** Markdown, HTML, PDF libraries (e.g., ReportLab)
- **Automation:** Python scripts, Shell scripting
- **Version Control:** Git, GitHub
- **Deployment:** Docker (optional), Platform-specific packaging tools

## Installation

### Prerequisites

- **Python 3.8+**
- **FFmpeg:** [Installation Guide](https://ffmpeg.org/download.html)
- **Git:** [Installation Guide](https://git-scm.com/downloads)

### Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/automated-doc-generator.git
   cd automated-doc-generator
