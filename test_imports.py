#!/usr/bin/env python
"""Test script to verify all critical modules import correctly."""

import sys
import traceback

tests_passed = 0
tests_failed = 0

def test_import(module_name: str):
    """Test importing a module."""
    global tests_passed, tests_failed
    try:
        __import__(module_name)
        print(f"✅ {module_name}")
        tests_passed += 1
        return True
    except Exception as e:
        print(f"❌ {module_name}")
        print(f"   Error: {e}")
        traceback.print_exc()
        tests_failed += 1
        return False

# Test critical imports
print("=" * 60)
print("MOT-X OS - Import Test Suite")
print("=" * 60 + "\n")

print("Testing core modules...")
test_import("src.motx_os_bridge.plugins.black_hole_folder")
test_import("src.motx_os_bridge.plugins.eye_tracking_integrated")
test_import("src.motx_os_bridge.utils.llm_client")
test_import("src.motx_os_bridge.utils.ollama_client")

print("\n" + "=" * 60)
print(f"Results: {tests_passed} passed, {tests_failed} failed")
print("=" * 60)

sys.exit(0 if tests_failed == 0 else 1)
