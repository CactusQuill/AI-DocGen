import argparse
from pathlib import Path
from screendoc import ScreenRecorder, StepDetector, DocumentationGenerator

def main():
    parser = argparse.ArgumentParser(description="Automated Documentation Generator")
    parser.add_argument("--output-dir", type=str, default="output",
                       help="Directory to save output files")
    parser.add_argument("--format", type=str, choices=["markdown", "html", "pdf"],
                       default="markdown", help="Output documentation format")
    parser.add_argument("--monitor", type=int, default=1,
                       help="Monitor number to record (default: 1)")
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize components
    recorder = ScreenRecorder(str(output_dir / "recordings"))
    detector = StepDetector()
    generator = DocumentationGenerator()
    
    try:
        print("Starting screen recording... Press Ctrl+C to stop.")
        recorder.start_recording(args.monitor)
    except KeyboardInterrupt:
        print("\nStopping recording...")
        video_path, timestamps = recorder.stop_recording()
        
        if video_path:
            print(f"\nRecording saved to: {video_path}")
            print("Detecting steps...")
            steps = detector.detect_steps(video_path, timestamps)
            
            print(f"Detected {len(steps)} steps")
            print("Saving screenshots...")
            screenshot_paths = detector.save_screenshots(steps, str(output_dir / "screenshots"))
            
            print("Generating documentation...")
            doc_path = generator.generate_documentation(steps, screenshot_paths, args.format)
            print(f"\nDocumentation generated: {doc_path}")
            
if __name__ == "__main__":
    main()
