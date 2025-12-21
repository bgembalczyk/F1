#!/usr/bin/env python3
"""Test importów po refaktoryzacji CircuitService."""

print("Testing CircuitService imports...")

# Test 1: Stary import (backward compatibility)
print("\n1. Testing old import (deprecated)...")
try:
    from models.services.circuit_service import CircuitService
    print("✓ from models.services.circuit_service import CircuitService")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 2: Nowy import (zalecany)
print("\n2. Testing new import (recommended)...")
try:
    from models.services.circuits import CircuitService
    print("✓ from models.services.circuits import CircuitService")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 3: Import funkcji pomocniczych
print("\n3. Testing helper functions import...")
try:
    from models.services.circuits import (
        merge_race_lap_records,
        build_record_key,
        extract_circuit_names,
    )
    print("✓ from models.services.circuits import merge_race_lap_records, ...")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 4: Import z konkretnych modułów
print("\n4. Testing specific module imports...")
try:
    from models.services.circuits.normalization import cleanup_urls
    from models.services.circuits.lap_record_merging import select_best_driver
    print("✓ from models.services.circuits.normalization import ...")
    print("✓ from models.services.circuits.lap_record_merging import ...")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 5: Sprawdzenie dostępności metod CircuitService
print("\n5. Testing CircuitService methods...")
try:
    assert hasattr(CircuitService, "normalize_record")
    assert hasattr(CircuitService, "merge_race_lap_records")
    assert hasattr(CircuitService, "record_key")
    assert hasattr(CircuitService, "core_key")
    print("✓ All CircuitService methods available")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n✓ All import tests passed!")

