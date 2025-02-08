import argparse
import os
import subprocess
import sys

def ensure_drawio_installed():
    """Check if draw.io desktop is installed and accessible."""
    # Common paths for draw.io installation
    drawio_paths = {
        'darwin': ['/Applications/draw.io.app/Contents/MacOS/draw.io'],
        'linux': ['/usr/bin/drawio', '/usr/local/bin/drawio'],
        'win32': ['C:\\Program Files\\draw.io\\draw.io.exe']
    }
    
    platform = sys.platform
    if platform not in drawio_paths:
        raise RuntimeError(f"Unsupported platform: {platform}")
        
    for path in drawio_paths[platform]:
        if os.path.exists(path):
            return path
            
    raise RuntimeError("draw.io is not installed. Please install it from https://www.drawio.com/")

def render_diagram(input_xml_path, output_path, format='png'):
    """
    Render a draw.io XML diagram as an image.
    
    Args:
        input_xml_path (str): Path to the input XML file
        output_path (str): Path where the output image should be saved
        format (str): Output format (png, jpg, pdf, svg)
    """
    drawio_path = ensure_drawio_installed()
    
    # Ensure input file exists
    if not os.path.exists(input_xml_path):
        raise FileNotFoundError(f"Input file not found: {input_xml_path}")
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    # Construct the export command
    cmd = [
        drawio_path,
        '--export',
        '--format', format,
        '--output', output_path,
        input_xml_path
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"Successfully rendered diagram to: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error rendering diagram: {e.stderr.decode()}")
        raise

def main():
    parser = argparse.ArgumentParser(description='Render draw.io XML diagram as image')
    parser.add_argument('input', help='Input XML file path')
    parser.add_argument('output', help='Output image file path')
    parser.add_argument('--format', choices=['png', 'jpg', 'pdf', 'svg'], 
                      default='png', help='Output format (default: png)')
    
    args = parser.parse_args()
    render_diagram(args.input, args.output, args.format)

if __name__ == '__main__':
    main()
