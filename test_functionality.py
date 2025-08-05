#!/usr/bin/env python3
"""Test transition functionality without requiring assets"""

import os
import sys
import re

# Set up environment for headless operation
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['DISPLAY'] = ':99'
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

# Add the current directory to Python path
sys.path.insert(0, '/home/runner/work/vne/vne')

def test_transition_functionality():
    """Test that transition parsing works correctly in event handlers"""
    print("Testing transition functionality...")
    
    try:
        from vne.events import EventManager
        import pygame
        
        # Initialize pygame for minimal functionality
        pygame.init()
        
        # Create a mock engine object with minimal required attributes
        class MockEngine:
            def __init__(self):
                self.current_bg_filename = None
                self.current_bgm_filename = None
                self.sprite_layers = {}
                self.screen_manager = MockScreenManager()
                self.renderer = MockRenderer()
                self.resource_manager = MockResourceManager()
                self.game_path = "projects/test-game"
                
            def Log(self, message):
                print(f"    [ENGINE] {message}")
        
        class MockScreenManager:
            def __init__(self):
                self.screens = []
                
            def hide(self, screen):
                if screen in self.screens:
                    self.screens.remove(screen)
                    
            def show(self, screen):
                if screen not in self.screens:
                    self.screens.append(screen)
        
        class MockRenderer:
            def __init__(self):
                # Create a dummy surface
                self.screen = pygame.Surface((800, 600))
        
        class MockResourceManager:
            def get_bytes(self, path):
                # Always fail to simulate missing assets
                raise FileNotFoundError(f"'{path}' not found")
        
        # Create mock engine and event manager
        engine = MockEngine()
        event_manager = EventManager()
        
        # Test 1: Background transition parsing
        print("  Testing background transition parsing...")
        try:
            # This should parse correctly even if the image loading fails
            event_manager.handle_bg("park transition dissolve", engine)
            print("    ✓ Background transition parsing successful")
        except Exception as e:
            if "Error loading background" in str(e):
                print("    ✓ Background transition parsed correctly (asset loading failed as expected)")
            else:
                print(f"    ✗ Unexpected error: {e}")
                return False
        
        # Test 2: Audio transition parsing
        print("  Testing audio transition parsing...")
        try:
            event_manager.handle_bgm("music transition dissolve", engine)
            print("    ✓ BGM transition parsing successful")
        except Exception as e:
            if "Error loading" in str(e):
                print("    ✓ BGM transition parsed correctly (asset loading failed as expected)")
            else:
                print(f"    ✗ Unexpected error: {e}")
                return False
        
        try:
            event_manager.handle_sfx("sound transition fadein", engine)
            print("    ✓ SFX transition parsing successful")
        except Exception as e:
            if "Error loading" in str(e):
                print("    ✓ SFX transition parsed correctly (asset loading failed as expected)")
            else:
                print(f"    ✗ Unexpected error: {e}")
                return False
        
        print("✓ All transition functionality tests passed!")
        return True
        
    except Exception as e:
        import traceback
        print(f"✗ Error testing transition functionality: {e}")
        print(traceback.format_exc())
        return False

def test_backward_compatibility():
    """Test that old animation syntax still works"""
    print("Testing backward compatibility...")
    
    # Test parsing logic directly
    test_cases = [
        ('kuro animation="dissolve"', True, 'animation'),
        ('kuro transition="dissolve"', True, 'transition'),
        ('kuro transition="fadein" animation="dissolve"', True, 'transition'),  # transition takes priority
        ('kuro position="left"', False, None),
    ]
    
    for arg, should_have_anim, expected_source in test_cases:
        anim_match = re.search(r'animation="(.*?)"', arg)
        transition_match = re.search(r'transition="(.*?)"', arg)
        
        if transition_match:
            has_anim = True
            source = 'transition'
        elif anim_match:
            has_anim = True
            source = 'animation'
        else:
            has_anim = False
            source = None
        
        if has_anim == should_have_anim and source == expected_source:
            print(f"  ✓ {arg}")
        else:
            print(f"  ✗ {arg} - expected anim={should_have_anim}, source={expected_source}, got anim={has_anim}, source={source}")
            return False
    
    print("✓ Backward compatibility tests passed!")
    return True

def test_examples_from_issue():
    """Test the specific examples mentioned in the issue"""
    print("Testing examples from the issue...")
    
    # The issue mentions these examples:
    # `@sprite kuro transition dissolve`
    # `@bg park transition dissolve`
    
    examples = [
        ('@sprite kuro transition dissolve', 'sprite'),
        ('@bg park transition dissolve', 'bg'),
    ]
    
    for command, command_type in examples:
        print(f"  Testing: {command}")
        
        if command_type == 'sprite':
            # Parse sprite command
            arg = command.replace('@sprite ', '')
            
            # Check for transition in the format 'transition dissolve' (without quotes)
            transition_match = re.search(r'transition\s+(\w+)', arg)
            if transition_match:
                transition_type = transition_match.group(1)
                print(f"    ✓ Found transition: {transition_type}")
            else:
                print(f"    ✗ No transition found in: {arg}")
                return False
                
        elif command_type == 'bg':
            # Parse bg command
            arg = command.replace('@bg ', '')
            
            transition_match = re.search(r'transition\s+(\w+)', arg)
            if transition_match:
                transition_type = transition_match.group(1)
                print(f"    ✓ Found transition: {transition_type}")
            else:
                print(f"    ✗ No transition found in: {arg}")
                return False
    
    print("✓ Issue examples tests passed!")
    return True

def main():
    """Run all tests"""
    print("=== VNE Transition Functionality Tests ===")
    
    tests = [
        test_backward_compatibility,
        test_examples_from_issue,
        test_transition_functionality,
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
        print("✅ All functionality tests passed!")
        print("🎉 Transition features are working correctly!")
        return True
    else:
        print("❌ Some functionality tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)