import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
from typing import List, Dict
from PIL import Image
import google.generativeai as genai
from fpdf import FPDF
from io import BytesIO
import markdown
import pdfkit
import time
import re
from .step_detector import Step

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        self.add_page()
        self.set_font('Arial', 'B', 24)
        
    def header(self):
        # Add logo if exists
        logo_path = Path("assets/logo.png")
        if logo_path.exists():
            self.image(str(logo_path), 10, 8, 33)
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'ScreenDoc Documentation', 0, 1, 'R')
        self.ln(10)
        
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
        
    def chapter_title(self, title):
        self.set_font('Arial', 'B', 20)
        self.set_fill_color(240, 240, 240)
        self.cell(0, 15, title, 0, 1, 'L', True)
        self.ln(10)
        
    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, body)
        self.ln()
        
    def add_step(self, number: int, description: str, image_path: str = None):
        # Step header
        self.set_font('Arial', 'B', 14)
        self.set_fill_color(230, 230, 230)
        self.cell(0, 10, f'Step {number}', 0, 1, 'L', True)
        self.ln(5)
        
        # Step description
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 8, description)
        self.ln(5)
        
        # Step image
        if image_path and Path(image_path).exists():
            # Calculate image dimensions to fit page width while maintaining aspect ratio
            page_width = self.w - 40  # 20mm margins on each side
            img = Image.open(image_path)
            width, height = img.size
            aspect = height / width
            
            img_width = page_width
            img_height = page_width * aspect
            
            # Add a new page if the image won't fit
            if self.get_y() + img_height + 20 > self.h:
                self.add_page()
            
            # Center the image
            x = (self.w - img_width) / 2
            self.image(image_path, x, self.get_y(), img_width)
            self.ln(img_height + 10)

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
        
    def generate_step_description(self, screenshot_path: str, prev_screenshot: str = None) -> str:
        """Generate a description for a step using the Gemini Vision API.
        
        Args:
            screenshot_path (str): Path to the screenshot
            prev_screenshot (str): Path to previous screenshot for context
            
        Returns:
            str: Generated description
        """
        try:
            # Load current screenshot
            with open(screenshot_path, 'rb') as img_file:
                try:
                  current_image_data = Image.open(BytesIO(img_file.read()))
                except Exception as e:
                    print(f"Error opening image: {e}")
            # Load previous screenshot if available
            prev_image_data = None
            if prev_screenshot and Path(prev_screenshot).exists():
                with open(prev_screenshot, 'rb') as img_file:
                    try:
                      prev_image_data = Image.open(BytesIO(img_file.read()))
                    except Exception as e:
                      print(f"Error opening image: {e}")
            
            # Create prompt based on context
            if prev_image_data:
                prompt = """Analyze these two consecutive screenshots from a process documentation and:
1. Describe what changed between the previous and current screen
2. Explain the user's action that likely caused this change
3. Identify any important UI elements or data that were modified
4. Note any system responses or feedback shown
5. Highlight any potential dependencies or prerequisites for this step

Focus on being specific and actionable. Use clear, professional language.
Previous screenshot shows the starting state, current screenshot shows the result."""
            else:
                prompt = """Analyze this screenshot from a process documentation and:
1. Describe the current state of the application/screen
2. Identify key UI elements and their purpose
3. Note any important data or settings shown
4. Highlight any system status or feedback messages
5. Suggest what actions might be available or required

Focus on being specific and actionable. Use clear, professional language ."""

            # Add retry logic with exponential backoff
            max_retries = self.max_retries
            delay = 1.0
            
            for attempt in range(max_retries):
                try:
                    if prev_image_data:
                        response = self.model.generate_content([
                            prompt,
                            prev_image_data,
                            current_image_data
                        ])
                    else:
                        response = self.model.generate_content([
                            prompt,
                            current_image_data
                        ])
                    
                    # Process and format the response
                    description = response.text.strip()
                    
                    # Post-process the description
                    description = self._enhance_description(description)
                    
                    time.sleep(self.request_delay)  # Rate limiting
                    return description
                    
                except Exception as e:
                    if attempt == max_retries - 1:
                        print(f"Error generating description after {max_retries} attempts: {str(e)}")
                        return f"Error generating description: {str(e)}"
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
            
        except Exception as e:
            print(f"Error processing screenshots: {str(e)}")
            return f"Error processing screenshots: {str(e)}"
            
    def _enhance_description(self, description: str) -> str:
        """Enhance the generated description with additional context and formatting.
        
        Args:
            description (str): Raw generated description
            
        Returns:
            str: Enhanced description
        """
        # Split description into paragraphs
        paragraphs = description.split('\n\n')
        
        # Process each paragraph
        enhanced_paragraphs = []
        for para in paragraphs:
            # Clean up formatting
            para = para.strip()
            
            # Convert bullet points to proper markdown
            if para.startswith('•'):
                para = '- ' + para[1:].strip()
            elif para.startswith('* '):
                para = '- ' + para[2:].strip()
                
            # Highlight important terms
            para = re.sub(r'(button|menu|dialog|window|panel|screen|field|input|output)',
                         r'**\1**', para, flags=re.IGNORECASE)
                         
            # Add paragraph to list
            if para:
                enhanced_paragraphs.append(para)
                
        # Join paragraphs with proper spacing
        enhanced_description = '\n\n'.join(enhanced_paragraphs)
        
        # Add context markers if they don't exist
        if not any(marker in enhanced_description.lower() 
                  for marker in ['result:', 'outcome:', 'effect:', 'change:']):
            enhanced_description += "\n\n**Result:** " + self._generate_result_summary(enhanced_description)
            
        return enhanced_description
        
    def _generate_result_summary(self, description: str) -> str:
        """Generate a summary of the step's result based on the description.
        
        Args:
            description (str): Step description
            
        Returns:
            str: Result summary
        """
        try:
            prompt = f"""Based on this step description, provide a one-sentence summary of the result or outcome:

{description}

Focus on the concrete change or achievement, not the process."""

            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error generating result summary: {str(e)}")
            return "Step completed successfully."
            
    def _link_steps(self, steps: List[Step]) -> List[Step]:
        """Add contextual links between steps.
        
        Args:
            steps (List[Step]): List of steps to process
            
        Returns:
            List[Step]: Steps with added context links
        """
        for i, step in enumerate(steps):
            if not hasattr(step, 'description') or not step.description:
                continue
                
            # Add context from previous step if available
            if i > 0 and hasattr(steps[i-1], 'description') and steps[i-1].description:
                context = self._generate_step_context(steps[i-1].description, step.description)
                if context:
                    step.description = f"{context}\n\n{step.description}"
                    
        return steps
        
    def _generate_step_context(self, prev_desc: str, curr_desc: str) -> str:
        """Generate contextual link between steps.
        
        Args:
            prev_desc (str): Previous step description
            curr_desc (str): Current step description
            
        Returns:
            str: Contextual link text
        """
        try:
            prompt = f"""Given these two consecutive steps in a process, create a one-sentence transition that shows how they are related:

Previous Step:
{prev_desc}

Current Step:
{curr_desc}

Focus on cause-and-effect or sequential relationship. Be concise and professional."""

            response = self.model.generate_content(prompt)
            return f"*Context: {response.text.strip()}*"
        except Exception as e:
            print(f"Error generating step context: {str(e)}")
            return ""
            
    def generate_documentation(self, steps: List[Step], screenshot_paths: Dict[int, str], 
                             output_format: str = "pdf", template: str = "default") -> str:
        """Generate documentation from detected steps."""
        # Generate descriptions for steps
        for i, step in enumerate(steps):
            if i in screenshot_paths:
                prev_screenshot = screenshot_paths.get(i-1) if i > 0 else None
                step.description = self.generate_step_description(
                    screenshot_paths[i],
                    prev_screenshot
                )
        
        # Add contextual links between steps
        steps = self._link_steps(steps)
        
        # Generate documentation in requested format
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if output_format.lower() == "pdf":
            return self._generate_pdf(steps, screenshot_paths, template, timestamp)
        elif output_format.lower() == "html":
            return self._generate_html(steps, screenshot_paths, template, timestamp)
        else:  # markdown
            return self._generate_markdown(steps, screenshot_paths, template, timestamp)
    
    def _generate_pdf(self, steps: List[Step], screenshot_paths: Dict[int, str], 
                     template: str, timestamp: str) -> str:
        """Generate PDF documentation."""
        output_path = f"documentation_{timestamp}.pdf"
        
        # Initialize PDF with custom class
        pdf = PDF()
        
        # Add title page
        pdf.set_font('Arial', 'B', 24)
        pdf.cell(0, 60, 'Process Documentation', 0, 1, 'C')
        pdf.set_font('Arial', '', 14)
        pdf.cell(0, 10, f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1, 'C')
        pdf.add_page()
        
        # Add table of contents
        pdf.chapter_title('Table of Contents')
        for i, _ in enumerate(steps, 1):
            pdf.cell(0, 10, f'Step {i}', 0, 1)
        pdf.add_page()
        
        # Add steps
        pdf.chapter_title('Process Steps')
        for i, step in enumerate(steps, 1):
            image_path = screenshot_paths.get(i-1)
            description = step.description if hasattr(step, 'description') and step.description else f"Step {i}"
            #description = f"Step {i}"
            pdf.add_step(i, description, image_path)
        
        # Save the PDF
        pdf.output(output_path)
        return output_path
    
    def _generate_html(self, steps: List[Step], screenshot_paths: Dict[int, str], 
                      template: str, timestamp: str) -> str:
        """Generate HTML documentation."""
        output_path = f"documentation_{timestamp}.html"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Process Documentation</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .header {{
                    text-align: center;
                    padding: 20px;
                    background-color: #fff;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    margin-bottom: 30px;
                }}
                .step {{
                    background-color: #fff;
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 30px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .step-number {{
                    font-size: 24px;
                    color: #333;
                    margin-bottom: 15px;
                }}
                .step-description {{
                    color: #666;
                    margin-bottom: 20px;
                }}
                .step-image {{
                    max-width: 100%;
                    height: auto;
                    border-radius: 4px;
                    margin-top: 15px;
                }}
                .toc {{
                    background-color: #fff;
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 30px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .toc-title {{
                    font-size: 20px;
                    margin-bottom: 15px;
                }}
                .toc-item {{
                    margin: 8px 0;
                }}
                @media print {{
                    body {{
                        background-color: #fff;
                    }}
                    .step {{
                        break-inside: avoid;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Process Documentation</h1>
                <p>Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </div>
            
            <div class="toc">
                <div class="toc-title">Table of Contents</div>
                {"".join(f'<div class="toc-item"><a href="#step-{i}">Step {i}</a></div>' for i in range(1, len(steps) + 1))}
            </div>
        """
        
        for i, step in enumerate(steps, 1):
            description = step.description if hasattr(step, 'description') and step.description else f"Step {i}"
            image_path = screenshot_paths.get(i-1, "")
            
            html_content += f"""
            <div class="step" id="step-{i}">
                <div class="step-number">Step {i}</div>
                <div class="step-description">{description}</div>
                {"<img class='step-image' src='" + image_path + "' alt='Step " + str(i) + "'>" if image_path else ""}
            </div>
            """
        
        html_content += """
        </body>
        </html>
        """
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        return output_path
    
    def _generate_markdown(self, steps: List[Step], screenshot_paths: Dict[int, str], 
                         template: str, timestamp: str) -> str:
        """Generate markdown documentation."""
        output_path = f"documentation_{timestamp}.md"
        
        content = f"""# Process Documentation
Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Table of Contents
{"".join(f'- [Step {i}](#step-{i})\n' for i in range(1, len(steps) + 1))}

## Steps
"""
        
        for i, step in enumerate(steps, 1):
            description = step.description if hasattr(step, 'description') and step.description else f"Step {i}"
            image_path = screenshot_paths.get(i-1, "")
            
            content += f"""
### Step {i}
{description}

{"![Step " + str(i) + "](" + image_path + ")" if image_path else ""}

---
"""
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        return output_path
