import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Step:
    timestamp: float
    screenshot: np.ndarray
    description: str = ""
    similarity_score: float = 0.0

class StepDetector:
    def __init__(self, similarity_threshold: float = 0.85, min_time_between_steps: float = 1.0):
        """Initialize the step detector.
        
        Args:
            similarity_threshold (float): Threshold for detecting significant changes (0-1)
            min_time_between_steps (float): Minimum time between steps in seconds
        """
        self.similarity_threshold = similarity_threshold
        self.min_time_between_steps = min_time_between_steps
        
    def calculate_similarity(self, frame1: np.ndarray, frame2: np.ndarray) -> float:
        """Calculate structural similarity between two frames.
        
        Args:
            frame1 (np.ndarray): First frame
            frame2 (np.ndarray): Second frame
            
        Returns:
            float: Similarity score between 0 and 1
        """
        # Convert frames to grayscale
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        
        # Calculate SSIM
        try:
            score = cv2.matchTemplate(gray1, gray2, cv2.TM_CCOEFF_NORMED)[0][0]
            return max(0.0, min(1.0, score))  # Ensure score is between 0 and 1
        except:
            return 0.0
            
    def detect_steps(self, video_path: str, timestamps: List[float]) -> List[Step]:
        """Detect significant steps in a recorded video.
        
        Args:
            video_path (str): Path to the recorded video
            timestamps (List[float]): List of frame timestamps
            
        Returns:
            List[Step]: List of detected steps
        """
        cap = cv2.VideoCapture(video_path)
        steps = []
        prev_frame = None
        prev_timestamp = 0
        frame_idx = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            current_timestamp = timestamps[frame_idx]
            
            if prev_frame is None:
                # First frame is always a step
                steps.append(Step(
                    timestamp=current_timestamp,
                    screenshot=frame.copy(),
                    similarity_score=1.0
                ))
            else:
                # Check time difference
                time_diff = current_timestamp - prev_timestamp
                
                if time_diff >= self.min_time_between_steps:
                    # Calculate similarity with previous frame
                    similarity = self.calculate_similarity(prev_frame, frame)
                    
                    # If significant change detected
                    if similarity < self.similarity_threshold:
                        # Calculate similarity with all recent steps to avoid duplicates
                        is_unique = True
                        for recent_step in steps[-3:]:  # Check last 3 steps
                            if self.calculate_similarity(recent_step.screenshot, frame) > self.similarity_threshold:
                                is_unique = False
                                break
                                
                        if is_unique:
                            steps.append(Step(
                                timestamp=current_timestamp,
                                screenshot=frame.copy(),
                                similarity_score=similarity
                            ))
                            prev_timestamp = current_timestamp
            
            prev_frame = frame.copy()
            frame_idx += 1
            
        cap.release()
        
        # Filter out steps that are too similar to their neighbors
        filtered_steps = []
        for i, step in enumerate(steps):
            if i == 0 or i == len(steps) - 1:  # Keep first and last steps
                filtered_steps.append(step)
            else:
                # Check if this step is significantly different from both neighbors
                prev_similarity = self.calculate_similarity(steps[i-1].screenshot, step.screenshot)
                next_similarity = self.calculate_similarity(step.screenshot, steps[i+1].screenshot)
                if prev_similarity < self.similarity_threshold and next_similarity < self.similarity_threshold:
                    filtered_steps.append(step)
        
        return filtered_steps
        
    def save_screenshots(self, steps: List[Step], output_dir: str) -> Dict[int, str]:
        """Save screenshots for each detected step.
        
        Args:
            steps (List[Step]): List of detected steps
            output_dir (str): Directory to save screenshots
            
        Returns:
            Dict[int, str]: Dictionary mapping step index to screenshot path
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        screenshot_paths = {}
        for idx, step in enumerate(steps):
            timestamp = datetime.fromtimestamp(step.timestamp).strftime("%Y%m%d_%H%M%S")
            output_path = str(output_dir / f"step_{idx}_{timestamp}.png")
            cv2.imwrite(output_path, step.screenshot)
            screenshot_paths[idx] = output_path
            
        return screenshot_paths
