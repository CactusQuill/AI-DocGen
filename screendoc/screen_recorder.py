import time
import mss
import cv2
import numpy as np
from pathlib import Path
from typing import Optional, Tuple

class ScreenRecorder:
    def __init__(self, output_dir: str = "recordings"):
        """Initialize the screen recorder.
        
        Args:
            output_dir (str): Directory to save recordings
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.sct = mss.mss()
        self.recording = False
        self.frames = []
        self.timestamps = []
        
    def start_recording(self, monitor: int = 1) -> None:
        """Start screen recording.
        
        Args:
            monitor (int): Monitor number to record (default: 1, primary monitor)
        """
        self.recording = True
        self.frames = []
        self.timestamps = []
        
        while self.recording:
            timestamp = time.time()
            frame = np.array(self.sct.grab(self.sct.monitors[monitor]))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            self.frames.append(frame)
            self.timestamps.append(timestamp)
            time.sleep(0.1)  # Add a small delay to reduce CPU usage
            
    def stop_recording(self) -> Tuple[str, list]:
        """Stop recording and save the video.
        
        Returns:
            Tuple[str, list]: Path to saved video and list of timestamps
        """
        self.recording = False
        if not self.frames:
            return None, []
            
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_path = str(self.output_dir / f"recording_{timestamp}.mp4")
        
        height, width = self.frames[0].shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, 30.0, (width, height))
        
        for frame in self.frames:
            out.write(frame)
            
        out.release()
        return output_path, self.timestamps
        
    def capture_screenshot(self, monitor: int = 1) -> np.ndarray:
        """Capture a single screenshot.
        
        Args:
            monitor (int): Monitor number to capture
            
        Returns:
            np.ndarray: Screenshot as numpy array
        """
        screenshot = np.array(self.sct.grab(self.sct.monitors[monitor]))
        return cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)
