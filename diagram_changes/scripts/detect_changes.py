import xml.etree.ElementTree as ET
import json
import os

def extract_mxcell_info(mxcell_elem):
    """Extract information from an mxCell element including its geometry."""
    info = {
        'style': mxcell_elem.get('style'),
        'parent': mxcell_elem.get('parent'),
        'vertex': mxcell_elem.get('vertex'),
        'edge': mxcell_elem.get('edge'),
        'source': mxcell_elem.get('source'),
        'target': mxcell_elem.get('target'),
        'id': mxcell_elem.get('id'),
        'value': mxcell_elem.get('value')
    }
    
    # Get geometry if it exists
    geometry = mxcell_elem.find('mxGeometry')
    if geometry is not None:
        info['geometry'] = {
            'x': geometry.get('x'),
            'y': geometry.get('y'),
            'width': geometry.get('width'),
            'height': geometry.get('height'),
            'relative': geometry.get('relative'),
        }
    
    return {k: v for k, v in info.items() if v is not None}

def extract_standalone_mxcell_info(mxcell_elem):
    """Extract information from a standalone mxCell element."""
    info = extract_mxcell_info(mxcell_elem)
    
    # For standalone cells, we want to include any child elements that might contain text/labels
    edge_label = mxcell_elem.find('.//mxGeometry//*[@value]')
    if edge_label is not None:
        info['label'] = edge_label.get('value')
    
    return info

def extract_generic_object_info(object_elem, include_mxcell=False):
    """Extract information from a generic object element."""
    info = {
        'label': object_elem.get('label'),
        'objectId': object_elem.get('id')
    }
    
    # Only include mxCell if specifically requested
    if include_mxcell:
        mxcell = object_elem.find('mxCell')
        if mxcell is not None:
            info['mxCell'] = extract_mxcell_info(mxcell)
    
    return info

def extract_fact_sheet_info(object_elem, include_mxcell=False):
    """Extract relevant information from a factSheet object element."""
    info = {
        'label': object_elem.get('label'),
        'factSheetType': object_elem.get('factSheetType'),
        'factSheetId': object_elem.get('factSheetId'),
        'objectId': object_elem.get('id')
    }
    
    # Only include mxCell if specifically requested
    if include_mxcell:
        mxcell = object_elem.find('mxCell')
        if mxcell is not None:
            info['mxCell'] = extract_mxcell_info(mxcell)
    
    return info

def extract_relation_info(object_elem, include_mxcell=False):
    """Extract relevant information from a relation object element."""
    info = {
        'dependencyRelation': object_elem.get('dependencyRelation'),
        'relationId': object_elem.get('relationId'),
        'sourceFactSheetId': object_elem.get('sourceFactSheetId'),
        'targetFactSheetId': object_elem.get('targetFactSheetId'),
        'objectId': object_elem.get('id')
    }
    
    # Only include mxCell if specifically requested
    if include_mxcell:
        mxcell = object_elem.find('mxCell')
        if mxcell is not None:
            info['mxCell'] = extract_mxcell_info(mxcell)
    
    return info

def compare_mxcells(original_mxcell, changed_mxcell):
    """Compare two mxCell elements and return their differences."""
    if original_mxcell is None or changed_mxcell is None:
        return None
    
    original_info = extract_mxcell_info(original_mxcell)
    changed_info = extract_mxcell_info(changed_mxcell)
    
    differences = {}
    
    # Compare all attributes
    for key in set(original_info.keys()) | set(changed_info.keys()):
        original_value = original_info.get(key)
        changed_value = changed_info.get(key)
        
        if original_value != changed_value:
            if isinstance(original_value, dict) and isinstance(changed_value, dict):
                # Handle nested geometry differences
                geo_diff = {}
                for geo_key in set(original_value.keys()) | set(changed_value.keys()):
                    orig_geo = original_value.get(geo_key)
                    changed_geo = changed_value.get(geo_key)
                    if orig_geo != changed_geo:
                        geo_diff[geo_key] = {'from': orig_geo, 'to': changed_geo}
                if geo_diff:
                    differences[key] = geo_diff
            else:
                differences[key] = {'from': original_value, 'to': changed_value}
    
    return differences if differences else None

def compare_objects(original_obj, changed_obj, extract_info_func):
    """Compare two objects and return their differences."""
    original_info = extract_info_func(original_obj, include_mxcell=True)
    changed_info = extract_info_func(changed_obj, include_mxcell=True)
    
    differences = {}
    
    # Compare regular attributes
    for key in set(original_info.keys()) - {'mxCell'}:
        if original_info.get(key) != changed_info.get(key):
            differences[key] = {
                'from': original_info.get(key),
                'to': changed_info.get(key)
            }
    
    # Compare mxCell elements if they exist
    original_mxcell = original_obj.find('mxCell')
    changed_mxcell = changed_obj.find('mxCell')
    mxcell_differences = compare_mxcells(original_mxcell, changed_mxcell)
    
    if mxcell_differences:
        differences['mxCell'] = mxcell_differences
    
    if differences:
        result = extract_info_func(changed_obj, include_mxcell=False)  # Get current state without mxCell
        result['changes'] = differences
        return result
    return None

def get_objects_by_type(root, object_type):
    """Get all objects of a specific type from the XML root."""
    if object_type == 'generic':
        return [elem for elem in root.findall(".//object") 
                if elem.get('factSheetType') is None 
                and elem.get('dependencyRelation') is None
                and elem.get('label') is not None]  # Must have a label to be a valid generic object
    else:
        return [elem for elem in root.findall(".//object") 
                if object_type == 'factSheet' and elem.get('factSheetType') is not None
                or object_type == 'relation' and elem.get('dependencyRelation') is not None]

def compare_diagrams(original_xml_path, changed_xml_path):
    # Parse XML files
    original_tree = ET.parse(original_xml_path)
    changed_tree = ET.parse(changed_xml_path)
    
    original_root = original_tree.getroot()
    changed_root = changed_tree.getroot()
    
    # Get standalone mxCells (direct children of root/1)
    original_cells = original_root.findall(".//root/mxCell[@id!='0'][@id!='1']") + original_root.findall(".//root/mxCell[@value]")
    changed_cells = changed_root.findall(".//root/mxCell[@id!='0'][@id!='1']") + changed_root.findall(".//root/mxCell[@value]")
    
    # Create dictionaries for standalone mxCells
    original_cells_by_id = {elem.get('id'): elem for elem in original_cells}
    changed_cells_by_id = {elem.get('id'): elem for elem in changed_cells}
    
    # Get fact sheets, relations, and generic objects from both XMLs
    original_fact_sheets = get_objects_by_type(original_root, 'factSheet')
    changed_fact_sheets = get_objects_by_type(changed_root, 'factSheet')
    original_relations = get_objects_by_type(original_root, 'relation')
    changed_relations = get_objects_by_type(changed_root, 'relation')
    original_generic_objects = get_objects_by_type(original_root, 'generic')
    changed_generic_objects = get_objects_by_type(changed_root, 'generic')
    
    # Create dictionaries for easy lookup by ID
    original_fact_sheets_by_id = {elem.get('id'): elem for elem in original_fact_sheets}
    changed_fact_sheets_by_id = {elem.get('id'): elem for elem in changed_fact_sheets}
    original_relations_by_id = {elem.get('id'): elem for elem in original_relations}
    changed_relations_by_id = {elem.get('id'): elem for elem in changed_relations}
    original_generic_by_id = {elem.get('id'): elem for elem in original_generic_objects}
    changed_generic_by_id = {elem.get('id'): elem for elem in changed_generic_objects}
    
    # Create dictionaries for factSheetId/relationId lookup for added/removed detection
    original_fact_sheets_by_fs_id = {elem.get('factSheetId'): elem for elem in original_fact_sheets}
    changed_fact_sheets_by_fs_id = {elem.get('factSheetId'): elem for elem in changed_fact_sheets}
    original_relations_by_rel_id = {elem.get('relationId'): elem for elem in original_relations}
    changed_relations_by_rel_id = {elem.get('relationId'): elem for elem in changed_relations}
    
    # Find added and removed fact sheets (based on factSheetId)
    added_fact_sheet_ids = set(changed_fact_sheets_by_fs_id.keys()) - set(original_fact_sheets_by_fs_id.keys())
    removed_fact_sheet_ids = set(original_fact_sheets_by_fs_id.keys()) - set(changed_fact_sheets_by_fs_id.keys())
    
    # Find added and removed relations (based on relationId)
    added_relation_ids = set(changed_relations_by_rel_id.keys()) - set(original_relations_by_rel_id.keys())
    removed_relation_ids = set(original_relations_by_rel_id.keys()) - set(changed_relations_by_rel_id.keys())
    
    # Find added and removed generic objects (based on object id)
    added_generic_ids = set(changed_generic_by_id.keys()) - set(original_generic_by_id.keys())
    removed_generic_ids = set(original_generic_by_id.keys()) - set(changed_generic_by_id.keys())
    
    # Find added and removed standalone mxCells
    added_cell_ids = set(changed_cells_by_id.keys()) - set(original_cells_by_id.keys())
    removed_cell_ids = set(original_cells_by_id.keys()) - set(changed_cells_by_id.keys())
    common_cell_ids = set(original_cells_by_id.keys()) & set(changed_cells_by_id.keys())
    
    # Find common objects by their object id
    common_fact_sheet_ids = set(original_fact_sheets_by_id.keys()) & set(changed_fact_sheets_by_id.keys())
    common_relation_ids = set(original_relations_by_id.keys()) & set(changed_relations_by_id.keys())
    common_generic_ids = set(original_generic_by_id.keys()) & set(changed_generic_by_id.keys())
    
    # Create result lists
    added_fact_sheets = [extract_fact_sheet_info(changed_fact_sheets_by_fs_id[id]) 
                        for id in added_fact_sheet_ids]
    removed_fact_sheets = [extract_fact_sheet_info(original_fact_sheets_by_fs_id[id]) 
                          for id in removed_fact_sheet_ids]
    added_relations = [extract_relation_info(changed_relations_by_rel_id[id]) 
                      for id in added_relation_ids]
    removed_relations = [extract_relation_info(original_relations_by_rel_id[id]) 
                        for id in removed_relation_ids]
    added_objects = [extract_generic_object_info(changed_generic_by_id[id])
                    for id in added_generic_ids]
    removed_objects = [extract_generic_object_info(original_generic_by_id[id])
                      for id in removed_generic_ids]
    added_cells = [extract_standalone_mxcell_info(changed_cells_by_id[id])
                  for id in added_cell_ids]
    removed_cells = [extract_standalone_mxcell_info(original_cells_by_id[id])
                    for id in removed_cell_ids]
    
    # Find changed fact sheets and relations (comparing by object id)
    changed_fact_sheets = []
    for id in common_fact_sheet_ids:
        diff = compare_objects(original_fact_sheets_by_id[id], 
                             changed_fact_sheets_by_id[id],
                             extract_fact_sheet_info)
        if diff:
            changed_fact_sheets.append(diff)
    
    changed_relations = []
    for id in common_relation_ids:
        diff = compare_objects(original_relations_by_id[id],
                             changed_relations_by_id[id],
                             extract_relation_info)
        if diff:
            changed_relations.append(diff)
            
    changed_objects = []
    for id in common_generic_ids:
        diff = compare_objects(original_generic_by_id[id],
                             changed_generic_by_id[id],
                             extract_generic_object_info)
        if diff:
            changed_objects.append(diff)
            
    # Find changed standalone mxCells
    changed_cells = []
    for id in common_cell_ids:
        original_info = extract_standalone_mxcell_info(original_cells_by_id[id])
        changed_info = extract_standalone_mxcell_info(changed_cells_by_id[id])
        
        differences = {}
        for key in set(original_info.keys()) | set(changed_info.keys()):
            if original_info.get(key) != changed_info.get(key):
                if isinstance(original_info.get(key), dict) and isinstance(changed_info.get(key), dict):
                    # Handle nested geometry differences
                    geo_diff = {}
                    for geo_key in set(original_info[key].keys()) | set(changed_info[key].keys()):
                        if original_info[key].get(geo_key) != changed_info[key].get(geo_key):
                            geo_diff[geo_key] = {
                                'from': original_info[key].get(geo_key),
                                'to': changed_info[key].get(geo_key)
                            }
                    if geo_diff:
                        differences[key] = geo_diff
                else:
                    differences[key] = {
                        'from': original_info.get(key),
                        'to': changed_info.get(key)
                    }
        
        if differences:
            result = changed_info.copy()
            result['changes'] = differences
            changed_cells.append(result)
    
    # Create result dictionary
    result = {
        'addedFactSheets': added_fact_sheets,
        'removedFactSheets': removed_fact_sheets,
        'changedFactSheets': changed_fact_sheets,
        'addedRelations': added_relations,
        'removedRelations': removed_relations,
        'changedRelations': changed_relations,
        'addedObjects': added_objects,
        'removedObjects': removed_objects,
        'changedObjects': changed_objects,
        'addedCells': added_cells,
        'removedCells': removed_cells,
        'changedCells': changed_cells
    }
    
    return result

def main():
    # Get the directory containing the files
    input_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'files/input')
    changes_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'files')
    
    # Compare diagrams and get changes
    changes = compare_diagrams(
        os.path.join(input_dir, 'original.xml'),
        os.path.join(input_dir, 'changed.xml')
    )
    
    # Write results to JSON file
    with open(os.path.join(changes_dir, 'diagram_changes.json'), 'w', encoding='utf-8') as f:
        json.dump(changes, f, indent=2)

if __name__ == '__main__':
    main()
