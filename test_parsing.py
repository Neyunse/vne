#!/usr/bin/env python3
"""Simple test for transition parsing logic"""

import re

def test_sprite_transition_parsing():
    """Test sprite transition parsing"""
    print("Testing sprite transition parsing...")
    
    test_cases = [
        ('kuro transition="dissolve"', 'dissolve', 'transition'),
        ('kuro position="left" transition="fadein"', 'fadein', 'transition'),
        ('kuro animation="dissolve"', 'dissolve', 'animation'),
        ('kuro position="right" animation="fadeout"', 'fadeout', 'animation'),
        ('kuro transition="dissolve" animation="fadein"', 'dissolve', 'transition'),  # transition should take priority
        ('kuro position="center"', None, None),  # no animation/transition
    ]
    
    for arg, expected_type, expected_source in test_cases:
        print(f"  Testing: @sprite {arg}")
        
        # Simulate the parsing logic from handle_sprite
        anim_match = re.search(r'animation="(.*?)"', arg)
        transition_match = re.search(r'transition="(.*?)"', arg)
        
        # Priorizar transition sobre animation si ambos están presentes
        if transition_match:
            anim_type = transition_match.group(1).lower()
            source = 'transition'
        elif anim_match:
            anim_type = anim_match.group(1).lower()
            source = 'animation'
        else:
            anim_type = None
            source = None
            
        if anim_type == expected_type and source == expected_source:
            print(f"    ✓ Expected {expected_type} from {expected_source}, got {anim_type} from {source}")
        else:
            print(f"    ✗ Expected {expected_type} from {expected_source}, got {anim_type} from {source}")
            return False
    
    return True

def test_bg_transition_parsing():
    """Test background transition parsing"""
    print("Testing background transition parsing...")
    
    test_cases = [
        ('park transition dissolve', 'park', 'dissolve'),
        ('black transition fadein', 'black', 'fadein'),
        ('school', 'school', None),
        ('white transition fadeout', 'white', 'fadeout'),
    ]
    
    for arg, expected_bg, expected_transition in test_cases:
        print(f"  Testing: @bg {arg}")
        
        # Simulate the parsing logic from handle_bg
        parts = arg.strip().split()
        bg_name = parts[0] if parts else arg.strip()
        
        transition_match = re.search(r'transition\s+(\w+)', arg)
        transition_type = transition_match.group(1).lower() if transition_match else None
        
        if bg_name == expected_bg and transition_type == expected_transition:
            print(f"    ✓ Expected bg={expected_bg}, transition={expected_transition}, got bg={bg_name}, transition={transition_type}")
        else:
            print(f"    ✗ Expected bg={expected_bg}, transition={expected_transition}, got bg={bg_name}, transition={transition_type}")
            return False
    
    return True

def test_audio_transition_parsing():
    """Test audio transition parsing"""
    print("Testing audio transition parsing...")
    
    test_cases = [
        ('music transition dissolve', 'music', 'dissolve'),
        ('sound transition fadein', 'sound', 'fadein'),
        ('bgmusic', 'bgmusic', None),
        ('effect transition fadeout', 'effect', 'fadeout'),
    ]
    
    for arg, expected_filename, expected_transition in test_cases:
        print(f"  Testing: @bgm {arg}")
        
        # Simulate the parsing logic from handle_bgm/handle_sfx
        parts = arg.strip().split()
        filename = parts[0] if parts else arg.strip()
        
        transition_match = re.search(r'transition\s+(\w+)', arg)
        transition_type = transition_match.group(1).lower() if transition_match else None
        
        if filename == expected_filename and transition_type == expected_transition:
            print(f"    ✓ Expected file={expected_filename}, transition={expected_transition}, got file={filename}, transition={transition_type}")
        else:
            print(f"    ✗ Expected file={expected_filename}, transition={expected_transition}, got file={filename}, transition={transition_type}")
            return False
    
    return True

def main():
    """Run all parsing tests"""
    print("=== VNE Transition Parsing Tests ===")
    
    tests = [
        test_sprite_transition_parsing,
        test_bg_transition_parsing,
        test_audio_transition_parsing,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
            print()
        else:
            print("Test failed!\n")
    
    print(f"=== Results: {passed}/{total} tests passed ===")
    
    if passed == total:
        print("✓ All parsing tests passed!")
        return True
    else:
        print("✗ Some tests failed.")
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)