
from graphviz import Digraph
import csv
from collections import defaultdict


# Define keywords for each category
categories = {
    'Contracts': ['contract'],
    'Drawings': ['drawing', 'spec'],
    'Reports': ['report'],
    'Meeting Minutes': ['meeting minute'],
    'Manuals': ['manual'],
    'Financials': ['financial', 'allowance log', 'billing', 'forecast', 'pay app', 'submittal', 'log', 'xls', 'xlsx', 'xlsm'],
    'Schedules': ['schedule', 'mpp'],
    'Correspondence': ['correspondence', 'msg'],
}





# Use the latest CSV file
csv_path = 'DocLabs_Sample_Project_Template/file_inventory_DocLabs_Sample_Project_Template_20250920_220124.csv'

# Build nested dict: FirstLevelFolder -> File Type -> Business Category -> count
hierarchy = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

import os

def get_first_level_folder(folder_path, root_folder):
    # Remove root_folder prefix
    rel = os.path.relpath(folder_path, root_folder)
    # The first part is the first-level folder
    first = rel.split(os.sep)[0]
    # If rel is '.' (root), return root_folder
    if rel == '.' or not first or first.startswith('.'):
        return root_folder
    # Only include folders starting with 01. to 10.
    if first[:3] in [f"0{i}." for i in range(1,10)] + ["10."]:
        return first
    return None

root_folder = '/Users/venkateshtadinada/Documents/VS-Code-Projects/folder-kb/DocLabs_Sample_Project_Template'

with open(csv_path, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    debug_count = 0
    for row in reader:
        folder = row['directory'] if 'directory' in row else row['parent'] if 'parent' in row else ''
        first_level = get_first_level_folder(folder, root_folder)
        ext = row.get('ext', '').upper()
        if not ext:
            filename = row.get('filename', '')
            if '.' in filename:
                ext = filename.split('.')[-1].upper()
            else:
                ext = ''
        path = (row['full_path'] + ' ' + row['filename']).lower()
        cat_found = None
        for cat, keywords in categories.items():
            if any(kw in path for kw in keywords):
                cat_found = cat
                break
        if debug_count < 10:
            print(f"Row {debug_count}: first_level='{first_level}', ext='{ext}', cat_found='{cat_found}', filename='{row.get('filename','')}'")
            debug_count += 1
        if first_level and ext and cat_found:
            hierarchy[first_level][ext][cat_found] += 1

# Draw hierarchical diagram: Folder -> File Types -> Business Categories
dot_hier = Digraph(comment='Project File Hierarchy')
dot_hier.node('root', 'File Inventory', shape='diamond', style='filled', color='gold')



# Draw only root and first-level folders (01. to 10.)
dot_hier.node('root', 'File Inventory', shape='diamond', style='filled', color='gold')
for first_level, ftypes in hierarchy.items():
    if first_level == root_folder:
        folder_label = os.path.basename(root_folder)
    else:
        folder_label = first_level
    folder_node = f"folder_{abs(hash(first_level))}"
    dot_hier.node(folder_node, folder_label, shape='ellipse', style='filled', color='lightgreen')
    dot_hier.edge('root', folder_node, label='in folder')
    for ftype, cats in ftypes.items():
        ftype_node = f"{folder_node}_type_{ftype}"
        ftype_label = f"{ftype} ({sum(cats.values())})"
        dot_hier.node(ftype_node, ftype_label, shape='box', style='filled', color='lightblue')
        dot_hier.edge(folder_node, ftype_node, label='has type')
        for cat, count in cats.items():
            cat_node = f"{ftype_node}_{cat.replace(' ', '_')}"
            cat_label = f"{cat} ({count})"
            dot_hier.node(cat_node, cat_label, shape='box', style='filled', color='lightyellow')
            dot_hier.edge(ftype_node, cat_node, label='is')

dot_hier.render('file_hierarchy_diagram', format='png', view=True)