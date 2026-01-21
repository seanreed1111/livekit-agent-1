# Menu Structure JSON Format Alternatives

This document compares five different approaches to representing McDonald's menu items and their variations, replacing the use of `null` to indicate "standard/as-is" items.

## Problem with Current Format

The current `menu-structure.json` uses `null` to represent that an item can be ordered as-is without modifications:

```json
{
  "Fruit & Maple Oatmeal": [
    "without Brown Sugar",
    null
  ],
  "Hotcakes": [
    "Sausage",
    null
  ]
}
```

This approach is unclear and makes `null` serve as a semantic value rather than the absence of value.

---

## Alternative 1: Explicit "Standard" Keyword

**File:** `menu-structure-v2-explicit-standard.json`

Replace `null` with a descriptive string constant like "Standard".

### Example
```json
{
  "Fruit & Maple Oatmeal": [
    "Standard",
    "without Brown Sugar"
  ],
  "Hotcakes": [
    "Standard",
    "with Sausage"
  ]
}
```

### Pros
- Clear and readable
- Easy to understand for humans
- Minimal changes to existing structure
- Simple to parse

### Cons
- Introduces a "magic string" that requires special handling
- Need to document that "Standard" is reserved
- Could conflict if an actual menu item has "Standard" in the name
- Still doesn't clearly distinguish between optional and required modifications

---

## Alternative 2: Separated Structure (RECOMMENDED)

**File:** `menu-structure-v2-separated.json`

Split into two properties: whether the base item is orderable, and what variations exist.

### Example
```json
{
  "Fruit & Maple Oatmeal": {
    "available_as_base": true,
    "variations": ["without Brown Sugar"]
  },
  "McFlurry (Medium)": {
    "available_as_base": false,
    "variations": ["M&Ms Candies", "Oreo Cookies", "Reeses Peanut Butter Cups"]
  }
}
```

### Pros
- Semantically clear distinction between base item availability and variations
- Explicitly shows when a choice is required (`available_as_base: false`)
- Self-documenting structure
- Easy to query programmatically
- No magic values or special constants
- Handles all cases elegantly (no variations, optional variations, required variations)

### Cons
- More verbose than simple array
- Requires object structure instead of simple array
- Slightly more complex to parse

### Why This Is Recommended
This approach provides the clearest semantics for voice ordering systems where you need to know:
1. Can I order this item without modifications?
2. What modifications are available?
3. Do I need to ask the customer to make a choice?

---

## Alternative 3: Flattened Structure

**File:** `menu-structure-v2-flattened.json`

List every orderable combination as its own menu item.

### Example
```json
{
  "Breakfast": [
    "Fruit & Maple Oatmeal",
    "Fruit & Maple Oatmeal without Brown Sugar",
    "Hotcakes",
    "Hotcakes and Sausage"
  ]
}
```

### Pros
- Simplest structure possible
- Every orderable item is explicit
- No need to combine strings programmatically
- Easy to search and match customer speech

### Cons
- Loses the relationship between base items and variations
- Harder to maintain (changes require updating multiple entries)
- More difficult to programmatically generate variation prompts
- Doesn't scale well with many variations
- Can't distinguish between "Hotcakes and Sausage" vs "Hotcakes with Sausage"

---

## Alternative 4: Base-First Structure

**File:** `menu-structure-v2-base-first.json`

Use explicit `base` and `options` properties.

### Example
```json
{
  "Fruit & Maple Oatmeal": {
    "base": "Fruit & Maple Oatmeal",
    "options": ["without Brown Sugar"]
  }
}
```

### Pros
- Explicit about what the base item is
- Clear structure
- Easy to understand

### Cons
- Redundant (base name repeats the key)
- Doesn't indicate whether base is orderable alone
- Still doesn't distinguish optional vs required modifications

---

## Alternative 5: Modifier-Centric Structure

**File:** `menu-structure-v2-modifiers.json`

Focus on modifications with flags indicating whether they're required.

### Example
```json
{
  "Fruit & Maple Oatmeal": {
    "modifications": [
      {"name": "without Brown Sugar", "required": false}
    ]
  },
  "McFlurry (Medium)": {
    "modifications": [
      {"name": "M&Ms Candies", "required": true},
      {"name": "Oreo Cookies", "required": true},
      {"name": "Reeses Peanut Butter Cups", "required": true}
    ]
  }
}
```

### Pros
- Explicitly shows when a choice is required
- Most flexible for future extensions (could add price, nutrition, etc.)
- Clear about modification semantics

### Cons
- Most verbose structure
- `required: true` on all items in a list is redundant (just means "pick one")
- Empty modifications array for items with no variations
- Overkill for simple use case

---

## Comparison Summary

| Format | Clarity | Simplicity | Flexibility | Recommended Use Case |
|--------|---------|------------|-------------|---------------------|
| Explicit Standard | Medium | High | Low | Simple systems where distinction between optional/required doesn't matter |
| Separated | High | Medium | High | **Voice ordering, complex menu systems** |
| Flattened | High | Very High | Very Low | Static menus, simple search/match systems |
| Base-First | Medium | Medium | Medium | Systems that need explicit base names |
| Modifier-Centric | Very High | Low | Very High | Complex systems with many metadata requirements |

---

## Recommendation

**Use Alternative 2 (Separated Structure)** for a voice ordering system because:

1. It clearly indicates whether an item can be ordered as-is
2. It distinguishes between optional modifications (Big Mac with or without pickles) and required choices (McFlurry flavor selection)
3. It's programmatically straightforward to generate appropriate prompts:
   - If `available_as_base` is true and variations exist: "Would you like that standard or with modifications?"
   - If `available_as_base` is false: "Which flavor would you like?"
4. It scales well as the menu evolves
5. It provides clear semantics without magic values

## Implementation Notes

For voice ordering implementation:

```python
# Example pseudocode
if item["available_as_base"] and len(item["variations"]) == 0:
    # Simple item, just add to order
    add_to_order(item_name)
elif item["available_as_base"] and len(item["variations"]) > 0:
    # Ask if they want modifications
    ask("Would you like that standard or with [list variations]?")
else:
    # Must choose from variations
    ask("Which would you like: [list variations]?")
```
