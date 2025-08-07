# CV Builder

Generate HTML and PDF resumes from JSON data using Jinja2 templates.

## Usage

### Generate single resume
```bash
python3 cvbuilder.py -i resume.json -t template.html -o output/
```

### Generate samples for all templates
```bash
# Generate samples for all configs and all templates
python3 generate_samples.py

# Generate samples for specific config with all templates
python3 generate_samples.py sample/johndoe.json
python3 generate_samples.py sample/maryann.json
python3 generate_samples.py /path/to/custom.json
```

## Resume Structure

### Sections Concept
Resumes are organized into **sections** - flexible containers for different types of information. Each section has:
- **id**: Used for ordering sections in the resume (e.g., "00", "01", "02")
- **label**: Display name shown in the resume (e.g., "Education", "Experience", "Skills")
- **content**: Array of items within that section

Common section types:
- **Education**: Schools, degrees, courses
- **Experience**: Jobs, internships, roles with achievements
- **Skills**: Technical skills, programming languages, tools
- **Projects**: Personal or academic projects with descriptions

### Sample Configuration Files

The `sample/` directory contains example configurations (`johndoe.json`, `maryann.json`) demonstrating different career stages and section structures.

## Examples

### Generate Resumes

```bash
# Generate experienced professional resume
python3 cvbuilder.py -i sample/johndoe.json -t template/template_1.html

# Generate fresh graduate resume
python3 cvbuilder.py -i sample/maryann.json -t template/template_2.html

# Generate with specific output directory
python3 cvbuilder.py -i sample/johndoe.json -t template/template_1.html -o ./output

# Generate samples for all configs and all templates  
python3 generate_samples.py

# Generate samples for specific config with all templates
python3 generate_samples.py sample/johndoe.json
python3 generate_samples.py sample/maryann.json
```

### JSON Structure
```json
{
  "name": "Full Name",
  "summary": "Professional summary...",
  "contact_info": [
    {"type": "email", "info": "email@example.com"},
    {"type": "link", "info": "github.com/username"},
    {"type": "text", "info": "City, State"}
  ],
  "sections": [
    {
      "id": "01",
      "label": "Experience",
      "content": [
        {
          "name": "Company Name",
          "period": "01/2023 - Present",
          "title": "Job Title",
          "bullets": ["Achievement 1", "Achievement 2"]
        }
      ]
    }
  ]
}
```

**Required fields:** `name`, `contact_info`, `sections`  
**Optional fields:** `summary`, `period`, `title`, `bullets` (within content items)

## Requirements

```bash
pip3 install jinja2 jsonschema weasyprint
```

## Output

- `name_resume.html` - HTML version
- `name_resume.pdf` - PDF version (requires WeasyPrint)

## TODO

- [ ] Add a way to customize template styling (font, paragraph spacing, colors, etc.)