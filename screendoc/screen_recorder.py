import time
import mss
import cv2
import numpy as np
from pathlib import Path
from typing import Optional, Tuple
import threading

class ScreenRecorder:
    def __init__(self, output_dir: str = "recordings"):
        """Initialize the screen recorder.
        
        Args:
            output_dir (str): Directory to save recordings
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.recording = False
        self.frames = []
        self.timestamps = []
        self._lock = threading.Lock()
        
    def start_recording(self, monitor: int = 1) -> None:
        """Start screen recording.
        
        Args:
            monitor (int): Monitor number to record (default: 1, primary monitor)
        """
        with mss.mss() as sct:  # Create new mss instance in this thread
            self.recording = True
            monitor = sct.monitors[monitor]  # Get monitor info once
            
            while self.recording:
                with self._lock:
                    timestamp = time.time()
                    frame = np.array(sct.grab(monitor))
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                    self.frames.append(frame)
                    self.timestamps.append(timestamp)
                time.sleep(0.033)  # ~30 FPS
            
    def stop_recording(self) -> Tuple[str, list]:
        """Stop recording and save the video.
        
        Returns:
            Tuple[str, list]: Path to saved video and list of timestamps
        """
        self.recording = False
        time.sleep(0.1)  # Give recording thread time to stop
        
        with self._lock:
            if not self.frames:
                return None, []
                
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            temp_output = str(self.output_dir / f"temp_{timestamp}.avi")
            final_output = str(self.output_dir / f"recording_{timestamp}.mp4")
            
            height, width = self.frames[0].shape[:2]
            
            # First save as AVI with raw frames
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(temp_output, fourcc, 30.0, (width, height))
            
            for frame in self.frames:
                out.write(frame)
            
            out.release()
            timestamps = self.timestamps.copy()
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
