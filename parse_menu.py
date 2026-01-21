#!/usr/bin/env python3
"""Parse McDonald's menu CSV and create hierarchical structure."""

import csv
import json
import re
from collections import defaultdict

# Size indicators that should create separate base items
SIZE_INDICATORS = {'Small', 'Medium', 'Large', 'Child', 'Snack', 'Regular Biscuit', 'Large Biscuit', 
                   '4 piece', '6 piece', '10 piece', '20 piece', '40 piece'}

def extract_parentheses_info(item):
    """Extract info from parentheses and determine if it's a size"""
    matches = re.findall(r'\(([^)]+)\)', item)
    if not matches:
        return None, item, False
    
    # Get the last parentheses (most specific)
    paren_info = matches[-1]
    base_item = item.rsplit(f'({paren_info})', 1)[0].strip()
    
    # Check if it's a size indicator
    is_size = paren_info in SIZE_INDICATORS
    
    return paren_info, base_item, is_size

def find_base_name(item):
    """Find the base name of an item, handling variations"""
    # Remove size info first
    paren_info, base_name, is_size = extract_parentheses_info(item)
    
    # Remove 'with' clauses
    if ' with ' in base_name:
        parts = base_name.split(' with ', 1)
        if len(parts) > 0:
            base_name = parts[0].strip()
    if ' without ' in base_name:
        parts = base_name.split(' without ', 1)
        if len(parts) > 0:
            base_name = parts[0].strip()
    
    return base_name, paren_info if is_size else None

# Read CSV
menu_data = defaultdict(list)
with open('menus/mcdonalds/mcdonalds-menu-items.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        category = row['Category']
        item = row['Item']
        menu_data[category].append(item)

hierarchy = {}
for category, items in menu_data.items():
    # Group items by base name and size
    base_groups = defaultdict(lambda: {'base': None, 'variations': []})
    
    for item in items:
        base_name, size_info = find_base_name(item)
        key = (base_name, size_info)
        
        # Determine if this is a variation or base
        if ' with ' in item or (' without ' in item and size_info is None):
            # This is a variation
            base_groups[key]['variations'].append(item)
        else:
            # This is a base item (or could be)
            if base_groups[key]['base'] is None:
                base_groups[key]['base'] = item
    
    # Build final structure
    category_dict = {}
    
    for (base_name, size_info), group_data in base_groups.items():
        # Determine full base name
        if size_info:
            full_base_name = f"{base_name} ({size_info})"
        else:
            # Use the actual base item if available, otherwise construct
            if group_data['base']:
                full_base_name = group_data['base']
            else:
                full_base_name = base_name
        
        # Extract variations
        variations = []
        for var_item in group_data.get('variations', []):
            var_paren, var_base, var_is_size = extract_parentheses_info(var_item)
            
            if ' with ' in var_item:
                parts = var_item.split(' with ', 1)
                if len(parts) > 1:
                    variation = parts[1]
                    # Remove size info if it matches
                    if size_info and f'({size_info})' in variation:
                        variation = variation.replace(f'({size_info})', '').strip()
                    variations.append(variation)
            elif ' without ' in var_item:
                parts = var_item.split(' without ', 1)
                if len(parts) > 1:
                    variation = parts[1]
                    if size_info and f'({size_info})' in variation:
                        variation = variation.replace(f'({size_info})', '').strip()
                    variations.append(f"without {variation}")
        
        # Remove duplicates and sort
        variations = sorted(list(set(variations)))
        category_dict[full_base_name] = variations
    
    # Handle items that might be variations of items with different sizes
    # For example: "Sausage Biscuit with Egg (Regular Biscuit)" -> base: "Sausage Biscuit (Regular Biscuit)"
    final_dict = category_dict.copy()
    processed_items = set(category_dict.keys())
    
    # Check for cross-size variations
    for item in items:
        if item in processed_items:
            continue
        
        # Try to match to existing base
        item_paren, item_base, item_is_size = extract_parentheses_info(item)
        
        for base in list(final_dict.keys()):
            base_paren, base_base, base_is_size = extract_parentheses_info(base)
            
            # Check if item is a variation of this base
            if base_is_size and item_is_size and base_paren == item_paren:
                # Same size, check if base names match
                if item_base.startswith(base_base + ' with'):
                    parts = item.split(' with ', 1)
                    if len(parts) > 1:
                        variation = parts[1]
                        if base_paren and f'({base_paren})' in variation:
                            variation = variation.replace(f'({base_paren})', '').strip()
                        if variation not in final_dict[base]:
                            final_dict[base].append(variation)
                        processed_items.add(item)
                        break
            elif not base_is_size and not item_is_size:
                # Neither has size, check if item is variation
                if item_base.startswith(base_base + ' with'):
                    parts = item.split(' with ', 1)
                    if len(parts) > 1:
                        variation = parts[1]
                        if variation not in final_dict[base]:
                            final_dict[base].append(variation)
                        processed_items.add(item)
                        break
        
        # If still not processed, add as standalone
        if item not in processed_items:
            final_dict[item] = []
            processed_items.add(item)
    
    # Sort variations
    for base in final_dict:
        final_dict[base] = sorted(final_dict[base])
    
    hierarchy[category] = dict(sorted(final_dict.items()))

# Save JSON
with open('menus/mcdonalds/menu-structure.json', 'w') as f:
    json.dump(hierarchy, f, indent=2)

print("JSON file created successfully!")
print(f"Categories: {list(hierarchy.keys())}")
