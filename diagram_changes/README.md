# Diagram Changes Analyzer

A Python-based tool for detecting and visualizing changes between XML-based diagrams. This tool helps identify additions, removals, and modifications between two versions of a diagram, generating visual representations of the changes.

> **Note:** The recommended way to use this tool is through the Jupyter notebook interface (`diagram_changes.ipynb`). The notebook provides an interactive, step-by-step workflow with visualizations and detailed explanations of the changes.

## Project Structure

```
diagram_changes/
├── files/
│   ├── generated_diagrams/    # Contains generated XML diagrams with changes highlighted
│   ├── rendered_diagrams/     # Contains rendered PNG versions of the diagrams
│   ├── input/                 # Directory for original and changed XML files
│   └── diagram_changes.json   # JSON file containing detected changes
├── scripts/
│   ├── detect_changes.py      # Core script for detecting differences between diagrams
│   ├── generate_new_diagrams.py # Script for generating new diagrams with highlighted changes
│   ├── print_changes.py       # Script for printing detected changes
│   └── render_diagram.py      # Script for rendering diagrams to PNG format
└── diagram_changes.ipynb      # Jupyter notebook for interactive analysis
```

## Features

- **Change Detection**: Analyzes and compares two XML diagram files to identify:
  - Added elements
  - Removed elements
  - Modified elements
  - Changes in relationships and connections

- **Visual Highlighting**:
  - Added elements (Green)
  - Removed elements (Red)
  - Modified elements (Yellow)
  - Special cases (Pink)

- **Multiple Output Formats**:
  - Generated XML diagrams with highlighted changes
  - Rendered PNG visualizations
  - JSON-formatted change reports

## Interactive Analysis (Recommended Method)

The project includes a Jupyter notebook (`diagram_changes.ipynb`) which is the primary interface for analyzing diagram changes. To get started:

1. Launch Jupyter Notebook:
   ```bash
   jupyter notebook
   ```

2. Open `diagram_changes.ipynb`

3. Follow the step-by-step instructions in the notebook to:
   - Load your original and modified diagrams
   - Detect and visualize changes
   - Export results in various formats
   - Explore detailed analysis of the modifications

The notebook provides an intuitive interface with inline visualizations and explanations of the changes.

## Alternative Usage (Command Line)

While the Jupyter notebook is recommended, you can also use the individual scripts directly:

1. Place your original and modified XML diagram files in the `files/input/` directory:
   - Original diagram as `original.xml`
   - Modified diagram as `changed.xml`

2. Run the change detection:
   ```bash
   python scripts/detect_changes.py
   ```

3. Generate visualized diagrams:
   ```bash
   python scripts/generate_new_diagrams.py
   ```

4. View changes in text format:
   ```bash
   python scripts/print_changes.py
   ```

5. Render diagrams to PNG:
   ```bash
   python scripts/render_diagram.py
   ```

## Color Coding

The tool uses the following color scheme to highlight changes:
- 🟢 Green: Added elements
- 🔴 Red: Removed elements
- 🟡 Yellow: Modified elements
- 🟣 Pink: Special cases (elements that have been added, removed, and changed)

## Requirements

- Python 3.x
- xml.etree.ElementTree
- Jupyter Notebook (for interactive analysis)

## Output Files

- `files/diagram_changes.json`: Contains detailed information about all detected changes
- `files/generated_diagrams/`: Contains XML files with visual highlighting of changes
- `files/rendered_diagrams/`: Contains PNG renderings of the modified diagrams