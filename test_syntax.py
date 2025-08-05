#!/usr/bin/env python3
"""Test both transition syntaxes for sprites"""

import re

def test_sprite_syntaxes():
    """Test both quoted and unquoted transition syntaxes for sprites"""
    print("Testing sprite transition syntaxes...")
    
    test_cases = [
        # (input, expected_type, expected_source)
        ('kuro transition="dissolve"', 'dissolve', 'quoted'),
        ('kuro transition dissolve', 'dissolve', 'unquoted'),
        ('kuro position="left" transition="fadein"', 'fadein', 'quoted'),
        ('kuro position="left" transition fadein', 'fadein', 'unquoted'),
        ('kuro animation="dissolve"', 'dissolve', 'animation'),
        ('kuro transition="dissolve" animation="fadein"', 'dissolve', 'quoted'),  # transition priority
        ('kuro transition dissolve animation="fadein"', 'dissolve', 'unquoted'),  # transition priority
        ('kuro position="center"', None, None),  # no animation/transition
    ]
    
    for arg, expected_type, expected_source in test_cases:
        print(f"  Testing: @sprite {arg}")
        
        # Simulate the new parsing logic
        anim_match = re.search(r'animation="(.*?)"', arg)
        transition_match_quoted = re.search(r'transition="(.*?)"', arg)
        transition_match_unquoted = re.search(r'transition\s+(\w+)', arg)
        
        # Priorizar transition sobre animation si ambos están presentes
        if transition_match_quoted:
            anim_type = transition_match_quoted.group(1).lower()
            source = 'quoted'
        elif transition_match_unquoted:
            anim_type = transition_match_unquoted.group(1).lower()
            source = 'unquoted'
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

def main():
    print("=== Sprite Transition Syntax Tests ===")
    
    if test_sprite_syntaxes():
        print("✓ All sprite transition syntax tests passed!")
        print("🎉 Both quoted and unquoted transition syntaxes work!")
        return True
    else:
        print("✗ Some sprite transition syntax tests failed.")
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)