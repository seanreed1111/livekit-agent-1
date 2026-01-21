# McDonald's Menu Structure

This document shows the hierarchical structure of the McDonald's menu, organized by category, base items, and their possible variations.

## Menu Hierarchy

The menu is organized into the following structure:
- **Categories** (top level): Main menu sections
- **Base Items**: Individual menu items
- **Variations**: Modifications and additions available for each base item

## Mermaid Graphs

The mermaid graphs below were generated using the following Python code:

```python
import json
import re

# Load the JSON structure
with open('menus/mcdonalds/menu-structure.json', 'r') as f:
    hierarchy = json.load(f)

def sanitize_node_id(text):
    """Convert text to valid mermaid node ID"""
    # Remove special characters, replace spaces with underscores
    node_id = re.sub(r'[^a-zA-Z0-9_]', '_', text)
    # Remove consecutive underscores
    node_id = re.sub(r'_+', '_', node_id)
    # Remove leading/trailing underscores
    node_id = node_id.strip('_')
    return node_id

def create_mermaid_graph_for_category(category, items):
    """Create mermaid graph for a single category"""
    lines = ["graph TD"]
    
    # Create category node
    cat_id = sanitize_node_id(category)
    lines.append(f"    {cat_id}[\"{category}\"]")
    
    # Create base items and variations
    for base_item, variations in items.items():
        base_id = sanitize_node_id(base_item)
        
        # Create base item node
        lines.append(f"    {base_id}[\"{base_item}\"]")
        # Connect category to base item
        lines.append(f"    {cat_id} --> {base_id}")
        
        # Create variation nodes
        for variation in variations:
            var_id = sanitize_node_id(f"{base_item}_{variation}")
            var_display = f"add {variation}" if not variation.startswith("without") else variation
            lines.append(f"    {var_id}[\"{var_display}\"]")
            # Connect base item to variation
            lines.append(f"    {base_id} --> {var_id}")
    
    return "\n".join(lines)

# Generate graphs for each category
for category, items in hierarchy.items():
    graph = create_mermaid_graph_for_category(category, items)
    print(f"## {category}\n")
    print("```mermaid")
    print(graph)
    print("```\n")
```

### Breakfast

```mermaid
graph TD
    Breakfast["Breakfast"]
    Bacon["Bacon"]
    Breakfast --> Bacon
    Big_Breakfast_Large_Biscuit["Big Breakfast (Large Biscuit)"]
    Breakfast --> Big_Breakfast_Large_Biscuit
    Big_Breakfast_Large_Biscuit_Egg_Whites["add Egg Whites"]
    Big_Breakfast_Large_Biscuit --> Big_Breakfast_Large_Biscuit_Egg_Whites
    Big_Breakfast_Large_Biscuit_Hotcakes["add Hotcakes"]
    Big_Breakfast_Large_Biscuit --> Big_Breakfast_Large_Biscuit_Hotcakes
    Big_Breakfast_Large_Biscuit_Hotcakes_and_Egg_Whites["add Hotcakes and Egg Whites"]
    Big_Breakfast_Large_Biscuit --> Big_Breakfast_Large_Biscuit_Hotcakes_and_Egg_Whites
    Big_Breakfast_Regular_Biscuit["Big Breakfast (Regular Biscuit)"]
    Breakfast --> Big_Breakfast_Regular_Biscuit
    Big_Breakfast_Regular_Biscuit_Egg_Whites["add Egg Whites"]
    Big_Breakfast_Regular_Biscuit --> Big_Breakfast_Regular_Biscuit_Egg_Whites
    Big_Breakfast_Regular_Biscuit_Hotcakes["add Hotcakes"]
    Big_Breakfast_Regular_Biscuit --> Big_Breakfast_Regular_Biscuit_Hotcakes
    Big_Breakfast_Regular_Biscuit_Hotcakes_and_Egg_Whites["add Hotcakes and Egg Whites"]
    Big_Breakfast_Regular_Biscuit --> Big_Breakfast_Regular_Biscuit_Hotcakes_and_Egg_Whites
    Cinnamon_Melts["Cinnamon Melts"]
    Breakfast --> Cinnamon_Melts
    Egg_McMuffin["Egg McMuffin"]
    Breakfast --> Egg_McMuffin
    Egg_White_Delight["Egg White Delight"]
    Breakfast --> Egg_White_Delight
    Fruit_Maple_Oatmeal["Fruit & Maple Oatmeal"]
    Breakfast --> Fruit_Maple_Oatmeal
    Fruit_Maple_Oatmeal_without_Brown_Sugar["without Brown Sugar"]
    Fruit_Maple_Oatmeal --> Fruit_Maple_Oatmeal_without_Brown_Sugar
    Fruit_Maple_Oatmeal_without_Brown_Sugar["Fruit & Maple Oatmeal without Brown Sugar"]
    Breakfast --> Fruit_Maple_Oatmeal_without_Brown_Sugar
    Hash_Brown["Hash Brown"]
    Breakfast --> Hash_Brown
    Hotcakes["Hotcakes"]
    Breakfast --> Hotcakes
    Hotcakes_and_Sausage["Hotcakes and Sausage"]
    Breakfast --> Hotcakes_and_Sausage
    Sausage["Sausage"]
    Breakfast --> Sausage
    Sausage_Biscuit_Large_Biscuit["Sausage Biscuit (Large Biscuit)"]
    Breakfast --> Sausage_Biscuit_Large_Biscuit
    Sausage_Biscuit_Large_Biscuit_Egg["add Egg"]
    Sausage_Biscuit_Large_Biscuit --> Sausage_Biscuit_Large_Biscuit_Egg
    Sausage_Biscuit_Large_Biscuit_Egg_Whites["add Egg Whites"]
    Sausage_Biscuit_Large_Biscuit --> Sausage_Biscuit_Large_Biscuit_Egg_Whites
    Sausage_Biscuit_Regular_Biscuit["Sausage Biscuit (Regular Biscuit)"]
    Breakfast --> Sausage_Biscuit_Regular_Biscuit
    Sausage_Biscuit_Regular_Biscuit_Egg["add Egg"]
    Sausage_Biscuit_Regular_Biscuit --> Sausage_Biscuit_Regular_Biscuit_Egg
    Sausage_Biscuit_Regular_Biscuit_Egg_Whites["add Egg Whites"]
    Sausage_Biscuit_Regular_Biscuit --> Sausage_Biscuit_Regular_Biscuit_Egg_Whites
    Sausage_Burrito["Sausage Burrito"]
    Breakfast --> Sausage_Burrito
    Sausage_McGriddles["Sausage McGriddles"]
    Breakfast --> Sausage_McGriddles
    Sausage_McMuffin["Sausage McMuffin"]
    Breakfast --> Sausage_McMuffin
    Sausage_McMuffin_Egg["add Egg"]
    Sausage_McMuffin --> Sausage_McMuffin_Egg
    Sausage_McMuffin_Egg_Whites["add Egg Whites"]
    Sausage_McMuffin --> Sausage_McMuffin_Egg_Whites
    Southern_Style_Chicken_Biscuit_Large_Biscuit["Southern Style Chicken Biscuit (Large Biscuit)"]
    Breakfast --> Southern_Style_Chicken_Biscuit_Large_Biscuit
    Southern_Style_Chicken_Biscuit_Regular_Biscuit["Southern Style Chicken Biscuit (Regular Biscuit)"]
    Breakfast --> Southern_Style_Chicken_Biscuit_Regular_Biscuit
    Steak["Steak"]
    Breakfast --> Steak
    Steak_Egg_Biscuit_Regular_Biscuit["Steak & Egg Biscuit (Regular Biscuit)"]
    Breakfast --> Steak_Egg_Biscuit_Regular_Biscuit
    Steak_Egg_McMuffin["Steak & Egg McMuffin"]
    Breakfast --> Steak_Egg_McMuffin
```


### Beef & Pork

```mermaid
graph TD
    Beef_Pork["Beef & Pork"]
    Bacon_Clubhouse_Burger["Bacon Clubhouse Burger"]
    Beef_Pork --> Bacon_Clubhouse_Burger
    Bacon_McDouble["Bacon McDouble"]
    Beef_Pork --> Bacon_McDouble
    Big_Mac["Big Mac"]
    Beef_Pork --> Big_Mac
    Cheeseburger["Cheeseburger"]
    Beef_Pork --> Cheeseburger
    Daily_Double["Daily Double"]
    Beef_Pork --> Daily_Double
    Double_Cheeseburger["Double Cheeseburger"]
    Beef_Pork --> Double_Cheeseburger
    Double_Quarter_Pounder["Double Quarter Pounder"]
    Beef_Pork --> Double_Quarter_Pounder
    Double_Quarter_Pounder_Cheese["add Cheese"]
    Double_Quarter_Pounder --> Double_Quarter_Pounder_Cheese
    Hamburger["Hamburger"]
    Beef_Pork --> Hamburger
    Jalape_o_Double["Jalapeño Double"]
    Beef_Pork --> Jalape_o_Double
    McDouble["McDouble"]
    Beef_Pork --> McDouble
    McRib["McRib"]
    Beef_Pork --> McRib
    Quarter_Pounder["Quarter Pounder"]
    Beef_Pork --> Quarter_Pounder
    Quarter_Pounder_Bacon_Cheese["add Bacon & Cheese"]
    Quarter_Pounder --> Quarter_Pounder_Bacon_Cheese
    Quarter_Pounder_Bacon_Habanero_Ranch["add Bacon Habanero Ranch"]
    Quarter_Pounder --> Quarter_Pounder_Bacon_Habanero_Ranch
    Quarter_Pounder_Cheese["add Cheese"]
    Quarter_Pounder --> Quarter_Pounder_Cheese
    Quarter_Pounder_Deluxe["Quarter Pounder Deluxe"]
    Beef_Pork --> Quarter_Pounder_Deluxe
```


### Chicken & Fish

```mermaid
graph TD
    Chicken_Fish["Chicken & Fish"]
    Bacon_Buffalo_Ranch_McChicken["Bacon Buffalo Ranch McChicken"]
    Chicken_Fish --> Bacon_Buffalo_Ranch_McChicken
    Bacon_Cheddar_McChicken["Bacon Cheddar McChicken"]
    Chicken_Fish --> Bacon_Cheddar_McChicken
    Bacon_Clubhouse_Crispy_Chicken_Sandwich["Bacon Clubhouse Crispy Chicken Sandwich"]
    Chicken_Fish --> Bacon_Clubhouse_Crispy_Chicken_Sandwich
    Bacon_Clubhouse_Grilled_Chicken_Sandwich["Bacon Clubhouse Grilled Chicken Sandwich"]
    Chicken_Fish --> Bacon_Clubhouse_Grilled_Chicken_Sandwich
    Buffalo_Ranch_McChicken["Buffalo Ranch McChicken"]
    Chicken_Fish --> Buffalo_Ranch_McChicken
    Chicken_McNuggets_10_piece["Chicken McNuggets (10 piece)"]
    Chicken_Fish --> Chicken_McNuggets_10_piece
    Chicken_McNuggets_20_piece["Chicken McNuggets (20 piece)"]
    Chicken_Fish --> Chicken_McNuggets_20_piece
    Chicken_McNuggets_4_piece["Chicken McNuggets (4 piece)"]
    Chicken_Fish --> Chicken_McNuggets_4_piece
    Chicken_McNuggets_40_piece["Chicken McNuggets (40 piece)"]
    Chicken_Fish --> Chicken_McNuggets_40_piece
    Chicken_McNuggets_6_piece["Chicken McNuggets (6 piece)"]
    Chicken_Fish --> Chicken_McNuggets_6_piece
    Filet_O_Fish["Filet-O-Fish"]
    Chicken_Fish --> Filet_O_Fish
    McChicken["McChicken"]
    Chicken_Fish --> McChicken
    Premium_Crispy_Chicken_Classic_Sandwich["Premium Crispy Chicken Classic Sandwich"]
    Chicken_Fish --> Premium_Crispy_Chicken_Classic_Sandwich
    Premium_Crispy_Chicken_Club_Sandwich["Premium Crispy Chicken Club Sandwich"]
    Chicken_Fish --> Premium_Crispy_Chicken_Club_Sandwich
    Premium_Crispy_Chicken_Ranch_BLT_Sandwich["Premium Crispy Chicken Ranch BLT Sandwich"]
    Chicken_Fish --> Premium_Crispy_Chicken_Ranch_BLT_Sandwich
    Premium_Grilled_Chicken_Classic_Sandwich["Premium Grilled Chicken Classic Sandwich"]
    Chicken_Fish --> Premium_Grilled_Chicken_Classic_Sandwich
    Premium_Grilled_Chicken_Club_Sandwich["Premium Grilled Chicken Club Sandwich"]
    Chicken_Fish --> Premium_Grilled_Chicken_Club_Sandwich
    Premium_Grilled_Chicken_Ranch_BLT_Sandwich["Premium Grilled Chicken Ranch BLT Sandwich"]
    Chicken_Fish --> Premium_Grilled_Chicken_Ranch_BLT_Sandwich
    Premium_McWrap_Chicken_Bacon_Crispy_Chicken["Premium McWrap Chicken & Bacon (Crispy Chicken)"]
    Chicken_Fish --> Premium_McWrap_Chicken_Bacon_Crispy_Chicken
    Premium_McWrap_Chicken_Bacon_Grilled_Chicken["Premium McWrap Chicken & Bacon (Grilled Chicken)"]
    Chicken_Fish --> Premium_McWrap_Chicken_Bacon_Grilled_Chicken
    Premium_McWrap_Chicken_Ranch_Crispy_Chicken["Premium McWrap Chicken & Ranch (Crispy Chicken)"]
    Chicken_Fish --> Premium_McWrap_Chicken_Ranch_Crispy_Chicken
    Premium_McWrap_Chicken_Ranch_Grilled_Chicken["Premium McWrap Chicken & Ranch (Grilled Chicken)"]
    Chicken_Fish --> Premium_McWrap_Chicken_Ranch_Grilled_Chicken
    Premium_McWrap_Chicken_Sweet_Chili_Crispy_Chicken["Premium McWrap Chicken Sweet Chili (Crispy Chicken)"]
    Chicken_Fish --> Premium_McWrap_Chicken_Sweet_Chili_Crispy_Chicken
    Premium_McWrap_Chicken_Sweet_Chili_Grilled_Chicken["Premium McWrap Chicken Sweet Chili (Grilled Chicken)"]
    Chicken_Fish --> Premium_McWrap_Chicken_Sweet_Chili_Grilled_Chicken
    Premium_McWrap_Southwest_Chicken_Crispy_Chicken["Premium McWrap Southwest Chicken (Crispy Chicken)"]
    Chicken_Fish --> Premium_McWrap_Southwest_Chicken_Crispy_Chicken
    Premium_McWrap_Southwest_Chicken_Grilled_Chicken["Premium McWrap Southwest Chicken (Grilled Chicken)"]
    Chicken_Fish --> Premium_McWrap_Southwest_Chicken_Grilled_Chicken
    Southern_Style_Crispy_Chicken_Sandwich["Southern Style Crispy Chicken Sandwich"]
    Chicken_Fish --> Southern_Style_Crispy_Chicken_Sandwich
```


### Salads

```mermaid
graph TD
    Salads["Salads"]
    Premium_Bacon_Ranch_Salad_without_Chicken["Premium Bacon Ranch Salad (without Chicken)"]
    Salads --> Premium_Bacon_Ranch_Salad_without_Chicken
    Premium_Bacon_Ranch_Salad_without_Chicken_Crispy_Chicken["add Crispy Chicken"]
    Premium_Bacon_Ranch_Salad_without_Chicken --> Premium_Bacon_Ranch_Salad_without_Chicken_Crispy_Chicken
    Premium_Bacon_Ranch_Salad_without_Chicken_Grilled_Chicken["add Grilled Chicken"]
    Premium_Bacon_Ranch_Salad_without_Chicken --> Premium_Bacon_Ranch_Salad_without_Chicken_Grilled_Chicken
    Premium_Southwest_Salad_without_Chicken["Premium Southwest Salad (without Chicken)"]
    Salads --> Premium_Southwest_Salad_without_Chicken
    Premium_Southwest_Salad_without_Chicken_Crispy_Chicken["add Crispy Chicken"]
    Premium_Southwest_Salad_without_Chicken --> Premium_Southwest_Salad_without_Chicken_Crispy_Chicken
    Premium_Southwest_Salad_without_Chicken_Grilled_Chicken["add Grilled Chicken"]
    Premium_Southwest_Salad_without_Chicken --> Premium_Southwest_Salad_without_Chicken_Grilled_Chicken
```


### Snacks & Sides

```mermaid
graph TD
    Snacks_Sides["Snacks & Sides"]
    Apple_Slices["Apple Slices"]
    Snacks_Sides --> Apple_Slices
    Chipotle_BBQ_Snack_Wrap_Crispy_Chicken["Chipotle BBQ Snack Wrap (Crispy Chicken)"]
    Snacks_Sides --> Chipotle_BBQ_Snack_Wrap_Crispy_Chicken
    Chipotle_BBQ_Snack_Wrap_Grilled_Chicken["Chipotle BBQ Snack Wrap (Grilled Chicken)"]
    Snacks_Sides --> Chipotle_BBQ_Snack_Wrap_Grilled_Chicken
    Fruit_n_Yogurt_Parfait["Fruit n Yogurt Parfait"]
    Snacks_Sides --> Fruit_n_Yogurt_Parfait
    Honey_Mustard_Snack_Wrap_Crispy_Chicken["Honey Mustard Snack Wrap (Crispy Chicken)"]
    Snacks_Sides --> Honey_Mustard_Snack_Wrap_Crispy_Chicken
    Honey_Mustard_Snack_Wrap_Grilled_Chicken["Honey Mustard Snack Wrap (Grilled Chicken)"]
    Snacks_Sides --> Honey_Mustard_Snack_Wrap_Grilled_Chicken
    Kids_French_Fries["Kids French Fries"]
    Snacks_Sides --> Kids_French_Fries
    Large_French_Fries["Large French Fries"]
    Snacks_Sides --> Large_French_Fries
    Medium_French_Fries["Medium French Fries"]
    Snacks_Sides --> Medium_French_Fries
    Ranch_Snack_Wrap_Crispy_Chicken["Ranch Snack Wrap (Crispy Chicken)"]
    Snacks_Sides --> Ranch_Snack_Wrap_Crispy_Chicken
    Ranch_Snack_Wrap_Grilled_Chicken["Ranch Snack Wrap (Grilled Chicken)"]
    Snacks_Sides --> Ranch_Snack_Wrap_Grilled_Chicken
    Side_Salad["Side Salad"]
    Snacks_Sides --> Side_Salad
    Small_French_Fries["Small French Fries"]
    Snacks_Sides --> Small_French_Fries
```


### Desserts

```mermaid
graph TD
    Desserts["Desserts"]
    Baked_Apple_Pie["Baked Apple Pie"]
    Desserts --> Baked_Apple_Pie
    Chocolate_Chip_Cookie["Chocolate Chip Cookie"]
    Desserts --> Chocolate_Chip_Cookie
    Hot_Caramel_Sundae["Hot Caramel Sundae"]
    Desserts --> Hot_Caramel_Sundae
    Hot_Fudge_Sundae["Hot Fudge Sundae"]
    Desserts --> Hot_Fudge_Sundae
    Kids_Ice_Cream_Cone["Kids Ice Cream Cone"]
    Desserts --> Kids_Ice_Cream_Cone
    Oatmeal_Raisin_Cookie["Oatmeal Raisin Cookie"]
    Desserts --> Oatmeal_Raisin_Cookie
    Strawberry_Sundae["Strawberry Sundae"]
    Desserts --> Strawberry_Sundae
```


### Beverages

```mermaid
graph TD
    Beverages["Beverages"]
    1_Low_Fat_Milk_Jug["1% Low Fat Milk Jug"]
    Beverages --> 1_Low_Fat_Milk_Jug
    Coca_Cola_Classic_Child["Coca-Cola Classic (Child)"]
    Beverages --> Coca_Cola_Classic_Child
    Coca_Cola_Classic_Large["Coca-Cola Classic (Large)"]
    Beverages --> Coca_Cola_Classic_Large
    Coca_Cola_Classic_Medium["Coca-Cola Classic (Medium)"]
    Beverages --> Coca_Cola_Classic_Medium
    Coca_Cola_Classic_Small["Coca-Cola Classic (Small)"]
    Beverages --> Coca_Cola_Classic_Small
    Dasani_Water_Bottle["Dasani Water Bottle"]
    Beverages --> Dasani_Water_Bottle
    Diet_Coke_Child["Diet Coke (Child)"]
    Beverages --> Diet_Coke_Child
    Diet_Coke_Large["Diet Coke (Large)"]
    Beverages --> Diet_Coke_Large
    Diet_Coke_Medium["Diet Coke (Medium)"]
    Beverages --> Diet_Coke_Medium
    Diet_Coke_Small["Diet Coke (Small)"]
    Beverages --> Diet_Coke_Small
    Diet_Dr_Pepper_Child["Diet Dr Pepper (Child)"]
    Beverages --> Diet_Dr_Pepper_Child
    Diet_Dr_Pepper_Large["Diet Dr Pepper (Large)"]
    Beverages --> Diet_Dr_Pepper_Large
    Diet_Dr_Pepper_Medium["Diet Dr Pepper (Medium)"]
    Beverages --> Diet_Dr_Pepper_Medium
    Diet_Dr_Pepper_Small["Diet Dr Pepper (Small)"]
    Beverages --> Diet_Dr_Pepper_Small
    Dr_Pepper_Child["Dr Pepper (Child)"]
    Beverages --> Dr_Pepper_Child
    Dr_Pepper_Large["Dr Pepper (Large)"]
    Beverages --> Dr_Pepper_Large
    Dr_Pepper_Medium["Dr Pepper (Medium)"]
    Beverages --> Dr_Pepper_Medium
    Dr_Pepper_Small["Dr Pepper (Small)"]
    Beverages --> Dr_Pepper_Small
    Fat_Free_Chocolate_Milk_Jug["Fat Free Chocolate Milk Jug"]
    Beverages --> Fat_Free_Chocolate_Milk_Jug
    Minute_Maid_100_Apple_Juice_Box["Minute Maid 100% Apple Juice Box"]
    Beverages --> Minute_Maid_100_Apple_Juice_Box
    Minute_Maid_Orange_Juice_Large["Minute Maid Orange Juice (Large)"]
    Beverages --> Minute_Maid_Orange_Juice_Large
    Minute_Maid_Orange_Juice_Medium["Minute Maid Orange Juice (Medium)"]
    Beverages --> Minute_Maid_Orange_Juice_Medium
    Minute_Maid_Orange_Juice_Small["Minute Maid Orange Juice (Small)"]
    Beverages --> Minute_Maid_Orange_Juice_Small
    Sprite_Child["Sprite (Child)"]
    Beverages --> Sprite_Child
    Sprite_Large["Sprite (Large)"]
    Beverages --> Sprite_Large
    Sprite_Medium["Sprite (Medium)"]
    Beverages --> Sprite_Medium
    Sprite_Small["Sprite (Small)"]
    Beverages --> Sprite_Small
```


### Coffee & Tea

```mermaid
graph TD
    Coffee_Tea["Coffee & Tea"]
    Caramel_Iced_Coffee_Large["Caramel Iced Coffee (Large)"]
    Coffee_Tea --> Caramel_Iced_Coffee_Large
    Caramel_Iced_Coffee_Medium["Caramel Iced Coffee (Medium)"]
    Coffee_Tea --> Caramel_Iced_Coffee_Medium
    Caramel_Iced_Coffee_Small["Caramel Iced Coffee (Small)"]
    Coffee_Tea --> Caramel_Iced_Coffee_Small
    Caramel_Latte_Large["Caramel Latte (Large)"]
    Coffee_Tea --> Caramel_Latte_Large
    Caramel_Latte_Medium["Caramel Latte (Medium)"]
    Coffee_Tea --> Caramel_Latte_Medium
    Caramel_Latte_Small["Caramel Latte (Small)"]
    Coffee_Tea --> Caramel_Latte_Small
    Caramel_Mocha_Large["Caramel Mocha (Large)"]
    Coffee_Tea --> Caramel_Mocha_Large
    Caramel_Mocha_Medium["Caramel Mocha (Medium)"]
    Coffee_Tea --> Caramel_Mocha_Medium
    Caramel_Mocha_Small["Caramel Mocha (Small)"]
    Coffee_Tea --> Caramel_Mocha_Small
    Coffee_Large["Coffee (Large)"]
    Coffee_Tea --> Coffee_Large
    Coffee_Medium["Coffee (Medium)"]
    Coffee_Tea --> Coffee_Medium
    Coffee_Small["Coffee (Small)"]
    Coffee_Tea --> Coffee_Small
    Frapp_Caramel_Large["Frappé Caramel (Large)"]
    Coffee_Tea --> Frapp_Caramel_Large
    Frapp_Caramel_Medium["Frappé Caramel (Medium)"]
    Coffee_Tea --> Frapp_Caramel_Medium
    Frapp_Caramel_Small["Frappé Caramel (Small)"]
    Coffee_Tea --> Frapp_Caramel_Small
    Frapp_Chocolate_Chip_Large["Frappé Chocolate Chip (Large)"]
    Coffee_Tea --> Frapp_Chocolate_Chip_Large
    Frapp_Chocolate_Chip_Medium["Frappé Chocolate Chip (Medium)"]
    Coffee_Tea --> Frapp_Chocolate_Chip_Medium
    Frapp_Chocolate_Chip_Small["Frappé Chocolate Chip (Small)"]
    Coffee_Tea --> Frapp_Chocolate_Chip_Small
    Frapp_Mocha_Large["Frappé Mocha (Large)"]
    Coffee_Tea --> Frapp_Mocha_Large
    Frapp_Mocha_Medium["Frappé Mocha (Medium)"]
    Coffee_Tea --> Frapp_Mocha_Medium
    Frapp_Mocha_Small["Frappé Mocha (Small)"]
    Coffee_Tea --> Frapp_Mocha_Small
    French_Vanilla_Iced_Coffee_Large["French Vanilla Iced Coffee (Large)"]
    Coffee_Tea --> French_Vanilla_Iced_Coffee_Large
    French_Vanilla_Iced_Coffee_Medium["French Vanilla Iced Coffee (Medium)"]
    Coffee_Tea --> French_Vanilla_Iced_Coffee_Medium
    French_Vanilla_Iced_Coffee_Small["French Vanilla Iced Coffee (Small)"]
    Coffee_Tea --> French_Vanilla_Iced_Coffee_Small
    French_Vanilla_Latte_Large["French Vanilla Latte (Large)"]
    Coffee_Tea --> French_Vanilla_Latte_Large
    French_Vanilla_Latte_Medium["French Vanilla Latte (Medium)"]
    Coffee_Tea --> French_Vanilla_Latte_Medium
    French_Vanilla_Latte_Small["French Vanilla Latte (Small)"]
    Coffee_Tea --> French_Vanilla_Latte_Small
    Hazelnut_Iced_Coffee_Large["Hazelnut Iced Coffee (Large)"]
    Coffee_Tea --> Hazelnut_Iced_Coffee_Large
    Hazelnut_Iced_Coffee_Medium["Hazelnut Iced Coffee (Medium)"]
    Coffee_Tea --> Hazelnut_Iced_Coffee_Medium
    Hazelnut_Iced_Coffee_Small["Hazelnut Iced Coffee (Small)"]
    Coffee_Tea --> Hazelnut_Iced_Coffee_Small
    Hazelnut_Latte_Large["Hazelnut Latte (Large)"]
    Coffee_Tea --> Hazelnut_Latte_Large
    Hazelnut_Latte_Medium["Hazelnut Latte (Medium)"]
    Coffee_Tea --> Hazelnut_Latte_Medium
    Hazelnut_Latte_Small["Hazelnut Latte (Small)"]
    Coffee_Tea --> Hazelnut_Latte_Small
    Hot_Chocolate_Large["Hot Chocolate (Large)"]
    Coffee_Tea --> Hot_Chocolate_Large
    Hot_Chocolate_Large_Nonfat_Milk["add Nonfat Milk"]
    Hot_Chocolate_Large --> Hot_Chocolate_Large_Nonfat_Milk
    Hot_Chocolate_Medium["Hot Chocolate (Medium)"]
    Coffee_Tea --> Hot_Chocolate_Medium
    Hot_Chocolate_Medium_Nonfat_Milk["add Nonfat Milk"]
    Hot_Chocolate_Medium --> Hot_Chocolate_Medium_Nonfat_Milk
    Hot_Chocolate_Small["Hot Chocolate (Small)"]
    Coffee_Tea --> Hot_Chocolate_Small
    Hot_Chocolate_Small_Nonfat_Milk["add Nonfat Milk"]
    Hot_Chocolate_Small --> Hot_Chocolate_Small_Nonfat_Milk
    Iced_Caramel_Mocha_Large["Iced Caramel Mocha (Large)"]
    Coffee_Tea --> Iced_Caramel_Mocha_Large
    Iced_Caramel_Mocha_Medium["Iced Caramel Mocha (Medium)"]
    Coffee_Tea --> Iced_Caramel_Mocha_Medium
    Iced_Caramel_Mocha_Small["Iced Caramel Mocha (Small)"]
    Coffee_Tea --> Iced_Caramel_Mocha_Small
    Iced_Coffee_Large["Iced Coffee (Large)"]
    Coffee_Tea --> Iced_Coffee_Large
    Iced_Coffee_Large_Sugar_Free_French_Vanilla_Syrup["add Sugar Free French Vanilla Syrup"]
    Iced_Coffee_Large --> Iced_Coffee_Large_Sugar_Free_French_Vanilla_Syrup
    Iced_Coffee_Medium["Iced Coffee (Medium)"]
    Coffee_Tea --> Iced_Coffee_Medium
    Iced_Coffee_Medium_Sugar_Free_French_Vanilla_Syrup["add Sugar Free French Vanilla Syrup"]
    Iced_Coffee_Medium --> Iced_Coffee_Medium_Sugar_Free_French_Vanilla_Syrup
    Iced_Coffee_Small["Iced Coffee (Small)"]
    Coffee_Tea --> Iced_Coffee_Small
    Iced_Coffee_Small_Sugar_Free_French_Vanilla_Syrup["add Sugar Free French Vanilla Syrup"]
    Iced_Coffee_Small --> Iced_Coffee_Small_Sugar_Free_French_Vanilla_Syrup
    Iced_Mocha_Large["Iced Mocha (Large)"]
    Coffee_Tea --> Iced_Mocha_Large
    Iced_Mocha_Large_Nonfat_Milk["add Nonfat Milk"]
    Iced_Mocha_Large --> Iced_Mocha_Large_Nonfat_Milk
    Iced_Mocha_Medium["Iced Mocha (Medium)"]
    Coffee_Tea --> Iced_Mocha_Medium
    Iced_Mocha_Medium_Nonfat_Milk["add Nonfat Milk"]
    Iced_Mocha_Medium --> Iced_Mocha_Medium_Nonfat_Milk
    Iced_Mocha_Small["Iced Mocha (Small)"]
    Coffee_Tea --> Iced_Mocha_Small
    Iced_Mocha_Small_Nonfat_Milk["add Nonfat Milk"]
    Iced_Mocha_Small --> Iced_Mocha_Small_Nonfat_Milk
    Iced_Nonfat_Caramel_Mocha_Large["Iced Nonfat Caramel Mocha (Large)"]
    Coffee_Tea --> Iced_Nonfat_Caramel_Mocha_Large
    Iced_Nonfat_Caramel_Mocha_Medium["Iced Nonfat Caramel Mocha (Medium)"]
    Coffee_Tea --> Iced_Nonfat_Caramel_Mocha_Medium
    Iced_Nonfat_Caramel_Mocha_Small["Iced Nonfat Caramel Mocha (Small)"]
    Coffee_Tea --> Iced_Nonfat_Caramel_Mocha_Small
    Iced_Tea_Child["Iced Tea (Child)"]
    Coffee_Tea --> Iced_Tea_Child
    Iced_Tea_Large["Iced Tea (Large)"]
    Coffee_Tea --> Iced_Tea_Large
    Iced_Tea_Medium["Iced Tea (Medium)"]
    Coffee_Tea --> Iced_Tea_Medium
    Iced_Tea_Small["Iced Tea (Small)"]
    Coffee_Tea --> Iced_Tea_Small
    Latte_Large["Latte (Large)"]
    Coffee_Tea --> Latte_Large
    Latte_Large_Sugar_Free_French_Vanilla_Syrup["add Sugar Free French Vanilla Syrup"]
    Latte_Large --> Latte_Large_Sugar_Free_French_Vanilla_Syrup
    Latte_Medium["Latte (Medium)"]
    Coffee_Tea --> Latte_Medium
    Latte_Medium_Sugar_Free_French_Vanilla_Syrup["add Sugar Free French Vanilla Syrup"]
    Latte_Medium --> Latte_Medium_Sugar_Free_French_Vanilla_Syrup
    Latte_Small["Latte (Small)"]
    Coffee_Tea --> Latte_Small
    Latte_Small_Sugar_Free_French_Vanilla_Syrup["add Sugar Free French Vanilla Syrup"]
    Latte_Small --> Latte_Small_Sugar_Free_French_Vanilla_Syrup
    Mocha_Large["Mocha (Large)"]
    Coffee_Tea --> Mocha_Large
    Mocha_Large_Nonfat_Milk["add Nonfat Milk"]
    Mocha_Large --> Mocha_Large_Nonfat_Milk
    Mocha_Medium["Mocha (Medium)"]
    Coffee_Tea --> Mocha_Medium
    Mocha_Medium_Nonfat_Milk["add Nonfat Milk"]
    Mocha_Medium --> Mocha_Medium_Nonfat_Milk
    Mocha_Small["Mocha (Small)"]
    Coffee_Tea --> Mocha_Small
    Mocha_Small_Nonfat_Milk["add Nonfat Milk"]
    Mocha_Small --> Mocha_Small_Nonfat_Milk
    Nonfat_Caramel_Latte_Large["Nonfat Caramel Latte (Large)"]
    Coffee_Tea --> Nonfat_Caramel_Latte_Large
    Nonfat_Caramel_Latte_Medium["Nonfat Caramel Latte (Medium)"]
    Coffee_Tea --> Nonfat_Caramel_Latte_Medium
    Nonfat_Caramel_Latte_Small["Nonfat Caramel Latte (Small)"]
    Coffee_Tea --> Nonfat_Caramel_Latte_Small
    Nonfat_Caramel_Mocha_Large["Nonfat Caramel Mocha (Large)"]
    Coffee_Tea --> Nonfat_Caramel_Mocha_Large
    Nonfat_Caramel_Mocha_Medium["Nonfat Caramel Mocha (Medium)"]
    Coffee_Tea --> Nonfat_Caramel_Mocha_Medium
    Nonfat_Caramel_Mocha_Small["Nonfat Caramel Mocha (Small)"]
    Coffee_Tea --> Nonfat_Caramel_Mocha_Small
    Nonfat_French_Vanilla_Latte_Large["Nonfat French Vanilla Latte (Large)"]
    Coffee_Tea --> Nonfat_French_Vanilla_Latte_Large
    Nonfat_French_Vanilla_Latte_Medium["Nonfat French Vanilla Latte (Medium)"]
    Coffee_Tea --> Nonfat_French_Vanilla_Latte_Medium
    Nonfat_French_Vanilla_Latte_Small["Nonfat French Vanilla Latte (Small)"]
    Coffee_Tea --> Nonfat_French_Vanilla_Latte_Small
    Nonfat_Hazelnut_Latte_Large["Nonfat Hazelnut Latte (Large)"]
    Coffee_Tea --> Nonfat_Hazelnut_Latte_Large
    Nonfat_Hazelnut_Latte_Medium["Nonfat Hazelnut Latte (Medium)"]
    Coffee_Tea --> Nonfat_Hazelnut_Latte_Medium
    Nonfat_Hazelnut_Latte_Small["Nonfat Hazelnut Latte (Small)"]
    Coffee_Tea --> Nonfat_Hazelnut_Latte_Small
    Nonfat_Latte_Large["Nonfat Latte (Large)"]
    Coffee_Tea --> Nonfat_Latte_Large
    Nonfat_Latte_Large_Sugar_Free_French_Vanilla_Syrup["add Sugar Free French Vanilla Syrup"]
    Nonfat_Latte_Large --> Nonfat_Latte_Large_Sugar_Free_French_Vanilla_Syrup
    Nonfat_Latte_Medium["Nonfat Latte (Medium)"]
    Coffee_Tea --> Nonfat_Latte_Medium
    Nonfat_Latte_Medium_Sugar_Free_French_Vanilla_Syrup["add Sugar Free French Vanilla Syrup"]
    Nonfat_Latte_Medium --> Nonfat_Latte_Medium_Sugar_Free_French_Vanilla_Syrup
    Nonfat_Latte_Small["Nonfat Latte (Small)"]
    Coffee_Tea --> Nonfat_Latte_Small
    Nonfat_Latte_Small_Sugar_Free_French_Vanilla_Syrup["add Sugar Free French Vanilla Syrup"]
    Nonfat_Latte_Small --> Nonfat_Latte_Small_Sugar_Free_French_Vanilla_Syrup
    Regular_Iced_Coffee_Large["Regular Iced Coffee (Large)"]
    Coffee_Tea --> Regular_Iced_Coffee_Large
    Regular_Iced_Coffee_Medium["Regular Iced Coffee (Medium)"]
    Coffee_Tea --> Regular_Iced_Coffee_Medium
    Regular_Iced_Coffee_Small["Regular Iced Coffee (Small)"]
    Coffee_Tea --> Regular_Iced_Coffee_Small
    Sweet_Tea_Child["Sweet Tea (Child)"]
    Coffee_Tea --> Sweet_Tea_Child
    Sweet_Tea_Large["Sweet Tea (Large)"]
    Coffee_Tea --> Sweet_Tea_Large
    Sweet_Tea_Medium["Sweet Tea (Medium)"]
    Coffee_Tea --> Sweet_Tea_Medium
    Sweet_Tea_Small["Sweet Tea (Small)"]
    Coffee_Tea --> Sweet_Tea_Small
```


### Smoothies & Shakes

```mermaid
graph TD
    Smoothies_Shakes["Smoothies & Shakes"]
    Blueberry_Pomegranate_Smoothie_Large["Blueberry Pomegranate Smoothie (Large)"]
    Smoothies_Shakes --> Blueberry_Pomegranate_Smoothie_Large
    Blueberry_Pomegranate_Smoothie_Medium["Blueberry Pomegranate Smoothie (Medium)"]
    Smoothies_Shakes --> Blueberry_Pomegranate_Smoothie_Medium
    Blueberry_Pomegranate_Smoothie_Small["Blueberry Pomegranate Smoothie (Small)"]
    Smoothies_Shakes --> Blueberry_Pomegranate_Smoothie_Small
    Chocolate_Shake_Large["Chocolate Shake (Large)"]
    Smoothies_Shakes --> Chocolate_Shake_Large
    Chocolate_Shake_Medium["Chocolate Shake (Medium)"]
    Smoothies_Shakes --> Chocolate_Shake_Medium
    Chocolate_Shake_Small["Chocolate Shake (Small)"]
    Smoothies_Shakes --> Chocolate_Shake_Small
    Mango_Pineapple_Smoothie_Large["Mango Pineapple Smoothie (Large)"]
    Smoothies_Shakes --> Mango_Pineapple_Smoothie_Large
    Mango_Pineapple_Smoothie_Medium["Mango Pineapple Smoothie (Medium)"]
    Smoothies_Shakes --> Mango_Pineapple_Smoothie_Medium
    Mango_Pineapple_Smoothie_Small["Mango Pineapple Smoothie (Small)"]
    Smoothies_Shakes --> Mango_Pineapple_Smoothie_Small
    McFlurry_Medium["McFlurry (Medium)"]
    Smoothies_Shakes --> McFlurry_Medium
    McFlurry_Medium_M_Ms_Candies["add M&Ms Candies"]
    McFlurry_Medium --> McFlurry_Medium_M_Ms_Candies
    McFlurry_Medium_Oreo_Cookies["add Oreo Cookies"]
    McFlurry_Medium --> McFlurry_Medium_Oreo_Cookies
    McFlurry_Medium_Reeses_Peanut_Butter_Cups["add Reeses Peanut Butter Cups"]
    McFlurry_Medium --> McFlurry_Medium_Reeses_Peanut_Butter_Cups
    McFlurry_Small["McFlurry (Small)"]
    Smoothies_Shakes --> McFlurry_Small
    McFlurry_Small_M_Ms_Candies["add M&Ms Candies"]
    McFlurry_Small --> McFlurry_Small_M_Ms_Candies
    McFlurry_Small_Oreo_Cookies["add Oreo Cookies"]
    McFlurry_Small --> McFlurry_Small_Oreo_Cookies
    McFlurry_Snack["McFlurry (Snack)"]
    Smoothies_Shakes --> McFlurry_Snack
    McFlurry_Snack_M_Ms_Candies["add M&Ms Candies"]
    McFlurry_Snack --> McFlurry_Snack_M_Ms_Candies
    McFlurry_Snack_Oreo_Cookies["add Oreo Cookies"]
    McFlurry_Snack --> McFlurry_Snack_Oreo_Cookies
    McFlurry_Snack_Reeses_Peanut_Butter_Cups["add Reeses Peanut Butter Cups"]
    McFlurry_Snack --> McFlurry_Snack_Reeses_Peanut_Butter_Cups
    Shamrock_Shake_Large["Shamrock Shake (Large)"]
    Smoothies_Shakes --> Shamrock_Shake_Large
    Shamrock_Shake_Medium["Shamrock Shake (Medium)"]
    Smoothies_Shakes --> Shamrock_Shake_Medium
    Strawberry_Banana_Smoothie_Large["Strawberry Banana Smoothie (Large)"]
    Smoothies_Shakes --> Strawberry_Banana_Smoothie_Large
    Strawberry_Banana_Smoothie_Medium["Strawberry Banana Smoothie (Medium)"]
    Smoothies_Shakes --> Strawberry_Banana_Smoothie_Medium
    Strawberry_Banana_Smoothie_Small["Strawberry Banana Smoothie (Small)"]
    Smoothies_Shakes --> Strawberry_Banana_Smoothie_Small
    Strawberry_Shake_Large["Strawberry Shake (Large)"]
    Smoothies_Shakes --> Strawberry_Shake_Large
    Strawberry_Shake_Medium["Strawberry Shake (Medium)"]
    Smoothies_Shakes --> Strawberry_Shake_Medium
    Strawberry_Shake_Small["Strawberry Shake (Small)"]
    Smoothies_Shakes --> Strawberry_Shake_Small
    Vanilla_Shake_Large["Vanilla Shake (Large)"]
    Smoothies_Shakes --> Vanilla_Shake_Large
    Vanilla_Shake_Medium["Vanilla Shake (Medium)"]
    Smoothies_Shakes --> Vanilla_Shake_Medium
    Vanilla_Shake_Small["Vanilla Shake (Small)"]
    Smoothies_Shakes --> Vanilla_Shake_Small
```


## Structure Details

### Breakfast

- **Bacon**
  - (no variations)
- **Big Breakfast (Large Biscuit)**
  - add Egg Whites
  - add Hotcakes
  - add Hotcakes and Egg Whites
- **Big Breakfast (Regular Biscuit)**
  - add Egg Whites
  - add Hotcakes
  - add Hotcakes and Egg Whites
- **Cinnamon Melts**
  - (no variations)
- **Egg McMuffin**
  - (no variations)
- **Egg White Delight**
  - (no variations)
- **Fruit & Maple Oatmeal**
  - without Brown Sugar
- **Fruit & Maple Oatmeal without Brown Sugar**
  - (no variations)
- **Hash Brown**
  - (no variations)
- **Hotcakes**
  - (no variations)
- **Hotcakes and Sausage**
  - (no variations)
- **Sausage**
  - (no variations)
- **Sausage Biscuit (Large Biscuit)**
  - add Egg
  - add Egg Whites
- **Sausage Biscuit (Regular Biscuit)**
  - add Egg
  - add Egg Whites
- **Sausage Burrito**
  - (no variations)
- **Sausage McGriddles**
  - (no variations)
- **Sausage McMuffin**
  - add Egg
  - add Egg Whites
- **Southern Style Chicken Biscuit (Large Biscuit)**
  - (no variations)
- **Southern Style Chicken Biscuit (Regular Biscuit)**
  - (no variations)
- **Steak**
  - (no variations)
- **Steak & Egg Biscuit (Regular Biscuit)**
  - (no variations)
- **Steak & Egg McMuffin**
  - (no variations)

### Beef & Pork

- **Bacon Clubhouse Burger**
  - (no variations)
- **Bacon McDouble**
  - (no variations)
- **Big Mac**
  - (no variations)
- **Cheeseburger**
  - (no variations)
- **Daily Double**
  - (no variations)
- **Double Cheeseburger**
  - (no variations)
- **Double Quarter Pounder**
  - add Cheese
- **Hamburger**
  - (no variations)
- **Jalapeño Double**
  - (no variations)
- **McDouble**
  - (no variations)
- **McRib**
  - (no variations)
- **Quarter Pounder**
  - add Bacon & Cheese
  - add Bacon Habanero Ranch
  - add Cheese
- **Quarter Pounder Deluxe**
  - (no variations)

### Chicken & Fish

- **Bacon Buffalo Ranch McChicken**
  - (no variations)
- **Bacon Cheddar McChicken**
  - (no variations)
- **Bacon Clubhouse Crispy Chicken Sandwich**
  - (no variations)
- **Bacon Clubhouse Grilled Chicken Sandwich**
  - (no variations)
- **Buffalo Ranch McChicken**
  - (no variations)
- **Chicken McNuggets (10 piece)**
  - (no variations)
- **Chicken McNuggets (20 piece)**
  - (no variations)
- **Chicken McNuggets (4 piece)**
  - (no variations)
- **Chicken McNuggets (40 piece)**
  - (no variations)
- **Chicken McNuggets (6 piece)**
  - (no variations)
- **Filet-O-Fish**
  - (no variations)
- **McChicken**
  - (no variations)
- **Premium Crispy Chicken Classic Sandwich**
  - (no variations)
- **Premium Crispy Chicken Club Sandwich**
  - (no variations)
- **Premium Crispy Chicken Ranch BLT Sandwich**
  - (no variations)
- **Premium Grilled Chicken Classic Sandwich**
  - (no variations)
- **Premium Grilled Chicken Club Sandwich**
  - (no variations)
- **Premium Grilled Chicken Ranch BLT Sandwich**
  - (no variations)
- **Premium McWrap Chicken & Bacon (Crispy Chicken)**
  - (no variations)
- **Premium McWrap Chicken & Bacon (Grilled Chicken)**
  - (no variations)
- **Premium McWrap Chicken & Ranch (Crispy Chicken)**
  - (no variations)
- **Premium McWrap Chicken & Ranch (Grilled Chicken)**
  - (no variations)
- **Premium McWrap Chicken Sweet Chili (Crispy Chicken)**
  - (no variations)
- **Premium McWrap Chicken Sweet Chili (Grilled Chicken)**
  - (no variations)
- **Premium McWrap Southwest Chicken (Crispy Chicken)**
  - (no variations)
- **Premium McWrap Southwest Chicken (Grilled Chicken)**
  - (no variations)
- **Southern Style Crispy Chicken Sandwich**
  - (no variations)

### Salads

- **Premium Bacon Ranch Salad (without Chicken)**
  - add Crispy Chicken
  - add Grilled Chicken
- **Premium Southwest Salad (without Chicken)**
  - add Crispy Chicken
  - add Grilled Chicken

### Snacks & Sides

- **Apple Slices**
  - (no variations)
- **Chipotle BBQ Snack Wrap (Crispy Chicken)**
  - (no variations)
- **Chipotle BBQ Snack Wrap (Grilled Chicken)**
  - (no variations)
- **Fruit n Yogurt Parfait**
  - (no variations)
- **Honey Mustard Snack Wrap (Crispy Chicken)**
  - (no variations)
- **Honey Mustard Snack Wrap (Grilled Chicken)**
  - (no variations)
- **Kids French Fries**
  - (no variations)
- **Large French Fries**
  - (no variations)
- **Medium French Fries**
  - (no variations)
- **Ranch Snack Wrap (Crispy Chicken)**
  - (no variations)
- **Ranch Snack Wrap (Grilled Chicken)**
  - (no variations)
- **Side Salad**
  - (no variations)
- **Small French Fries**
  - (no variations)

### Desserts

- **Baked Apple Pie**
  - (no variations)
- **Chocolate Chip Cookie**
  - (no variations)
- **Hot Caramel Sundae**
  - (no variations)
- **Hot Fudge Sundae**
  - (no variations)
- **Kids Ice Cream Cone**
  - (no variations)
- **Oatmeal Raisin Cookie**
  - (no variations)
- **Strawberry Sundae**
  - (no variations)

### Beverages

- **1% Low Fat Milk Jug**
  - (no variations)
- **Coca-Cola Classic (Child)**
  - (no variations)
- **Coca-Cola Classic (Large)**
  - (no variations)
- **Coca-Cola Classic (Medium)**
  - (no variations)
- **Coca-Cola Classic (Small)**
  - (no variations)
- **Dasani Water Bottle**
  - (no variations)
- **Diet Coke (Child)**
  - (no variations)
- **Diet Coke (Large)**
  - (no variations)
- **Diet Coke (Medium)**
  - (no variations)
- **Diet Coke (Small)**
  - (no variations)
- **Diet Dr Pepper (Child)**
  - (no variations)
- **Diet Dr Pepper (Large)**
  - (no variations)
- **Diet Dr Pepper (Medium)**
  - (no variations)
- **Diet Dr Pepper (Small)**
  - (no variations)
- **Dr Pepper (Child)**
  - (no variations)
- **Dr Pepper (Large)**
  - (no variations)
- **Dr Pepper (Medium)**
  - (no variations)
- **Dr Pepper (Small)**
  - (no variations)
- **Fat Free Chocolate Milk Jug**
  - (no variations)
- **Minute Maid 100% Apple Juice Box**
  - (no variations)
- **Minute Maid Orange Juice (Large)**
  - (no variations)
- **Minute Maid Orange Juice (Medium)**
  - (no variations)
- **Minute Maid Orange Juice (Small)**
  - (no variations)
- **Sprite (Child)**
  - (no variations)
- **Sprite (Large)**
  - (no variations)
- **Sprite (Medium)**
  - (no variations)
- **Sprite (Small)**
  - (no variations)

### Coffee & Tea

- **Caramel Iced Coffee (Large)**
  - (no variations)
- **Caramel Iced Coffee (Medium)**
  - (no variations)
- **Caramel Iced Coffee (Small)**
  - (no variations)
- **Caramel Latte (Large)**
  - (no variations)
- **Caramel Latte (Medium)**
  - (no variations)
- **Caramel Latte (Small)**
  - (no variations)
- **Caramel Mocha (Large)**
  - (no variations)
- **Caramel Mocha (Medium)**
  - (no variations)
- **Caramel Mocha (Small)**
  - (no variations)
- **Coffee (Large)**
  - (no variations)
- **Coffee (Medium)**
  - (no variations)
- **Coffee (Small)**
  - (no variations)
- **Frappé Caramel (Large)**
  - (no variations)
- **Frappé Caramel (Medium)**
  - (no variations)
- **Frappé Caramel (Small)**
  - (no variations)
- **Frappé Chocolate Chip (Large)**
  - (no variations)
- **Frappé Chocolate Chip (Medium)**
  - (no variations)
- **Frappé Chocolate Chip (Small)**
  - (no variations)
- **Frappé Mocha (Large)**
  - (no variations)
- **Frappé Mocha (Medium)**
  - (no variations)
- **Frappé Mocha (Small)**
  - (no variations)
- **French Vanilla Iced Coffee (Large)**
  - (no variations)
- **French Vanilla Iced Coffee (Medium)**
  - (no variations)
- **French Vanilla Iced Coffee (Small)**
  - (no variations)
- **French Vanilla Latte (Large)**
  - (no variations)
- **French Vanilla Latte (Medium)**
  - (no variations)
- **French Vanilla Latte (Small)**
  - (no variations)
- **Hazelnut Iced Coffee (Large)**
  - (no variations)
- **Hazelnut Iced Coffee (Medium)**
  - (no variations)
- **Hazelnut Iced Coffee (Small)**
  - (no variations)
- **Hazelnut Latte (Large)**
  - (no variations)
- **Hazelnut Latte (Medium)**
  - (no variations)
- **Hazelnut Latte (Small)**
  - (no variations)
- **Hot Chocolate (Large)**
  - add Nonfat Milk
- **Hot Chocolate (Medium)**
  - add Nonfat Milk
- **Hot Chocolate (Small)**
  - add Nonfat Milk
- **Iced Caramel Mocha (Large)**
  - (no variations)
- **Iced Caramel Mocha (Medium)**
  - (no variations)
- **Iced Caramel Mocha (Small)**
  - (no variations)
- **Iced Coffee (Large)**
  - add Sugar Free French Vanilla Syrup
- **Iced Coffee (Medium)**
  - add Sugar Free French Vanilla Syrup
- **Iced Coffee (Small)**
  - add Sugar Free French Vanilla Syrup
- **Iced Mocha (Large)**
  - add Nonfat Milk
- **Iced Mocha (Medium)**
  - add Nonfat Milk
- **Iced Mocha (Small)**
  - add Nonfat Milk
- **Iced Nonfat Caramel Mocha (Large)**
  - (no variations)
- **Iced Nonfat Caramel Mocha (Medium)**
  - (no variations)
- **Iced Nonfat Caramel Mocha (Small)**
  - (no variations)
- **Iced Tea (Child)**
  - (no variations)
- **Iced Tea (Large)**
  - (no variations)
- **Iced Tea (Medium)**
  - (no variations)
- **Iced Tea (Small)**
  - (no variations)
- **Latte (Large)**
  - add Sugar Free French Vanilla Syrup
- **Latte (Medium)**
  - add Sugar Free French Vanilla Syrup
- **Latte (Small)**
  - add Sugar Free French Vanilla Syrup
- **Mocha (Large)**
  - add Nonfat Milk
- **Mocha (Medium)**
  - add Nonfat Milk
- **Mocha (Small)**
  - add Nonfat Milk
- **Nonfat Caramel Latte (Large)**
  - (no variations)
- **Nonfat Caramel Latte (Medium)**
  - (no variations)
- **Nonfat Caramel Latte (Small)**
  - (no variations)
- **Nonfat Caramel Mocha (Large)**
  - (no variations)
- **Nonfat Caramel Mocha (Medium)**
  - (no variations)
- **Nonfat Caramel Mocha (Small)**
  - (no variations)
- **Nonfat French Vanilla Latte (Large)**
  - (no variations)
- **Nonfat French Vanilla Latte (Medium)**
  - (no variations)
- **Nonfat French Vanilla Latte (Small)**
  - (no variations)
- **Nonfat Hazelnut Latte (Large)**
  - (no variations)
- **Nonfat Hazelnut Latte (Medium)**
  - (no variations)
- **Nonfat Hazelnut Latte (Small)**
  - (no variations)
- **Nonfat Latte (Large)**
  - add Sugar Free French Vanilla Syrup
- **Nonfat Latte (Medium)**
  - add Sugar Free French Vanilla Syrup
- **Nonfat Latte (Small)**
  - add Sugar Free French Vanilla Syrup
- **Regular Iced Coffee (Large)**
  - (no variations)
- **Regular Iced Coffee (Medium)**
  - (no variations)
- **Regular Iced Coffee (Small)**
  - (no variations)
- **Sweet Tea (Child)**
  - (no variations)
- **Sweet Tea (Large)**
  - (no variations)
- **Sweet Tea (Medium)**
  - (no variations)
- **Sweet Tea (Small)**
  - (no variations)

### Smoothies & Shakes

- **Blueberry Pomegranate Smoothie (Large)**
  - (no variations)
- **Blueberry Pomegranate Smoothie (Medium)**
  - (no variations)
- **Blueberry Pomegranate Smoothie (Small)**
  - (no variations)
- **Chocolate Shake (Large)**
  - (no variations)
- **Chocolate Shake (Medium)**
  - (no variations)
- **Chocolate Shake (Small)**
  - (no variations)
- **Mango Pineapple Smoothie (Large)**
  - (no variations)
- **Mango Pineapple Smoothie (Medium)**
  - (no variations)
- **Mango Pineapple Smoothie (Small)**
  - (no variations)
- **McFlurry (Medium)**
  - add M&Ms Candies
  - add Oreo Cookies
  - add Reeses Peanut Butter Cups
- **McFlurry (Small)**
  - add M&Ms Candies
  - add Oreo Cookies
- **McFlurry (Snack)**
  - add M&Ms Candies
  - add Oreo Cookies
  - add Reeses Peanut Butter Cups
- **Shamrock Shake (Large)**
  - (no variations)
- **Shamrock Shake (Medium)**
  - (no variations)
- **Strawberry Banana Smoothie (Large)**
  - (no variations)
- **Strawberry Banana Smoothie (Medium)**
  - (no variations)
- **Strawberry Banana Smoothie (Small)**
  - (no variations)
- **Strawberry Shake (Large)**
  - (no variations)
- **Strawberry Shake (Medium)**
  - (no variations)
- **Strawberry Shake (Small)**
  - (no variations)
- **Vanilla Shake (Large)**
  - (no variations)
- **Vanilla Shake (Medium)**
  - (no variations)
- **Vanilla Shake (Small)**
  - (no variations)

