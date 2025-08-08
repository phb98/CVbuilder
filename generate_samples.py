#!/usr/bin/env python3

import argparse
import os
import sys
import subprocess
from pathlib import Path
from cvbuilder import generate_resume

def is_chromium_available():
    """Check if Chromium is available on the system"""
    try:
        result = subprocess.run(['chromium', '--version'], capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        return False

def capture_screenshot(html_path, output_path):
    """Capture a screenshot of the HTML file using Chromium headless"""
    try:
        # Use chromium in headless mode to capture a screenshot
        cmd = [
            'chromium',
            '--headless',
            '--disable-gpu',
            '--window-size=1200,1600',
            '--screenshot=' + str(output_path),
            'file://' + str(html_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"    Screenshot: {Path(output_path).name}")
            return str(output_path)
        else:
            print(f"    ⚠ Screenshot failed: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        print(f"    ⚠ Screenshot timeout for {html_path}")
        return None
    except Exception as e:
        print(f"    ⚠ Screenshot error: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(
        description='Generate resume samples for all templates, optionally for a specific config',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              # Generate samples for all configs and all templates
  %(prog)s sample/johndoe.json         # Generate samples for johndoe config with all templates
  %(prog)s sample/maryann.json         # Generate samples for maryann config with all templates
  %(prog)s /path/to/myresume.json      # Generate samples for custom config with all templates
        """
    )
    
    parser.add_argument('config', nargs='?', 
                        help='Path to JSON config file. If not provided, generates for all configs in sample/ directory.')
    
    args = parser.parse_args()
    
    # Define paths
    base_dir = Path(__file__).parent
    sample_dir = base_dir / "sample"
    template_dir = base_dir / "template"
    output_dir = sample_dir / "output"
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all template files
    template_files = list(template_dir.glob("*.html"))
    
    if not template_files:
        print("No template files found in template directory")
        sys.exit(1)
    
    # Determine which sample data files to process
    if args.config:
        # Process specific config file path
        specific_config = Path(args.config)
        if not specific_config.exists():
            print(f"Config file not found: {specific_config}")
            sys.exit(1)
        if not specific_config.is_file():
            print(f"Path is not a file: {specific_config}")
            sys.exit(1)
        if specific_config.suffix != '.json':
            print(f"Config file must be a JSON file: {specific_config}")
            sys.exit(1)
        sample_data_files = [specific_config]
        print(f"Processing specific config: {specific_config}")
    else:
        # Process all configs in sample directory
        sample_data_files = list(sample_dir.glob("*.json"))
        if not sample_data_files:
            print("No sample data files found in sample directory")
            sys.exit(1)
        print(f"Processing all configs in sample/ directory")
    
    # Check if Chromium is available for screenshots
    chromium_available = is_chromium_available()
    if chromium_available:
        print("✓ Chromium available - screenshots will be generated")
    else:
        print("⚠ Chromium not available - screenshots will be skipped")
    
    print(f"Found {len(template_files)} template(s)")
    print(f"Found {len(sample_data_files)} sample data file(s)")
    print(f"Output directory: {output_dir}")
    print()
    
    # Generate sample for each combination of template and sample data
    for sample_data in sorted(sample_data_files):
        sample_name = sample_data.stem  # e.g., "johndoe", "maryann"
        print(f"Processing {sample_name}...")
        
        for template_file in sorted(template_files):
            template_name = template_file.stem  # e.g., "template_1"
            print(f"  Generating {sample_name} with {template_name}...")
            
            try:
                # Create a temporary file with the desired output name format
                temp_data_name = f"{sample_name}_{template_name}.json"
                temp_data_path = sample_data.parent / temp_data_name
                
                # Copy the content to temporary file
                import shutil
                shutil.copy2(sample_data, temp_data_path)
                
                # Generate the resume
                result = generate_resume(
                    json_path=str(temp_data_path),
                    template_path=str(template_file),
                    output_dir=str(output_dir)
                )
                
                # Clean up temporary file
                temp_data_path.unlink()
                
                print(f"  ✓ Generated {sample_name}_{template_name}")
                if result.get('html'):
                    print(f"    HTML: {Path(result['html']).name}")
                    
                    # Capture screenshot for each template (only if Chromium is available)
                    if chromium_available:
                        html_path = Path(result['html'])
                        screenshot_path = html_path.with_suffix('.png')
                        capture_screenshot(html_path, screenshot_path)
                    
                if result.get('pdf'):
                    print(f"    PDF: {Path(result['pdf']).name}")
                
            except Exception as e:
                print(f"  ✗ Failed to generate {sample_name}_{template_name}: {e}")
        
        print()

if __name__ == "__main__":
    main()