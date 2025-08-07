#!/usr/bin/env python3

import json
import sys
import argparse
import tempfile
import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from jsonschema import validate, ValidationError

try:
    import weasyprint
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# JSON Schema for resume data validation
RESUME_SCHEMA = {
    "type": "object",
    "required": ["name", "contact_info", "sections"],
    "properties": {
        "name": {"type": "string", "minLength": 1},
        "summary": {"type": "string"},
        "contact_info": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["type", "info"],
                "properties": {
                    "type": {"type": "string", "enum": ["text", "email", "link"]},
                    "info": {"type": "string", "minLength": 1}
                }
            }
        },
        "sections": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "label", "content"],
                "properties": {
                    "id": {"type": "string"},
                    "label": {"type": "string", "minLength": 1},
                    "content": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["name"],
                            "properties": {
                                "name": {"type": "string", "minLength": 1},
                                "period": {"type": "string"},
                                "title": {"type": "string"},
                                "bullets": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                }
                            },
                            "additionalProperties": False
                        }
                    }
                }
            }
        }
    }
}

def validate_file_path(file_path, file_type="file"):
    """Validate that a file path exists and is accessible"""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"{file_type.capitalize()} not found: {file_path}")
    if not path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")
    return path

def load_and_validate_json(json_path):
    """Load JSON file and validate against schema"""
    try:
        path = validate_file_path(json_path, "JSON file")
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validate against schema
        validate(instance=data, schema=RESUME_SCHEMA)
        
        print(f"✓ JSON loaded and validated: {len(data.get('sections', []))} sections found")
        return data
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format in {json_path}: {e}")
    except ValidationError as e:
        raise ValueError(f"Invalid resume data structure: {e.message}")

def load_template(template_path):
    """Load and prepare Jinja2 template with security settings"""
    try:
        template_file = validate_file_path(template_path, "template file")
        
        # Create secure Jinja2 environment with autoescape enabled
        env = Environment(
            loader=FileSystemLoader(template_file.parent),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        template = env.get_template(template_file.name)
        print(f"✓ Template loaded: {template_path}")
        return template
        
    except Exception as e:
        raise ValueError(f"Failed to load template {template_path}: {e}")

def generate_pdf(html_path, pdf_path=None):
    """Generate PDF from HTML file using WeasyPrint"""
    if not PDF_AVAILABLE:
        raise ImportError(
            "WeasyPrint is required for PDF generation. Install with: pip install weasyprint"
        )
    
    try:
        # Determine output path
        if pdf_path is None:
            html_file = Path(html_path)
            pdf_path = html_file.with_suffix('.pdf')
        
        pdf_file = Path(pdf_path)
        
        # Generate PDF
        weasyprint.HTML(filename=html_path).write_pdf(pdf_file)
        
        print(f"✓ PDF resume generated: {pdf_file.absolute()}")
        return str(pdf_file.absolute())
        
    except Exception as e:
        raise ValueError(f"Failed to generate PDF: {e}")

def generate_resume(json_path, template_path, output_dir=None):
    """Generate both HTML and PDF resume from JSON data and template"""
    try:
        # Load and validate data
        data = load_and_validate_json(json_path)
        
        # Sort sections by ID for consistent ordering
        data['sections'] = sorted(data['sections'], key=lambda x: x.get('id', ''))
        
        # Load template
        template = load_template(template_path)
        
        # Render HTML with data
        html_content = template.render(**data)
        
        # Determine output directory and base filename
        if output_dir is None:
            output_dir = Path.cwd()
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        
        base_filename = Path(json_path).stem + '_resume'
        html_path = output_dir / f"{base_filename}.html"
        pdf_path = output_dir / f"{base_filename}.pdf"
        
        # Write HTML file
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✓ HTML resume generated: {html_path.absolute()}")
        
        # Generate PDF
        if PDF_AVAILABLE:
            try:
                weasyprint.HTML(filename=str(html_path)).write_pdf(str(pdf_path))
                print(f"✓ PDF resume generated: {pdf_path.absolute()}")
            except Exception as e:
                print(f"⚠ PDF generation failed: {e}", file=sys.stderr)
        else:
            print(f"⚠ PDF generation skipped: WeasyPrint not available. Install with: pip install weasyprint", file=sys.stderr)
        
        return {
            'html': str(html_path.absolute()),
            'pdf': str(pdf_path.absolute()) if PDF_AVAILABLE else None
        }
        
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description='Generate HTML and PDF resumes from JSON data using Jinja2 templates',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -i resume.json -t template.html
  %(prog)s -i resume.json -t template.html -o ./output
  %(prog)s -i resume.json -t template.html -o /path/to/output/dir
        """
    )
    
    parser.add_argument('-i', '--input', required=True,
                        help='Path to JSON resume data file')
    parser.add_argument('-t', '--template', required=True,
                        help='Path to HTML template file')
    parser.add_argument('-o', '--output', 
                        help='Output directory path (optional, defaults to current directory)')
    
    args = parser.parse_args()
    
    # Generate both HTML and PDF
    generate_resume(args.input, args.template, args.output)

if __name__ == "__main__":
    main()