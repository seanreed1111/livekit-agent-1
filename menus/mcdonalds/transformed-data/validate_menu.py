#!/usr/bin/env python3
"""Validate menu JSON against its schema using jsonschema library."""

import json
from pathlib import Path

from jsonschema import validate, ValidationError


def validate_menu():
    """Validate the McDonald's menu JSON against its schema."""
    base_dir = Path(__file__).parent / "transformed-data"

    # Load the schema
    schema_path = base_dir / "menu-structure-schema.json"
    with open(schema_path, "r") as f:
        schema = json.load(f)

    # Load the data
    data_path = base_dir / "menu-structure-2026-01-21.json"
    with open(data_path, "r") as f:
        data = json.load(f)

    # Validate using jsonschema
    try:
        validate(instance=data, schema=schema)
        print("✓ Validation successful! The JSON file conforms to the schema.")
        print(f"\n  Statistics:")
        print(f"  - Categories: {len(data)}")

        total_items = 0
        items_with_variations = 0
        total_variations = 0
        items_not_available_as_base = 0

        for category_items in data.values():
            total_items += len(category_items)

            for item_data in category_items.values():
                if item_data["variations"]:
                    items_with_variations += 1
                    total_variations += len(item_data["variations"])
                if not item_data["available_as_base"]:
                    items_not_available_as_base += 1

        print(f"  - Total items: {total_items}")
        print(f"  - Items with variations: {items_with_variations}")
        print(f"  - Total variations: {total_variations}")
        print(f"  - Items requiring variation selection: {items_not_available_as_base}")

        return True

    except ValidationError as e:
        print("✗ Validation failed:")
        print(f"  Path: {' > '.join(str(p) for p in e.path)}")
        print(f"  Error: {e.message}")
        if e.context:
            print(f"\n  Additional errors:")
            for error in e.context:
                print(f"    - {error.message}")
        return False

    except Exception as e:
        print(f"✗ Error during validation: {e}")
        return False


if __name__ == "__main__":
    import sys

    success = validate_menu()
    sys.exit(0 if success else 1)
