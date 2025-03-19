import cv2
import time
import numpy as np
import mss
import os
import threading
from pathlib import Path
from typing import Tuple

class ScreenRecorder:
    def __init__(self, output_dir: str = "recordings"):
        """Initialize the screen recorder.
        
        Args:
            output_dir (str): Directory to save recordings
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.recording = False
        self._lock = threading.Lock()
        self.frames = []
        self.timestamps = []

    def start_recording(self, monitor: int = 1) -> None:
        """Start screen recording continuously until stopped.
        
        Args:
            monitor (int): Monitor number to record (default: 1, primary monitor)
        """
        with mss.mss() as sct:  # Create new mss instance in this thread
            self.recording = True
            monitor = sct.monitors[monitor]  # Get monitor info once
            screen_width = monitor["width"]
            screen_height = monitor["height"]
            
            # Set up the codec for video saving
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            
            # Create a video writer object for continuous recording
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_file = str(self.output_dir / f"temp.avi")
            out = cv2.VideoWriter(output_file, fourcc, 30.0, (screen_width, screen_height))
            # Start recording loop
            while self.recording:
                timestamp = time.time()
                frame = np.array(sct.grab(monitor))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                self.timestamps.append(timestamp)

                # Write the current frame to the video file
                out.write(frame)

                time.sleep(1 / 30)  # ~30 FPS (control the frame rate)

            # Release the video writer when the recording is stopped

            out.release()
            print(f"Recording stopped. Video saved at {output_file}")

    def stop_recording(self) -> Tuple[str, list]:
        """Stop recording and save the video.
        
        Returns:
            Tuple[str, list]: Path to saved video and list of timestamps
        """
        self.recording = False
        time.sleep(0.1)  # Give recording thread time to stop
                
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        temp_output = str(self.output_dir / f"temp.avi")
        timestamps = self.timestamps.copy()
        final_output = str(self.output_dir / f"recording_{timestamp}.mp4")
                
        self.frames = []
        self.timestamps = []
        
        # Convert to web-compatible MP4 using ffmpeg
                    
        import subprocess
        try:
            # Ensure the conversion is done with web-compatible settings
            subprocess.run([
                'ffmpeg', '-i', temp_output,
                '-c:v', 'libx264',  # Use H.264 codec
                '-preset', 'medium',  # Balance between speed and quality
                '-crf', '23',  # Quality level (lower is better, 23 is default)
                '-movflags', '+faststart',  # Enable fast start for web playback
                '-y',  # Overwrite output file if it exists
                final_output
            ], check=True, capture_output=True)
            
            # Remove temporary file
            import os
            os.remove(temp_output)
            
            return final_output, timestamps
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg error: {e.stderr.decode()}")
            # If ffmpeg fails, return the original AVI file
            import shutil
            shutil.move(temp_output, final_output)
            return final_output, timestamps
        except Exception as e:
            print(f"Error during conversion: {e}")
            return temp_output, timestamps
        
#        return "Recording stopped and saved.", []

    def capture_screenshot(self, monitor: int = 1) -> np.ndarray:
        """Capture a single screenshot.
        
        Args:
            monitor (int): Monitor number to capture
            
        Returns:
            np.ndarray: Screenshot as numpy array
        """
        with mss.mss() as sct:
            screenshot = np.array(sct.grab(sct.monitors[monitor]))
            return cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)
