"""
MOM Template Manager
Allows customization of MOM generation templates
"""

import json
import os
from pathlib import Path


class MOMTemplateManager:
    """Manages MOM generation templates"""
    
    TEMPLATES_FILE = "mom_templates.json"
    
    DEFAULT_TEMPLATES = {
        "standard": {
            "name": "Standard MOM",
            "description": "Comprehensive minutes with all sections",
            "prompt": """Based on the following meeting transcript, generate comprehensive Minutes of Meeting (MOM) including:
1. Key Discussion Points - Main topics discussed
2. Action Items - Tasks with owners and deadlines
3. Decisions Made - Important conclusions reached
4. Next Steps - Follow-up activities
5. Attendees Summary - Who participated

Meeting Transcript:
{transcript}

Please format the MOM in a clear, structured way with proper sections."""
        },
        "executive": {
            "name": "Executive Summary",
            "description": "Brief high-level summary (1-2 pages max)",
            "prompt": """Create a brief executive summary of this meeting in 2-3 paragraphs maximum:

Meeting Transcript:
{transcript}

Focus on:
- Key decisions made
- Critical action items
- Business impact"""
        },
        "technical": {
            "name": "Technical Discussion",
            "description": "Detailed technical meeting minutes",
            "prompt": """Generate detailed technical meeting minutes from this transcript:

Meeting Transcript:
{transcript}

Include:
1. Technical Topics Discussed
2. Architecture/Design Decisions
3. Code/System Changes
4. Performance Considerations
5. Outstanding Technical Issues
6. Technical Action Items with owners"""
        },
        "agile": {
            "name": "Agile Standup",
            "description": "Agile standup format minutes",
            "prompt": """Format this meeting as Agile standup minutes:

Meeting Transcript:
{transcript}

Use this format:
- Yesterday Accomplished
- Today's Plan
- Blockers/Issues
- Team Members Present
- Sprint Context if applicable"""
        },
        "client": {
            "name": "Client Meeting",
            "description": "Client-facing meeting format",
            "prompt": """Generate client-appropriate meeting minutes:

Meeting Transcript:
{transcript}

Include:
1. Meeting Objective
2. Key Discussion Points
3. Client Concerns/Feedback
4. Proposed Solutions
5. Deliverables & Timeline
6. Next Steps & Follow-up Items
7. Decision Items

Keep professional tone, avoid internal jargon."""
        },
        "legal": {
            "name": "Legal/Compliance",
            "description": "Formal legal/compliance meeting minutes",
            "prompt": """Generate formal legal meeting minutes:

Meeting Transcript:
{transcript}

Required sections:
- Meeting Date, Time, Location
- Attendees (with titles)
- Agenda Items Discussed
- Agreements Reached
- Legal Commitments Made
- Compliance Items Addressed
- Follow-up Requirements
- Next Review Date
- Certified by (attach signature)"""
        }
    }
    
    @classmethod
    def initialize_templates(cls):
        """Initialize templates file with defaults"""
        if not os.path.exists(cls.TEMPLATES_FILE):
            cls.save_templates(cls.DEFAULT_TEMPLATES)
            print(f"Created {cls.TEMPLATES_FILE} with default templates")
            return True
        return False
    
    @classmethod
    def load_templates(cls) -> dict:
        """Load templates from file"""
        cls.initialize_templates()
        
        try:
            with open(cls.TEMPLATES_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading templates: {str(e)}")
            return cls.DEFAULT_TEMPLATES
    
    @classmethod
    def save_templates(cls, templates: dict):
        """Save templates to file"""
        try:
            with open(cls.TEMPLATES_FILE, 'w') as f:
                json.dump(templates, f, indent=2)
            print(f"Templates saved to {cls.TEMPLATES_FILE}")
        except Exception as e:
            print(f"Error saving templates: {str(e)}")
    
    @classmethod
    def get_template(cls, template_name: str) -> dict:
        """Get a specific template"""
        templates = cls.load_templates()
        if template_name not in templates:
            print(f"Template '{template_name}' not found")
            print(f"Available templates: {', '.join(templates.keys())}")
            return None
        return templates[template_name]
    
    @classmethod
    def list_templates(cls):
        """List all available templates"""
        templates = cls.load_templates()
        
        print("\nAvailable MOM Templates:")
        print("-" * 60)
        
        for name, template in templates.items():
            print(f"\n{name.upper()}")
            print(f"  Name: {template.get('name', 'N/A')}")
            print(f"  Description: {template.get('description', 'N/A')}")
        
        print("\n" + "-" * 60)
    
    @classmethod
    def add_template(cls, name: str, title: str, description: str, prompt: str):
        """Add a new custom template"""
        templates = cls.load_templates()
        
        if name in templates:
            print(f"Template '{name}' already exists. Use update to modify.")
            return False
        
        templates[name] = {
            "name": title,
            "description": description,
            "prompt": prompt
        }
        
        cls.save_templates(templates)
        print(f"Template '{name}' created successfully")
        return True
    
    @classmethod
    def update_template(cls, name: str, **kwargs):
        """Update an existing template"""
        templates = cls.load_templates()
        
        if name not in templates:
            print(f"Template '{name}' not found")
            return False
        
        template = templates[name]
        
        if 'title' in kwargs:
            template['name'] = kwargs['title']
        if 'description' in kwargs:
            template['description'] = kwargs['description']
        if 'prompt' in kwargs:
            template['prompt'] = kwargs['prompt']
        
        cls.save_templates(templates)
        print(f"Template '{name}' updated successfully")
        return True
    
    @classmethod
    def delete_template(cls, name: str):
        """Delete a template"""
        templates = cls.load_templates()
        
        if name not in templates:
            print(f"Template '{name}' not found")
            return False
        
        if name in cls.DEFAULT_TEMPLATES:
            print(f"Cannot delete default template '{name}'")
            return False
        
        del templates[name]
        cls.save_templates(templates)
        print(f"Template '{name}' deleted")
        return True
    
    @classmethod
    def export_template(cls, name: str, filename: str):
        """Export template to file"""
        template = cls.get_template(name)
        if not template:
            return False
        
        try:
            with open(filename, 'w') as f:
                json.dump(template, f, indent=2)
            print(f"Template exported to {filename}")
            return True
        except Exception as e:
            print(f"Error exporting template: {str(e)}")
            return False
    
    @classmethod
    def import_template(cls, name: str, filename: str):
        """Import template from file"""
        try:
            with open(filename, 'r') as f:
                template = json.load(f)
            
            templates = cls.load_templates()
            templates[name] = template
            cls.save_templates(templates)
            print(f"Template '{name}' imported from {filename}")
            return True
        except Exception as e:
            print(f"Error importing template: {str(e)}")
            return False


def main():
    """Command-line interface for template management"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Manage MOM templates')
    parser.add_argument('--list', action='store_true', help='List all templates')
    parser.add_argument('--add', nargs=4, metavar=('NAME', 'TITLE', 'DESCRIPTION', 'PROMPT'),
                       help='Add new template: --add name title description prompt')
    parser.add_argument('--update', nargs=2, metavar=('NAME', 'PROMPT'),
                       help='Update template prompt: --update name prompt')
    parser.add_argument('--delete', metavar='NAME', help='Delete custom template')
    parser.add_argument('--export', nargs=2, metavar=('NAME', 'FILE'),
                       help='Export template to file: --export name file.json')
    parser.add_argument('--import', dest='import_template', nargs=2, metavar=('NAME', 'FILE'),
                       help='Import template from file: --import name file.json')
    parser.add_argument('--show', metavar='NAME', help='Show template details')
    parser.add_argument('--init', action='store_true', help='Initialize default templates')
    
    args = parser.parse_args()
    
    # Initialize if needed
    if args.init:
        MOMTemplateManager.initialize_templates()
        return
    
    # List templates
    if args.list:
        MOMTemplateManager.list_templates()
        return
    
    # Show specific template
    if args.show:
        template = MOMTemplateManager.get_template(args.show)
        if template:
            print(f"\nTemplate: {args.show}")
            print(f"Name: {template['name']}")
            print(f"Description: {template['description']}")
            print(f"\nPrompt:\n{template['prompt']}")
        return
    
    # Add template
    if args.add:
        name, title, description, prompt = args.add
        MOMTemplateManager.add_template(name, title, description, prompt)
        return
    
    # Update template
    if args.update:
        name, prompt = args.update
        MOMTemplateManager.update_template(name, prompt=prompt)
        return
    
    # Delete template
    if args.delete:
        MOMTemplateManager.delete_template(args.delete)
        return
    
    # Export template
    if args.export:
        name, filename = args.export
        MOMTemplateManager.export_template(name, filename)
        return
    
    # Import template
    if args.import_template:
        name, filename = args.import_template
        MOMTemplateManager.import_template(name, filename)
        return
    
    # Default: show help
    parser.print_help()


if __name__ == '__main__':
    main()
