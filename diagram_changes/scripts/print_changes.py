import json
import xml.etree.ElementTree as ET
import os

def get_label_for_id(factsheet_id, original_root, changed_root):
    # Search in both XML files for the factsheet
    for root in [original_root, changed_root]:
        # Find all factSheet objects
        for obj in root.findall(".//object[@type='factSheet']"):
            if obj.get('factSheetId') == factsheet_id and obj.get('label'):
                return obj.get('label')
    return factsheet_id  # Return the ID if no label is found

def format_changes(changes):
    formatted_changes = []
    for category, category_changes in changes.items():
        if category == 'mxCell':
            if 'geometry' in category_changes:
                formatted_changes.append(("geometry", "position was modified"))
            for field, value in category_changes.items():
                if field != 'geometry' and isinstance(value, dict) and 'from' in value and 'to' in value:
                    formatted_changes.append((field, {
                        'from': value['from'],
                        'to': value['to']
                    }))
        elif isinstance(category_changes, dict):
            if 'from' in category_changes and 'to' in category_changes:
                formatted_changes.append((category, {
                    'from': category_changes['from'],
                    'to': category_changes['to']
                }))
            else:
                for field, value in category_changes.items():
                    if isinstance(value, dict) and 'from' in value and 'to' in value:
                        formatted_changes.append((field, {
                            'from': value['from'],
                            'to': value['to']
                        }))
    return formatted_changes

def print_change(field, value):
    if isinstance(value, dict):  # It's a from/to change
        print(f"  - {field} changed:")
        print(f"      from: '{value['from']}'")
        print(f"      to:   '{value['to']}'")
    else:  # It's a simple change
        print(f"  - {value}")

def print_header(text):
    print(f"")
    print("-" * len(text))
    print(f"{text}")
    print("-" * len(text))

def read_changes(json_file, original_xml='original.xml', changed_xml='changed.xml'):
    # Parse XML files
    original_tree = ET.parse(original_xml)
    changed_tree = ET.parse(changed_xml)
    original_root = original_tree.getroot()
    changed_root = changed_tree.getroot()
    
    with open(json_file, 'r') as f:
        changes = json.load(f)
    
    # Process each change type if it has entries
    for change_type, items in changes.items():
        if items:  # Only process non-empty lists
            if change_type == "addedFactSheets":
                print_header("Added Fact Sheets")
                for item in items:
                    print(f"• {item['label']} ({item['factSheetType']})")
            
            elif change_type == "removedFactSheets":
                print_header("Removed Fact Sheets")
                for item in items:
                    print(f"• {item['label']} ({item['factSheetType']})")
            
            elif change_type == "changedFactSheets":
                print_header("Changed Fact Sheets")
                for item in items:
                    print(f"• {item['label']} ({item['factSheetType']}) was modified:")
                    if 'changes' in item:
                        for field, value in format_changes(item['changes']):
                            print_change(field, value)
                    print()
            
            elif change_type == "addedRelations":
                print_header("Added Relations")
                for item in items:
                    source_label = get_label_for_id(item['sourceFactSheetId'], original_root, changed_root)
                    target_label = get_label_for_id(item['targetFactSheetId'], original_root, changed_root)
                    print(f"• Added {item['dependencyRelation']} relation:")
                    print(f"    from: '{source_label}'")
                    print(f"    to:   '{target_label}'")
                    print()
            
            elif change_type == "removedRelations":
                print_header("Removed Relations")
                for item in items:
                    source_label = get_label_for_id(item['sourceFactSheetId'], original_root, changed_root)
                    target_label = get_label_for_id(item['targetFactSheetId'], original_root, changed_root)
                    print(f"• Removed {item['dependencyRelation']} relation:")
                    print(f"    from: '{source_label}'")
                    print(f"    to:   '{target_label}'")
                    print()

            elif change_type == "changedRelations":
                print_header("Changed Relations")
                for item in items:
                    source_label = get_label_for_id(item['sourceFactSheetId'], original_root, changed_root)
                    target_label = get_label_for_id(item['targetFactSheetId'], original_root, changed_root)
                    print(f"• Modified {item['dependencyRelation']} relation:")
                    print(f"    from: '{source_label}'")
                    print(f"    to:   '{target_label}'")
                    if 'changes' in item:
                        for field, value in format_changes(item['changes']):
                            print_change(field, value)
                    print()
            
            elif change_type == "addedObjects":
                print_header("Added Objects")
                for item in items:
                    print(f"• {item['label']}")
            
            elif change_type == "removedObjects":
                print_header("Removed Objects")
                for item in items:
                    print(f"• {item['label']}")

            elif change_type == "changedObjects":
                print_header("Changed Objects")
                for item in items:
                    print(f"• {item['label']} was modified:")
                    if 'changes' in item:
                        for field, value in format_changes(item['changes']):
                            print_change(field, value)
                    print()
            
            elif change_type == "addedCells":
                print_header("Added Cells")
                for item in items:
                    if 'value' in item:
                        print(f"• Added cell with value: '{item['value']}'")
                    else:
                        print(f"• Added new connection or shape")

            elif change_type == "removedCells":
                print_header("Removed Cells")
                for item in items:
                    if 'value' in item:
                        print(f"• Removed cell with value: '{item['value']}'")
                    else:
                        print(f"• Removed connection or shape")

            elif change_type == "changedCells":
                print_header("Changed Cells")
                for item in items:
                    cell_desc = "Cell"
                    if 'value' in item:
                        cell_desc += f" with value: '{item['value']}'"
                    print(f"• {cell_desc} was modified:")
                    if 'changes' in item:
                        for field, value in format_changes(item['changes']):
                            print_change(field, value)
                    print()

if __name__ == "__main__":
    # Get the directory containing the files
    input_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'files/input')
    changes_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'files')
    
    # Read changes with proper file paths
    read_changes(
        os.path.join(changes_dir, 'diagram_changes.json'),
        os.path.join(input_dir, 'original.xml'),
        os.path.join(input_dir, 'changed.xml')
    )
