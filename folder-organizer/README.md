# Folder Organizer

A powerful Python script to automatically organize files into folders based on various criteria like file type, date, size, or custom rules.

## Features

- **Multiple Organization Methods**: By type, date, size, name patterns, or custom rules
- **Flexible Date Formats**: Organize by year, month, or custom date patterns
- **Size-Based Organization**: Group files by size ranges
- **Custom Rules Engine**: Define complex organization rules with JSON
- **Safe Operations**: Dry run mode to preview changes
- **Undo Functionality**: Generate scripts to reverse organization
- **Recursive Processing**: Handle subdirectories
- **Copy or Move**: Choose between copying or moving files
- **Conflict Resolution**: Automatic handling of filename conflicts

## Usage

### Basic Syntax
```bash
python folder_organizer.py <source_directory> [options]
```

### Examples

#### 1. Organize by File Type (Dry Run)
```bash
python folder_organizer.py ./Downloads --by-type
```

#### 2. Execute File Type Organization
```bash
python folder_organizer.py ./Downloads --by-type --execute
```

#### 3. Organize by Date (Monthly Folders)
```bash
python folder_organizer.py ./Photos --by-date --execute
```

#### 4. Organize by Date (Yearly Folders)
```bash
python folder_organizer.py ./Documents --by-date --date-format "%Y" --execute
```

#### 5. Organize by File Size
```bash
python folder_organizer.py ./Files --by-size --execute
```

#### 6. Organize by Name Patterns
```bash
python folder_organizer.py ./Downloads --by-name '{"Screenshots": "screenshot", "Invoices": "invoice"}' --execute
```

#### 7. Use Custom Rules
```bash
python folder_organizer.py ./Files --custom-rules my_rules.json --execute
```

#### 8. Copy Instead of Move
```bash
python folder_organizer.py ./Photos --by-type --copy --execute
```

## Organization Methods

### 1. By File Type (`--by-type`)

Organizes files into predefined categories:

- **Images**: jpg, png, gif, bmp, tiff, webp, svg, etc.
- **Documents**: pdf, doc, docx, txt, rtf, odt, etc.
- **Videos**: mp4, avi, mkv, mov, wmv, etc.
- **Audio**: mp3, wav, flac, aac, ogg, etc.
- **Archives**: zip, rar, 7z, tar, gz, etc.
- **Code**: py, js, html, css, cpp, java, etc.
- **Others**: Files that don't match any category

### 2. By Date (`--by-date`)

Organizes files based on modification or creation date:

```bash
# Monthly folders (2023-01, 2023-02, etc.)
--date-format "%Y-%m"

# Yearly folders (2023, 2024, etc.)
--date-format "%Y"

# Daily folders (2023-01-15, etc.)
--date-format "%Y-%m-%d"

# Custom format (Jan-2023, etc.)
--date-format "%b-%Y"
```

### 3. By Size (`--by-size`)

Default size categories:
- **Small**: < 1MB
- **Medium**: 1-10MB  
- **Large**: 10-100MB
- **Very Large**: > 100MB

### 4. By Name Patterns (`--by-name`)

Organize based on filename content:

```bash
python folder_organizer.py ./Downloads --by-name '{
  "Screenshots": "screenshot",
  "Invoices": "invoice", 
  "Receipts": "receipt",
  "Work Docs": "work"
}' --execute
```

### 5. Custom Rules (`--custom-rules`)

Use a JSON file to define complex organization rules.

## Custom Rules Format

Create a JSON file with custom organization rules:

```json
{
  "description": "My custom organization rules",
  "default_folder": "Others",
  "rules": [
    {
      "name": "Work Documents",
      "folder": "Work",
      "conditions": {
        "extensions": [".docx", ".xlsx", ".pptx"],
        "name_contains": "work"
      }
    },
    {
      "name": "Screenshots", 
      "folder": "Screenshots",
      "conditions": {
        "extensions": [".png", ".jpg"],
        "name_contains": "screenshot"
      }
    },
    {
      "name": "Large Videos",
      "folder": "Large Videos", 
      "conditions": {
        "extensions": [".mp4", ".avi"],
        "size_range": [104857600, 999999999999]
      }
    }
  ]
}
```

### Rule Conditions

- **extensions**: List of file extensions (e.g., `[".jpg", ".png"]`)
- **name_contains**: Text that must be in filename
- **size_range**: `[min_bytes, max_bytes]` for file size

## Command Line Options

### Required
- `source_dir`: Directory to organize

### Organization Methods (choose one)
- `--by-type`: Organize by file type
- `--by-date`: Organize by date
- `--by-size`: Organize by file size  
- `--by-name JSON`: Organize by name patterns
- `--custom-rules FILE`: Use custom rules from JSON file

### Options
- `--target-dir DIR`: Target directory (default: same as source)
- `--date-format FORMAT`: Date format for date organization (default: %Y-%m)
- `--use-creation-date`: Use creation date instead of modification date
- `--recursive`: Process files in subdirectories
- `--include-hidden`: Include hidden files (starting with .)
- `--copy`: Copy files instead of moving them
- `--execute`: Execute organization (default is dry run)
- `--create-undo`: Create undo script after organization

### Utilities
- `--create-sample-rules FILE`: Create sample custom rules file

## Real-World Examples

### Example 1: Clean Up Downloads Folder

```bash
# Preview organization
python folder_organizer.py ~/Downloads --by-type

# Execute if satisfied
python folder_organizer.py ~/Downloads --by-type --execute --create-undo
```

**Result:**
```
Downloads/
├── Images/
│   ├── photo1.jpg
│   └── screenshot.png
├── Documents/
│   ├── invoice.pdf
│   └── manual.docx
├── Archives/
│   └── software.zip
└── Others/
    └── unknown_file.xyz
```

### Example 2: Organize Photo Collection by Date

```bash
python folder_organizer.py ./Photos --by-date --date-format "%Y-%m" --recursive --execute
```

**Result:**
```
Photos/
├── 2023-01/
├── 2023-02/
├── 2023-12/
└── 2024-01/
```

### Example 3: Organize Work Files with Custom Rules

**Create rules file (work_rules.json):**
```json
{
  "default_folder": "Others",
  "rules": [
    {
      "name": "Client Documents",
      "folder": "Clients",
      "conditions": {
        "extensions": [".pdf", ".docx"],
        "name_contains": "client"
      }
    },
    {
      "name": "Presentations", 
      "folder": "Presentations",
      "conditions": {
        "extensions": [".pptx", ".key"]
      }
    },
    {
      "name": "Spreadsheets",
      "folder": "Data", 
      "conditions": {
        "extensions": [".xlsx", ".csv"]
      }
    }
  ]
}
```

**Run organization:**
```bash
python folder_organizer.py ./WorkFiles --custom-rules work_rules.json --execute
```

### Example 4: Size-Based Organization for Media Files

```bash
python folder_organizer.py ./Media --by-size --recursive --execute
```

**Result:**
```
Media/
├── Small (< 1MB)/
├── Medium (1-10MB)/
├── Large (10-100MB)/
└── Very Large (> 100MB)/
```

## Safety Features

### 1. Dry Run Mode
By default, the script runs in dry run mode showing what would happen without making changes:

```bash
python folder_organizer.py ./Files --by-type
# Shows preview, doesn't move files

python folder_organizer.py ./Files --by-type --execute  
# Actually moves files
```

### 2. Undo Functionality
Generate a script to reverse the organization:

```bash
python folder_organizer.py ./Files --by-type --execute --create-undo
# Creates undo_organization.py

python undo_organization.py  # Moves files back
```

### 3. Conflict Resolution
Automatically handles filename conflicts by adding numbers:
- `document.pdf` → `document_1.pdf`
- `photo.jpg` → `photo_1.jpg`

### 4. Copy Mode
Use `--copy` to copy files instead of moving them, preserving originals.

## Advanced Usage

### Recursive Organization
Process all subdirectories:
```bash
python folder_organizer.py ./Project --by-type --recursive --execute
```

### Include Hidden Files
Process files starting with `.`:
```bash
python folder_organizer.py ./Config --by-type --include-hidden --execute
```

### Custom Target Directory
Organize files into a different location:
```bash
python folder_organizer.py ./Messy --by-type --target-dir ./Organized --execute
```

### Complex Date Patterns
```bash
# Organize by year and month
python folder_organizer.py ./Files --by-date --date-format "%Y/%B" --execute

# Result: 2023/January/, 2023/February/, etc.
```

## Sample Workflows

### 1. Download Folder Cleanup
```bash
# 1. Preview organization
python folder_organizer.py ~/Downloads --by-type

# 2. Execute with undo capability  
python folder_organizer.py ~/Downloads --by-type --execute --create-undo

# 3. If needed, undo
python undo_organization.py
```

### 2. Photo Organization
```bash
# Organize photos by year-month, including subdirectories
python folder_organizer.py ./Photos --by-date --date-format "%Y-%m" --recursive --execute
```

### 3. Project File Organization
```bash
# Create custom rules for project files
python folder_organizer.py --create-sample-rules project_rules.json

# Edit project_rules.json as needed

# Organize using custom rules
python folder_organizer.py ./ProjectFiles --custom-rules project_rules.json --execute
```

## Requirements

```bash
pip install colorama tqdm
```

## Tips and Best Practices

### 1. Always Test First
```bash
# Always run without --execute first to preview
python folder_organizer.py ./Files --by-type
```

### 2. Use Undo Scripts
```bash
# Create undo capability for safety
python folder_organizer.py ./Files --by-type --execute --create-undo
```

### 3. Backup Important Files
Make backups of important directories before organizing.

### 4. Start Small
Test on a small directory first to understand the behavior.

### 5. Custom Rules for Specific Needs
Create custom rules for specialized organization requirements.

## Troubleshooting

### Common Issues

1. **Permission Errors**
   - Ensure you have write permissions to source and target directories
   - Run as administrator if needed on Windows

2. **Files Not Moving**
   - Check if you're using `--execute` flag
   - Verify source directory exists and contains files

3. **Unexpected Results**
   - Use dry run mode first to preview changes
   - Check file extensions and naming patterns

### Error Handling

The script handles errors gracefully:
- Continues processing if individual files fail
- Logs all errors for review
- Provides summary of successful and failed operations

This folder organizer provides a comprehensive solution for keeping your files organized automatically, with safety features and flexibility to handle various organization needs.
