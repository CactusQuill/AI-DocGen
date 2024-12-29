import os
import json
import time
import base64
from PIL import Image
import google.generativeai as genai
from pathlib import Path
from typing import List, Dict
from datetime import datetime
from dotenv import load_dotenv
from .step_detector import Step

class DocumentationGenerator:
    def __init__(self):
        """Initialize the documentation generator."""
        load_dotenv()
        
        # Configure Gemini API
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel(os.getenv("MODEL_NAME", "gemini-vision-1.5"))
        
        # Rate limiting parameters
        self.request_delay = 2.0  # Delay between requests in seconds
        self.max_retries = 3
        
    def generate_step_description(self, screenshot_path: str, prev_screenshot_path: str = None) -> str:
        """Generate description for a step using Google's Gemini Vision API.
        
        Args:
            screenshot_path (str): Path to the step screenshot
            prev_screenshot_path (str): Path to the previous screenshot (optional)
            
        Returns:
            str: Generated description
        """
        try:
            # Load the current screenshot
            current_image = Image.open(screenshot_path)
            # Convert image to RGB mode if it's not already
            if current_image.mode != 'RGB':
                current_image = current_image.convert('RGB')
            
            if prev_screenshot_path:
                # Load the previous screenshot for comparison
                prev_image = Image.open(prev_screenshot_path)
                if prev_image.mode != 'RGB':
                    prev_image = prev_image.convert('RGB')
                
                prompt = """
                You are analyzing two consecutive screenshots from a workflow recording.
                Compare them and describe what changed or what action was taken.
                Focus on significant UI interactions, content changes, or system responses.
                Be concise but specific about what happened in this step.
                The first image is the previous state, and the second image is the current state.
                """
                
                try:
                    response = self.model.generate_content([
                        prompt,
                        prev_image,
                        current_image
                    ])
                except Exception as e:
                    print(f"Error with comparison analysis: {str(e)}")
                    # Fallback to single image analysis
                    return self.generate_step_description(screenshot_path)
            else:
                prompt = """
                You are analyzing a screenshot from a workflow recording.
                Describe what is shown in this screenshot and what it represents in the workflow.
                Focus on significant UI elements, content, or system state.
                Be concise but specific about what this step shows.
                """
                
                response = self.model.generate_content([
                    prompt,
                    current_image
                ])
            
            # Add delay for rate limiting
            time.sleep(self.request_delay)
            
            if hasattr(response, 'text') and response.text:
                return response.text.strip()
            elif hasattr(response, 'parts'):
                return ' '.join([part.text for part in response.parts]).strip()
            else:
                return f"Step {Path(screenshot_path).stem}"
                
        except Exception as e:
            print(f"Error generating description: {str(e)}")
            return f"Step {Path(screenshot_path).stem}"
            
    def generate_documentation(self, steps: List[Step], screenshot_paths: Dict[int, str], 
                             output_format: str = "markdown") -> str:
        """Generate documentation from detected steps.
        
        Args:
            steps (List[Step]): List of detected steps
            screenshot_paths (Dict[int, str]): Dictionary mapping step indices to screenshot paths
            output_format (str): Output format (markdown/html/pdf)
            
        Returns:
            str: Path to generated documentation
        """
        print(f"\nGenerating descriptions for {len(steps)} steps...")
        
        # Generate descriptions for each step
        for idx, step in enumerate(steps):
            if idx in screenshot_paths:
                print(f"Processing step {idx + 1}/{len(steps)}...")
                
                # Get previous screenshot path if available
                prev_screenshot = screenshot_paths.get(idx - 1) if idx > 0 else None
                
                step.description = self.generate_step_description(
                    screenshot_paths[idx],
                    prev_screenshot
                )
                
        # Create documentation based on format
        if output_format.lower() == "markdown":
            return self._generate_markdown(steps, screenshot_paths)
        elif output_format.lower() == "html":
            return self._generate_html(steps, screenshot_paths)
        elif output_format.lower() == "pdf":
            return self._generate_pdf(steps, screenshot_paths)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
            
    def _generate_markdown(self, steps: List[Step], screenshot_paths: Dict[int, str]) -> str:
        """Generate markdown documentation.
        
        Args:
            steps (List[Step]): List of detected steps
            screenshot_paths (Dict[int, str]): Dictionary mapping step indices to screenshot paths
            
        Returns:
            str: Path to generated markdown file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"documentation_{timestamp}.md"
        
        with open(output_path, "w") as f:
            f.write("# Automated Documentation\n\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for idx, step in enumerate(steps):
                f.write(f"## Step {idx + 1}\n\n")
                if idx in screenshot_paths:
                    f.write(f"![Step {idx + 1}]({screenshot_paths[idx]})\n\n")
                f.write(f"{step.description}\n\n")
                
        return output_path
        
    def _generate_html(self, steps: List[Step], screenshot_paths: Dict[int, str]) -> str:
        """Generate HTML documentation."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"documentation_{timestamp}.html"
        
        with open(output_path, "w") as f:
            f.write("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Automated Documentation</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    img { max-width: 100%; height: auto; }
                    .step { margin-bottom: 40px; }
                </style>
            </head>
            <body>
            """)
            
            f.write("<h1>Automated Documentation</h1>")
            f.write(f"<p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>")
            
            for idx, step in enumerate(steps):
                f.write(f'<div class="step">')
                f.write(f"<h2>Step {idx + 1}</h2>")
                if idx in screenshot_paths:
                    f.write(f'<img src="{screenshot_paths[idx]}" alt="Step {idx + 1}">')
                f.write(f"<p>{step.description}</p>")
                f.write("</div>")
                
            f.write("</body></html>")
            
        return output_path
        
    def _generate_pdf(self, steps: List[Step], screenshot_paths: Dict[int, str]) -> str:
        """Generate PDF documentation."""
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib.utils import ImageReader
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"documentation_{timestamp}.pdf"
        
        c = canvas.Canvas(output_path, pagesize=letter)
        width, height = letter
        
        # Title
        c.setFont("Helvetica-Bold", 24)
        c.drawString(72, height - 72, "Automated Documentation")
        
        # Generation timestamp
        c.setFont("Helvetica", 12)
        c.drawString(72, height - 100, 
                    f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        y_position = height - 150
        
        for idx, step in enumerate(steps):
            if y_position < 100:  # Start new page if not enough space
                c.showPage()
                y_position = height - 72
                
            # Step header
            c.setFont("Helvetica-Bold", 16)
            c.drawString(72, y_position, f"Step {idx + 1}")
            y_position -= 30
            
            # Screenshot
            if idx in screenshot_paths:
                img = ImageReader(screenshot_paths[idx])
                img_width, img_height = img.getSize()
                aspect = img_height / float(img_width)
                
                # Scale image to fit page width while maintaining aspect ratio
                scaled_width = width - 144  # 72 points margin on each side
                scaled_height = scaled_width * aspect
                
                c.drawImage(img, 72, y_position - scaled_height, 
                          width=scaled_width, height=scaled_height)
                y_position -= scaled_height + 20
                
            # Description
            c.setFont("Helvetica", 12)
            text = step.description
            for line in text.split('\n'):
                if y_position < 100:  # Start new page if not enough space
                    c.showPage()
                    y_position = height - 72
                c.drawString(72, y_position, line)
                y_position -= 15
                
            y_position -= 30  # Space between steps
            
        c.save()
        return output_path
