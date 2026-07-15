# MOM Templates Guide

Customize how Minutes of Meeting are generated using templates.

## Quick Start

### View Available Templates
```bash
python mom_templates.py --list
```

### Generate MOM with a Template
```bash
python mom_generator.py --audio meeting.wav --template executive
```

## Built-in Templates

### 1. Standard (Default)
**Best for:** General meetings
```
- Key Discussion Points
- Action Items
- Decisions Made
- Next Steps
- Attendees Summary
```

### 2. Executive
**Best for:** C-level/leadership reviews  
Concise 2-3 paragraph summary focused on:
- Key decisions
- Critical action items
- Business impact

### 3. Technical
**Best for:** Engineering/technical meetings  
Includes:
- Technical topics discussed
- Architecture/design decisions
- Code/system changes
- Performance considerations
- Outstanding technical issues

### 4. Agile
**Best for:** Sprint planning, standups, retrospectives  
Format:
- Yesterday Accomplished
- Today's Plan
- Blockers/Issues
- Team Members

### 5. Client
**Best for:** Client-facing meetings  
Includes:
- Meeting objective
- Client concerns/feedback
- Proposed solutions
- Deliverables & timeline
- (Professional tone, no jargon)

### 6. Legal/Compliance
**Best for:** Legal meetings, compliance reviews  
Includes:
- Attendees with titles
- Legal commitments made
- Compliance items addressed
- Follow-up requirements
- (Formal legal format)

## Using Templates

### Show Template Details
```bash
python mom_templates.py --show standard
```

### Generate MOM with Template
```bash
# Using batch script with template
python mom_generator.py --audio meeting.wav --template technical

# Process directory with template
python mom_generator.py --audio recordings --batch --template client
```

## Custom Templates

### Add Custom Template
```bash
python mom_templates.py --add mytemplate "My Template Title" "Description" "Your prompt template here with {transcript} placeholder"
```

Example:
```bash
python mom_templates.py --add sales "Sales Call Summary" "Sales meeting notes" "Summarize this sales call focusing on: 1. Prospect needs 2. Product fit 3. Next sales steps\n\nTranscript:\n{transcript}"
```

### Update Template Prompt
```bash
python mom_templates.py --update technical "Your updated prompt with {transcript} placeholder"
```

### Delete Custom Template
```bash
python mom_templates.py --delete mytemplate
```

## Template File Structure

Templates are stored in `mom_templates.json`:

```json
{
  "template_name": {
    "name": "Display Name",
    "description": "What this template is for",
    "prompt": "Your prompt here with {transcript} placeholder"
  }
}
```

## Template Prompt Best Practices

### Required: Use {transcript} placeholder
```python
prompt = """
Generate MOM from this meeting:

Transcript:
{transcript}

Please include:
1. Key points
2. Action items
"""
```

### Make it Specific
```python
# Good - specific output format
prompt = """
Focus on financial metrics and budget discussions:
{transcript}

Format output as:
- Budget Areas Discussed
- Cost Impacts
- Approved Changes
- Next Budget Review
"""

# Avoid - too vague
prompt = "Summarize this: {transcript}"
```

### Include Context
```python
# Good - provides context
prompt = """
This is a security team meeting. Extract:
{transcript}

Security-focused items:
1. Vulnerabilities discussed
2. Security improvements planned
3. Compliance items
"""

# Avoid - missing context
prompt = "Meeting minutes: {transcript}"
```

## Advanced: Custom Templates

### Example 1: Product Management
```bash
python mom_templates.py --add pm "Product Meeting" "Product management discussions" "From this product team meeting, extract:

Transcript:
{transcript}

Sections:
1. Features Discussed
2. User Feedback Summary
3. Product Roadmap Updates
4. Technical Constraints
5. Timeline & Priorities
6. Owner for Each Initiative"
```

### Example 2: HR/Team
```bash
python mom_templates.py --add hr_meeting "HR Discussion" "HR and team meetings" "Create HR meeting notes:

Transcript:
{transcript}

Include:
1. Team Updates
2. HR Topics Discussed
3. Policy Changes
4. Training Needs Identified
5. Action Items with Owners
6. Confidential Notes (if any)"
```

### Example 3: Marketing
```bash
python mom_templates.py --add marketing "Marketing Campaign" "Marketing strategy meetings" "Extract marketing meeting outcomes:

Transcript:
{transcript}

Marketing Focus:
1. Campaign Goals
2. Target Audience
3. Key Messages
4. Channels/Tactics
5. Budget Allocation
6. Success Metrics
7. Campaign Owner"
```

## Import/Export Templates

### Export Template to File
```bash
python mom_templates.py --export standard template_standard.json
```

### Import Template from File
```bash
python mom_templates.py --import mycompany_template company_template.json
```

Useful for:
- Sharing templates across teams
- Version control
- Template library

## Using with Batch Processing

Generate MOMs with custom template for all files:
```bash
python mom_generator.py --audio recordings --batch --template technical
```

## Template Customization Workflow

1. **Start** with built-in template that's closest to your needs:
   ```bash
   python mom_templates.py --show standard
   ```

2. **Identify** what needs to change:
   - What sections to add/remove?
   - What specific format needed?
   - What context is important?

3. **Create** custom template:
   ```bash
   python mom_templates.py --add mytemplate "My Title" "Description" "Your prompt"
   ```

4. **Test** with sample meeting:
   ```bash
   python mom_generator.py --audio sample.wav --template mytemplate
   ```

5. **Refine** based on output:
   ```bash
   python mom_templates.py --update mytemplate "Improved prompt"
   ```

6. **Share** or backup:
   ```bash
   python mom_templates.py --export mytemplate mytemplate.json
   ```

## Troubleshooting

### "Template not found"
- Check available templates: `python mom_templates.py --list`
- Verify template name spelling (case-sensitive)

### "Error: {transcript} not replaced"
- Make sure your prompt includes `{transcript}` placeholder
- It will be replaced with the actual meeting transcript

### "Output doesn't look right"
- Review the generated template prompt
- Make it more specific about what you want
- Test with different Ollama models

## Tips for Best Results

1. **Be Specific**: More specific prompts → better output
2. **Add Context**: Include what type of meeting it is
3. **Clear Format**: Specify exact sections/format desired
4. **Test First**: Try template with one file before batch
5. **Iterate**: Refine prompts based on results
6. **Share**: Save working templates for team use

## Template Performance

- **Simple templates** (fewer sections) = faster processing
- **Complex templates** (detailed requirements) = better quality but slower
- **Larger Ollama models** = better output quality
- **Smaller Ollama models** = faster processing

Choose based on your priorities: Speed vs. Quality

---

For more information, see:
- README.md - Full documentation
- QUICKSTART.md - Getting started
- config.json - Configuration options
