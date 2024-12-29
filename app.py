import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_extras.switch_page_button import switch_page
from streamlit_lottie import st_lottie
import requests
import json
from pathlib import Path
import os
from screendoc import ScreenRecorder, StepDetector, DocumentationGenerator

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
                # Get relative path for video display
                video_path = Path(st.session_state.output_path)
                video_bytes = video_path.read_bytes()
                
                # Create a unique key for the video player
                video_key = f"video_{hash(str(video_path))}"
                st.video(video_bytes, key=video_key)
            except Exception as e:
                st.error(f"Error loading video: {str(e)}")
            
            if st.button("Detect Steps"):
                with st.spinner("Detecting steps..."):
                    detector = StepDetector()
                    steps = detector.detect_steps(str(video_path), st.session_state.timestamps)
                    # Save screenshots
                    screenshot_paths = detector.save_screenshots(steps, str(screenshots_dir))
                    st.session_state.steps = steps
                    st.session_state.screenshot_paths = screenshot_paths
                    st.success(f"Detected {len(steps)} steps!")
                    st.rerun()
        
        with steps_col:
            if st.session_state.steps:
                st.markdown("### Detected Steps")
                
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
