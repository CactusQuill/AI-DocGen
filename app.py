import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_extras.switch_page_button import switch_page
from streamlit_lottie import st_lottie
import requests
import json
from pathlib import Path
import os
import numpy as np
from screendoc import ScreenRecorder, StepDetector, DocumentationGenerator
import time
import tempfile
import cv2

# Page config
st.set_page_config(
    page_title="ScreenDoc - Automated Documentation Generator",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #FF4B4B;
        color: white;
        border: none;
    }
    .stButton>button:hover {
        background-color: #FF6B6B;
        color: white;
    }
    .status-box {
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .recording {
        background-color: rgba(255, 75, 75, 0.1);
        border: 1px solid #FF4B4B;
    }
    .success {
        background-color: rgba(0, 255, 0, 0.1);
        border: 1px solid #00FF00;
    }
    .step-preview {
        border: 1px solid #ddd;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    .step-preview img {
        max-width: 100%;
        height: auto;
        border: 1px solid #eee;
        border-radius: 3px;
    }
    </style>
""", unsafe_allow_html=True)

def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def process_video(video_file):
    # Създаваме временен файл за каченото видео
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(video_file.read())  # Записваме каченото видео
        temp_file_path = temp_file.name  # Вземаме пътя до временния файл

    # Отваряме видеото с OpenCV
    cap = cv2.VideoCapture(temp_file_path)
    
    if not cap.isOpened():
        st.error("Не може да се отвори видео файла.")
        return []
    
    timestamps = []  # Списък за времеви печати на кадрите
    frame_rate = cap.get(cv2.CAP_PROP_FPS)  # Получаваме FPS (кадри в секунда)
    
    # Четене на кадрите от видеото
    while True:
        ret, frame = cap.read()  # Четем следващия кадър
        if not ret:
            break  # Ако няма повече кадри, прекратяваме цикъла
        
        timestamp = time.time()  # Вземаме текущото време
        timestamps.append(timestamp)  # Добавяме времевия печат в списъка

    # Затваряме видеото след обработката
    cap.release()

    return timestamps
# Initialize session state variables
if 'recording' not in st.session_state:
    st.session_state.recording = False
if 'current_step' not in st.session_state:
    st.session_state.current_step = 0
if 'steps' not in st.session_state:
    st.session_state.steps = []
if 'output_path' not in st.session_state:
    st.session_state.output_path = None
if 'timestamps' not in st.session_state:
    st.session_state.timestamps = None
if 'recorder' not in st.session_state:
    st.session_state.recorder = None
if 'recording_thread' not in st.session_state:
    st.session_state.recording_thread = None
if 'doc_path' not in st.session_state:
    st.session_state.doc_path = None

# Create output directories
output_dir = Path("output")
recordings_dir = output_dir / "recordings"
screenshots_dir = output_dir / "screenshots"
docs_dir = output_dir / "docs"
timestamps1 = []
for dir_path in [output_dir, recordings_dir, screenshots_dir, docs_dir]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Sidebar
with st.sidebar:
    st.image("https://raw.githubusercontent.com/your-username/ScreenDoc/main/assets/logo.png", width=200)
    selected = option_menu(
        menu_title="Navigation",
        options=["Record", "Review", "Generate", "Settings"],
        icons=["camera-video", "eye", "file-earmark-text", "gear"],
        menu_icon="house",
        default_index=0,
    )

# Main content
st.title("ScreenDoc")
st.subheader("Automated Documentation Generator")

if selected == "Record":
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Animation
        lottie_recording = load_lottie_url("https://assets5.lottiefiles.com/packages/lf20_9aa9jkxv.json")
        st_lottie(lottie_recording, height=300, key="recording_animation")
        
        # Recording status
        if st.session_state.recording:
            st.markdown("""
                <div class='status-box recording'>
                    <h3>🔴 Recording in progress...</h3>
                    <p>Click "Stop Recording" when you're done.</p>
                </div>
            """, unsafe_allow_html=True)
        st.title("Upload and Display Video")
        # File uploader widget to upload a video
        video_file = st.file_uploader("Choose a video...", type=["mp4", "mov", "avi", "mkv"])
        if video_file is not None:
          timestamps = process_video(video_file)  # Извикваме функцията за обработка на видеото
        video_path = recordings_dir / "temp.avi" 
        if video_file:
          with open(video_path, "wb") as f:
              f.write(video_file.getbuffer())

          with st.spinner("Convert video"):
            recorder = ScreenRecorder(str(recordings_dir))
            st.session_state.recorder = recorder
            st.session_state.recording = False
            video_file, timestamps1 = st.session_state.recorder.stop_recording()
            st.session_state.output_path = video_file
            st.session_state.timestamps = timestamps

        # Recording controls
        if not st.session_state.recording:
            if st.button("Start Recording", key="start_recording"):
                st.session_state.recording = True
                # Initialize recorder with proper output directory
                recorder = ScreenRecorder(str(recordings_dir))
                st.session_state.recorder = recorder
                # Start recording in a separate thread
                import threading
                recording_thread = threading.Thread(target=recorder.start_recording, daemon=True)
                recording_thread.start()
                st.session_state.recording_thread = recording_thread
                st.rerun()
        else:
            if st.button("Stop Recording", key="stop_recording"):
                with st.spinner("Convert video"):
                  try:  
                    if st.session_state.recorder:
                        st.session_state.recording = False
                        # Stop recording and save
                        video_path, timestamps = st.session_state.recorder.stop_recording()
                        if video_path:
                            st.session_state.output_path = video_path
                            st.session_state.timestamps = timestamps
                            st.success(f"Recording saved successfully!")
                        else:
                            st.error("No frames were recorded. Please try again.")
                        # Clean up
                        st.session_state.recorder = None
                        st.session_state.recording_thread = None
                        st.rerun()
                  except Exception as e2:
                    st.error(f"Could not convert video: {str(e2)}")
     
    
    with col2:
        st.markdown("### Recording Settings")
        st.slider("Quality", 1, 100, 80, key="quality")
        st.slider("FPS", 1, 60, 30, key="fps")

elif selected == "Review":
    if st.session_state.output_path and Path(st.session_state.output_path).exists():
        # Create two columns for video and steps
        video_col, steps_col = st.columns([1.5, 1])
        
        with video_col:
            st.markdown("### Video Preview")
            try:
                video_path = Path(st.session_state.output_path)
                if not video_path.exists():
                    st.error("Video file not found!")
                else:
                    # Read video file in binary mode
                    with open(video_path, 'rb') as video_file:
                        video_bytes = video_file.read()
                        
                    # Create a download button for the video
                    st.download_button(
                        label="Download Video",
                        data=video_bytes,
                        file_name=video_path.name,
                        mime="video/mp4"
                    )
                    
                    # Display video with error handling
                    try:
                        st.video(video_bytes, format="video/mp4")
                    except Exception as e:
                        st.error(f"Error displaying video. Try downloading it instead. Error: {str(e)}")
                        
                        # Fallback: show first frame as image
                        try:
                            import cv2
                            cap = cv2.VideoCapture(str(video_path))
                            ret, frame = cap.read()
                            if ret:
                                st.image(frame, channels="BGR", caption="First frame of the recording")
                            cap.release()
                        except Exception as e2:
                            st.error(f"Could not show preview frame: {str(e2)}")
            except Exception as e:
                st.error(f"Error accessing video file: {str(e)}")
            
            # Step Detection Settings
            st.markdown("### Step Detection Settings")
            col1, col2 = st.columns(2)
            
            with col1:
                similarity_threshold = st.slider(
                    "Similarity Threshold",
                    min_value=0.5,
                    max_value=1.0,
                    value=0.85,
                    step=0.05,
                    help="Lower values will detect more subtle changes (more steps), higher values will only detect significant changes (fewer steps)"
                )
            
            with col2:
                min_time_between = st.slider(
                    "Minimum Time Between Steps (seconds)",
                    min_value=0.1,
                    max_value=5.0,
                    value=1.0,
                    step=0.1,
                    help="Minimum time that must pass between detected steps"
                )
            
            if st.button("Detect Steps"):
                with st.spinner("Detecting steps..."):
                    detector = StepDetector(
                        similarity_threshold=similarity_threshold,
                        min_time_between_steps=min_time_between
                    )
                    steps = detector.detect_steps(str(video_path), st.session_state.timestamps)
                    
                    # Save detection parameters
                    st.session_state.similarity_threshold = similarity_threshold
                    st.session_state.min_time_between = min_time_between
                    
                    # Save screenshots
                    screenshot_paths = detector.save_screenshots(steps, str(screenshots_dir))
                    st.session_state.steps = steps
                    st.session_state.screenshot_paths = screenshot_paths
                    st.success(f"Detected {len(steps)} steps!")
                    
                    # Show detection summary
                    st.info(f"""
                        Detection Summary:
                        - Similarity Threshold: {similarity_threshold}
                        - Min Time Between Steps: {min_time_between}s
                        - Total Steps Detected: {len(steps)}
                    """)
                    st.rerun()
        
        with steps_col:
            if st.session_state.steps:
                st.markdown("### Detected Steps")
                
                # Show current detection settings if available
                if hasattr(st.session_state, 'similarity_threshold'):
                    st.markdown(f"""
                        *Current Detection Settings:*
                        - Similarity: {st.session_state.similarity_threshold}
                        - Min Time: {st.session_state.min_time_between}s
                    """)
                
                # Add select all/none buttons
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Select All"):
                        st.session_state.selected_steps = list(range(len(st.session_state.steps)))
                        st.rerun()
                with col2:
                    if st.button("Clear All"):
                        st.session_state.selected_steps = []
                        st.rerun()
                
                # Initialize selected steps if not exists
                if 'selected_steps' not in st.session_state:
                    st.session_state.selected_steps = list(range(len(st.session_state.steps)))
                
                # Keep track of steps to delete
                if 'steps_to_delete' not in st.session_state:
                    st.session_state.steps_to_delete = set()
                
                # Show steps with delete buttons
                for i, step in enumerate(st.session_state.steps):
                    if i not in st.session_state.steps_to_delete:  # Only show non-deleted steps
                        with st.container():
                            col1, col2 = st.columns([0.8, 0.2])
                            with col1:
                                step_selected = st.checkbox(
                                    f"Step {i+1}", 
                                    value=i in st.session_state.selected_steps,
                                    key=f"step_{i}"
                                )
                                if step_selected and i not in st.session_state.selected_steps:
                                    st.session_state.selected_steps.append(i)
                                elif not step_selected and i in st.session_state.selected_steps:
                                    st.session_state.selected_steps.remove(i)
                            
                            with col2:
                                if st.button("🗑️", key=f"delete_{i}"):
                                    st.session_state.steps_to_delete.add(i)
                                    st.rerun()
                            
                            if i in st.session_state.selected_steps:
                                with st.expander("Preview", expanded=False):
                                    if i in st.session_state.screenshot_paths:
                                        st.image(st.session_state.screenshot_paths[i])
                                    st.text(f"Similarity Score: {step.similarity_score:.2f}")
                
                # Apply deletions if there are any
                if st.session_state.steps_to_delete:
                    # Remove steps and screenshots
                    new_steps = []
                    new_screenshots = {}
                    new_index = 0
                    
                    for i, step in enumerate(st.session_state.steps):
                        if i not in st.session_state.steps_to_delete:
                            new_steps.append(step)
                            if i in st.session_state.screenshot_paths:
                                new_screenshots[new_index] = st.session_state.screenshot_paths[i]
                            new_index += 1
                    
                    st.session_state.steps = new_steps
                    st.session_state.screenshot_paths = new_screenshots
                    st.session_state.steps_to_delete = set()  # Clear the deletion set
                    st.session_state.selected_steps = list(range(len(new_steps)))  # Reset selection
                    st.success("Steps deleted successfully!")
                    st.rerun()
    else:
          st.info("Please record a video first!")

elif selected == "Generate":
    if st.session_state.steps and hasattr(st.session_state, 'screenshot_paths'):
        # Create two columns for controls and preview
        control_col, preview_col = st.columns([1, 2])
        
        with control_col:
            st.markdown("### Documentation Generation")
            format_option = st.selectbox(
                "Output Format",
                ["Markdown", "HTML", "PDF"],
                key="format"
            )
            
            template_option = st.selectbox(
                "Template",
                ["Default", "Tutorial", "Technical", "Process"],
                key="template"
            )
            
            if st.button("Generate Documentation"):
                with st.spinner("Generating documentation..."):
                    try:
                        generator = DocumentationGenerator()
                        doc_path = generator.generate_documentation(
                            st.session_state.steps,
                            st.session_state.screenshot_paths,
                            format_option.lower()
                        )
                        st.session_state.doc_path = doc_path
                        st.success(f"Documentation generated successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error generating documentation: {str(e)}")
        
        with preview_col:
            if st.session_state.doc_path and Path(st.session_state.doc_path).exists():
                st.markdown("### Documentation Preview")
                
                # Show preview based on format
                if format_option.lower() == "markdown":
                    with open(st.session_state.doc_path, 'r') as f:
                        st.markdown(f.read())
                elif format_option.lower() == "html":
                    with open(st.session_state.doc_path, 'r') as f:
                        st.components.v1.html(f.read(), height=600)
                else:  # PDF
                    st.markdown("### PDF Preview")
                    with open(st.session_state.doc_path, 'rb') as f:
                        st.download_button(
                            "Download PDF",
                            f.read(),
                            file_name="documentation.pdf",
                            mime="application/pdf"
                        )
                
                # Add open in new window button
                if format_option.lower() in ["markdown", "html"]:
                    doc_url = f"file://{st.session_state.doc_path}"
                    st.markdown(f"""
                        <a href="{doc_url}" target="_blank">
                            <button style="background-color: #4CAF50; color: white; padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer;">
                                Open in New Window
                            </button>
                        </a>
                    """, unsafe_allow_html=True)
    else:
        st.info("Please record and detect steps first!")

else:  # Settings
    st.markdown("### Application Settings")
    
    # API Settings
    st.subheader("API Configuration")
    text_api_key = st.text_input("Text API Key", type="password")
    image_api_key = st.text_input("Image API Key", type="password")
    
    # Detection Settings
    st.subheader("Step Detection Settings")
    similarity_threshold = st.slider(
        "Similarity Threshold",
        min_value=0.0,
        max_value=1.0,
        value=0.85,
        help="Threshold for detecting significant changes (0-1)"
    )
    
    min_time_between_steps = st.slider(
        "Minimum Time Between Steps (seconds)",
        min_value=0.1,
        max_value=5.0,
        value=1.0,
        help="Minimum time gap between detected steps"
    )
    
    if st.button("Save Settings"):
        # Save settings to .env file
        with open(".env", "w") as f:
            f.write(f"TEXT_API_KEY={text_api_key}\n")
            f.write(f"IMAGE_API_KEY={image_api_key}\n")
            f.write(f"SIMILARITY_THRESHOLD={similarity_threshold}\n")
            f.write(f"MIN_TIME_BETWEEN_STEPS={min_time_between_steps}\n")
        st.success("Settings saved successfully!")
