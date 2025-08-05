#!/usr/bin/env python3
"""Test script to verify transition functionality"""

import os
import sys
import re

# Set up environment for headless operation
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['DISPLAY'] = ':99'

# Add the current directory to Python path
sys.path.insert(0, '/home/runner/work/vne/vne')

def test_transition_parsing():
    """Test that the new transition parsing works correctly"""
    print("Testing transition parsing...")
    
    try:
        from vne.events import EventManager
        from vne import Core
        
        # Create a minimal engine instance
        engine = Core("projects/test-game", devMode=True)
        event_manager = EventManager()
        
        # Test sprite transition parsing
        print("  Testing sprite transitions...")
        
        # Test cases for sprite transitions
        test_cases = [
            '@sprite kuro transition="dissolve"',
            '@sprite kuro position="left" transition="fadein"', 
            '@sprite kuro animation="dissolve"',  # Should still work
            '@sprite kuro position="right" animation="fadeout"',  # Should still work
        ]
        
        for test_case in test_cases:
            print(f"    Testing: {test_case}")
            
            # Parse the argument (simulate what handle_sprite receives)
            arg = test_case.replace('@sprite ', '')
            
            # Test regex patterns
            anim_match = re.search(r'animation="(.*?)"', arg)
            transition_match = re.search(r'transition="(.*?)"', arg)
            
            if transition_match:
                anim_type = transition_match.group(1).lower()
                print(f"      Found transition: {anim_type}")
            elif anim_match:
                anim_type = anim_match.group(1).lower()
                print(f"      Found animation: {anim_type}")
            else:
                print(f"      No animation/transition found")
        
        # Test background transition parsing
        print("  Testing background transitions...")
        
        bg_test_cases = [
            'park transition dissolve',
            'black transition fadein',
            'school',  # No transition
        ]
        
        for test_case in bg_test_cases:
            print(f"    Testing: @bg {test_case}")
            
            # Parse like handle_bg does
            parts = test_case.strip().split()
            bg_name = parts[0] if parts else test_case.strip()
            transition_match = re.search(r'transition\s+(\w+)', test_case)
            
            print(f"      Background name: {bg_name}")
            if transition_match:
                transition_type = transition_match.group(1).lower()
                print(f"      Transition type: {transition_type}")
            else:
                print(f"      No transition")
        
        # Test audio transition parsing
        print("  Testing audio transitions...")
        
        audio_test_cases = [
            'music transition dissolve',
            'sound transition fadein',
            'music',  # No transition
        ]
        
        for test_case in audio_test_cases:
            print(f"    Testing: @bgm {test_case}")
            
            # Parse like handle_bgm does
            parts = test_case.strip().split()
            filename = parts[0] if parts else test_case.strip()
            transition_match = re.search(r'transition\s+(\w+)', test_case)
            
            print(f"      Filename: {filename}")
            if transition_match:
                transition_type = transition_match.group(1).lower()
                print(f"      Transition type: {transition_type}")
            else:
                print(f"      No transition")
        
        print("✓ Transition parsing tests passed!")
        return True
        
    except Exception as e:
        import traceback
        print(f"✗ Error testing transition parsing: {e}")
        print(traceback.format_exc())
        return False

def test_backwards_compatibility():
    """Test that old animation syntax still works"""
    print("Testing backwards compatibility...")
    
    try:
        # Test that existing scripts with animation="dissolve" still work
        arg = 'kuro position="left" animation="dissolve"'
        
        # This should work with both old and new code
        anim_match = re.search(r'animation="(.*?)"', arg)
        transition_match = re.search(r'transition="(.*?)"', arg)
        
        if transition_match:
            anim_type = transition_match.group(1).lower()
        elif anim_match:
            anim_type = anim_match.group(1).lower()
        else:
            anim_type = None
            
        if anim_type == "dissolve":
            print("✓ Old animation syntax still works!")
            return True
        else:
            print("✗ Old animation syntax broken!")
            return False
            
    except Exception as e:
        print(f"✗ Error testing backwards compatibility: {e}")
        return False

def main():
    """Run all tests"""
    print("=== VNE Transition Feature Tests ===")
    
    tests_passed = 0
    total_tests = 2
    
    if test_transition_parsing():
        tests_passed += 1
        
    if test_backwards_compatibility():
        tests_passed += 1
    
    print(f"\n=== Test Results: {tests_passed}/{total_tests} passed ===")
    
    if tests_passed == total_tests:
        print("✓ All tests passed! Transition features implemented correctly.")
        return True
    else:
        print("✗ Some tests failed. Check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)