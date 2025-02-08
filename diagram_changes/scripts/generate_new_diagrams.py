import xml.etree.ElementTree as ET
import json
import os
import copy

# Define colors for different change types
colors = {
    'added': '#00FF00',      # Green
    'removed': '#FF0000',    # Red
    'changed': '#FFFF00',    # Yellow
    'added_changed': '#FF45D9'  # Pink for objects that have been added, removed and changed
}

def modify_style(style, color, is_standalone=False):
    """Add dashed border with specified color to the style."""
    style_parts = style.split(';') if style else []
    new_parts = []
    
    # Remove existing stroke and label border properties if they exist
    for part in style_parts:
        if not any(prop in part for prop in ['strokeWidth', 'dashed', 'strokeColor'] + (['labelBorderColor'] if is_standalone else [])):
            new_parts.append(part)
    
    # Add new style properties
    new_parts.extend([
        'strokeWidth=3',
        'dashed=1',
        f'strokeColor={color}'
    ])
    
    # Add labelBorderColor only for standalone mxCells
    if is_standalone:
        new_parts.append(f'labelBorderColor={color}')
    
    return ';'.join(filter(None, new_parts))

def get_change_type(obj_id, fact_sheet_id, changes_data):
    """Determine if an object was added, removed, changed, or unchanged."""
    # Check in factSheets first using factSheetId
    if fact_sheet_id:
        for item in changes_data['removedFactSheets']:
            if item['factSheetId'] == fact_sheet_id:
                return 'removed'
        for item in changes_data['addedFactSheets']:
            if item['factSheetId'] == fact_sheet_id:
                return 'added'
        for item in changes_data['changedFactSheets']:
            if item['factSheetId'] == fact_sheet_id:
                return 'changed'
    
    # Then check by objectId
    for category in ['addedFactSheets', 'removedFactSheets', 'changedFactSheets']:
        for item in changes_data[category]:
            if item['objectId'] == obj_id:
                return category.replace('FactSheets', '')
    
    # Check in relations
    for category in ['addedRelations', 'removedRelations', 'changedRelations']:
        for item in changes_data[category]:
            if item['objectId'] == obj_id:
                return category.replace('Relations', '')
    
    # Check in generic objects
    for category in ['addedObjects', 'removedObjects', 'changedObjects']:
        for item in changes_data[category]:
            if item['objectId'] == obj_id:
                return category.replace('Objects', '')
    
    # Check in cells
    for category in ['addedCells', 'removedCells', 'changedCells']:
        for item in changes_data[category]:
            if item['id'] == obj_id:
                return category.replace('Cells', '')
    
    return 'unchanged'

def apply_change_style(obj, change_type):
    """Apply style changes based on the change type."""
    if change_type == 'unchanged':
        return
    
    # Find or create mxCell element
    mxcell = obj.find('mxCell')
    if mxcell is None:
        return
    
    # Modify the style
    current_style = mxcell.get('style', '')
    new_style = modify_style(current_style, colors[change_type], is_standalone=False)
    mxcell.set('style', new_style)

def create_changed_based_diagram(changed_xml_path, changes_json_path, output_path):
    """Create a diagram based on changed.xml showing additions and changes."""
    # Load and parse the XML file
    tree = ET.parse(changed_xml_path)
    root = tree.getroot()
    
    # Load changes data
    with open(changes_json_path, 'r') as f:
        changes_data = json.load(f)
    
    # Create sets of IDs for quick lookup
    added_ids = {item['factSheetId'] for item in changes_data['addedFactSheets']}
    changed_ids = {item['factSheetId'] for item in changes_data['changedFactSheets']}
    
    # Process all objects
    for obj in root.findall('.//object'):
        obj_id = obj.get('id')
        fact_sheet_id = obj.get('factSheetId')
        if obj_id:
            change_type = get_change_type(obj_id, fact_sheet_id, changes_data)
            if change_type in ['added', 'changed']:
                # Check if object is both added and changed
                if fact_sheet_id and fact_sheet_id in added_ids and fact_sheet_id in changed_ids:
                    mxcell = obj.find('mxCell')
                    if mxcell is not None:
                        current_style = mxcell.get('style', '')
                        new_style = modify_style(current_style, colors['added_changed'], is_standalone=False)
                        mxcell.set('style', new_style)
                else:
                    # Regular styling for other cases
                    mxcell = obj.find('mxCell')
                    if mxcell is not None:
                        current_style = mxcell.get('style', '')
                        new_style = modify_style(current_style, colors[change_type], is_standalone=False)
                        mxcell.set('style', new_style)
    
    # Process standalone mxCells (those directly under root)
    for cell in root.findall('.//root/mxCell[@id!="0"][@id!="1"]'):
        cell_id = cell.get('id')
        if cell_id:
            change_type = get_change_type(cell_id, None, changes_data)
            if change_type in ['added', 'changed']:
                current_style = cell.get('style', '')
                # Check if cell is both added and changed
                if cell_id in added_ids and cell_id in changed_ids:
                    new_style = modify_style(current_style, colors['added_changed'], is_standalone=True)
                else:
                    new_style = modify_style(current_style, colors[change_type], is_standalone=True)
                cell.set('style', new_style)
    
    # Write the tree to the output file
    tree.write(output_path, encoding='utf-8', xml_declaration=True)

def create_original_based_diagram(original_xml_path, changes_json_path, output_path):
    """Create a diagram based on original.xml showing removals and changes."""
    # Load and parse the XML file
    tree = ET.parse(original_xml_path)
    root = tree.getroot()
    
    # Load changes data
    with open(changes_json_path, 'r') as f:
        changes_data = json.load(f)
    
    # Process all objects
    for obj in root.findall('.//object'):
        obj_id = obj.get('id')
        fact_sheet_id = obj.get('factSheetId')
        if obj_id:
            change_type = get_change_type(obj_id, fact_sheet_id, changes_data)
            if change_type in ['removed', 'changed']:
                mxcell = obj.find('mxCell')
                if mxcell is not None:
                    current_style = mxcell.get('style', '')
                    new_style = modify_style(current_style, colors[change_type], is_standalone=False)
                    mxcell.set('style', new_style)
    
    # Process standalone mxCells (those directly under root)
    for cell in root.findall('.//root/mxCell[@id!="0"][@id!="1"]'):
        cell_id = cell.get('id')
        if cell_id:
            change_type = get_change_type(cell_id, None, changes_data)
            if change_type in ['removed', 'changed']:
                current_style = cell.get('style', '')
                new_style = modify_style(current_style, colors[change_type], is_standalone=True)
                cell.set('style', new_style)
    
    # Write the tree to the output file
    tree.write(output_path, encoding='utf-8', xml_declaration=True)

def combine_diagrams(original_xml_path, changed_xml_path, changes_json_path, output_path):
    # Load and parse the XML files
    original_tree = ET.parse(original_xml_path)
    changed_tree = ET.parse(changed_xml_path)
    
    # Load changes data
    with open(changes_json_path, 'r') as f:
        changes_data = json.load(f)
    
    # Create a new tree starting with the changed diagram
    combined_tree = copy.deepcopy(changed_tree)
    combined_root = combined_tree.getroot()
    
    # Get all objects from both diagrams
    original_objects = original_tree.findall('.//object')
    changed_objects = combined_tree.findall('.//object')
    
    # Process all objects in the changed diagram
    for obj in changed_objects:
        obj_id = obj.get('id')
        fact_sheet_id = obj.get('factSheetId')
        if obj_id:
            change_type = get_change_type(obj_id, fact_sheet_id, changes_data)
            apply_change_style(obj, change_type)
            
            # If this is an added object, adjust its y-coordinate
            if change_type == 'added':
                mxcell = obj.find('mxCell')
                if mxcell is not None:
                    geometry = mxcell.find('mxGeometry')
                    if geometry is not None:
                        current_y = float(geometry.get('y', 0))
                        height = float(geometry.get('height', 45))  # Default height is 45 if not specified
                        new_y = current_y + 15 + height
                        geometry.set('y', str(new_y))
    
    # Keep track of which IDs were modified
    modified_ids = {}
    
    # Add removed objects from the original diagram
    changed_ids = {obj.get('id') for obj in changed_objects}
    for obj in original_objects:
        obj_id = obj.get('id')
        fact_sheet_id = obj.get('factSheetId')
        if obj_id:
            change_type = get_change_type(obj_id, fact_sheet_id, changes_data)
            if change_type == 'removed':
                # This is a removed object
                obj_copy = copy.deepcopy(obj)
                # If this ID exists in the changed diagram, append '_removed'
                if obj_id in changed_ids:
                    new_id = f"{obj_id}_removed"
                    obj_copy.set('id', new_id)
                    modified_ids[obj_id] = new_id
                    # Update any references to this ID in mxCell elements
                    mxcell = obj_copy.find('mxCell')
                    if mxcell is not None:
                        if mxcell.get('source') == obj_id:
                            mxcell.set('source', new_id)
                        if mxcell.get('target') == obj_id:
                            mxcell.set('target', new_id)
                # Apply red style
                mxcell = obj_copy.find('mxCell')
                if mxcell is not None:
                    current_style = mxcell.get('style', '')
                    new_style = modify_style(current_style, colors['removed'], is_standalone=False)
                    mxcell.set('style', new_style)
                # Add to combined diagram
                root_one = combined_root.find('.//mxCell[@id="1"]/..')
                if root_one is not None:
                    root_one.append(obj_copy)
    
    # Update all relation references in the combined diagram
    for relation in combined_root.findall('.//object[@type="relation"]'):
        mxcell = relation.find('mxCell')
        if mxcell is not None:
            source = mxcell.get('source')
            target = mxcell.get('target')
            if source in modified_ids:
                mxcell.set('source', modified_ids[source])
            if target in modified_ids:
                mxcell.set('target', modified_ids[target])
    
    # Process standalone mxCells (those directly under root)
    for cell in combined_root.findall('.//root/mxCell[@id!="0"][@id!="1"]'):
        cell_id = cell.get('id')
        if cell_id:
            change_type = get_change_type(cell_id, None, changes_data)
            if change_type != 'unchanged':
                current_style = cell.get('style', '')
                new_style = modify_style(current_style, colors[change_type], is_standalone=True)
                cell.set('style', new_style)
    
    # Write the combined tree to the output file
    combined_tree.write(output_path, encoding='utf-8', xml_declaration=True)

def main():
    # Get the directory containing the files
    input_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'files/input')
    changes_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'files')
    generated_diagrams_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'files/generated_diagrams')
    
    # Define input and output paths
    original_xml = os.path.join(input_dir, 'original.xml')
    changed_xml = os.path.join(input_dir, 'changed.xml')
    changes_json = os.path.join(changes_dir, 'diagram_changes.json')

    # Create all three diagrams
    combine_diagrams(original_xml, changed_xml, changes_json, 
                    os.path.join(generated_diagrams_dir, 'combined_diagram.xml'))
    create_changed_based_diagram(changed_xml, changes_json,
                               os.path.join(generated_diagrams_dir, 'additions_diagram.xml'))
    create_original_based_diagram(original_xml, changes_json,
                                os.path.join(generated_diagrams_dir, 'removals_diagram.xml'))

if __name__ == '__main__':
    main()
