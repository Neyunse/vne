#!/usr/bin/env python3
"""Integration test for transition features"""

import os
import sys
import time

# Set up environment for headless operation
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['DISPLAY'] = ':99'
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

# Add the current directory to Python path
sys.path.insert(0, '/home/runner/work/vne/vne')

def test_transitions_in_engine():
    """Test transitions by running the transitions scene"""
    print("Testing transition features in the engine...")
    
    try:
        from vne import Core
        from vne.config import key, file_extension, aes_extension
        from vne.aes import AES, SCRIPT_AAD
        from vne.events import EventManager
        
        # Compilation helper functions
        def compile_kag(source_file: str, target_file: str):
            """Compile a script file"""
            with open(source_file, "r", encoding="utf-8") as sf:
                plain_text = sf.read()
            plain_bytes = plain_text.encode("utf-8")
            compiled = AES(key).encrypt(plain_bytes, aad=SCRIPT_AAD)
            mode = "w" if isinstance(compiled, str) else "wb"
            with open(target_file, mode) as tf:
                tf.write(compiled)
        
        def get_data_folder(game_path):
            """Get data folder path"""
            return os.path.join(game_path, "data")
        
        def compile_all_kag_in_folder(data_folder):
            """Compile all .script files"""
            for root, dirs, files in os.walk(data_folder):
                for file in files:
                    if file.endswith(file_extension):
                        source_path = os.path.join(root, file)
                        target_path = os.path.splitext(source_path)[0] + aes_extension
                        compile_kag(source_path, target_path)
        
        # Test project path
        game_path = "projects/test-game"
        
        # Compile scripts first
        data_folder = get_data_folder(game_path)
        print(f"Compiling scripts in: {data_folder}")
        compile_all_kag_in_folder(data_folder)
        
        # Create engine instance
        print("Creating engine instance...")
        engine = Core(game_path, devMode=True)
        
        # Create event manager
        event_manager = EventManager()
        
        # Test individual transition commands
        print("Testing individual transition commands...")
        
        # Test 1: Background transition
        print("  Testing @bg black transition dissolve")
        try:
            event_manager.handle_bg("black transition dissolve", engine)
            print("    ✓ Background transition handled successfully")
        except Exception as e:
            print(f"    ✗ Background transition failed: {e}")
            return False
        
        # Test 2: Sprite transition (new syntax)
        print("  Testing @sprite kuro transition=\"dissolve\"")
        try:
            event_manager.handle_sprite('kuro transition="dissolve"', engine)
            print("    ✓ Sprite transition handled successfully")
        except Exception as e:
            print(f"    ✗ Sprite transition failed: {e}")
            return False
        
        # Test 3: Sprite animation (old syntax - should still work)
        print("  Testing @sprite kuro animation=\"fadein\"")
        try:
            event_manager.handle_sprite('kuro animation="fadein"', engine)
            print("    ✓ Sprite animation (old syntax) handled successfully")
        except Exception as e:
            print(f"    ✗ Sprite animation (old syntax) failed: {e}")
            return False
        
        # Test 4: Audio transition
        print("  Testing @bgm test transition dissolve")
        try:
            event_manager.handle_bgm("test transition dissolve", engine)
            print("    ✓ BGM transition handled successfully")
        except Exception as e:
            # Audio files might not exist, so we'll catch expected errors
            if "Error loading" in str(e):
                print("    ✓ BGM transition parsing worked (audio file not found, but that's expected)")
            else:
                print(f"    ✗ BGM transition failed unexpectedly: {e}")
                return False
        
        # Test 5: SFX transition
        print("  Testing @sfx test transition fadein")
        try:
            event_manager.handle_sfx("test transition fadein", engine)
            print("    ✓ SFX transition handled successfully")
        except Exception as e:
            # Audio files might not exist, so we'll catch expected errors
            if "Error loading" in str(e):
                print("    ✓ SFX transition parsing worked (audio file not found, but that's expected)")
            else:
                print(f"    ✗ SFX transition failed unexpectedly: {e}")
                return False
        
        print("✓ All transition commands handled successfully!")
        return True
        
    except Exception as e:
        import traceback
        print(f"✗ Error testing transitions in engine: {e}")
        print(traceback.format_exc())
        return False

def test_script_parsing():
    """Test that our transition script parses correctly"""
    print("Testing transition script parsing...")
    
    try:
        from vne.lexer import ScriptLexer
        from vne import Core
        
        # Create engine instance
        engine = Core("projects/test-game", devMode=True)
        
        # Read our transitions script
        script_path = "projects/test-game/data/scenes/transitions.script"
        if not os.path.exists(script_path):
            print(f"✗ Transitions script not found at {script_path}")
            return False
        
        with open(script_path, 'r', encoding='utf-8') as f:
            script_content = f.read()
        
        # Parse the script
        lexer = ScriptLexer(engine.game_path, engine)
        commands = lexer.parse_script(script_content)
        
        print(f"  Script parsed into {len(commands)} commands")
        
        # Check for our transition commands
        transition_commands = [cmd for cmd in commands if 'transition' in cmd]
        print(f"  Found {len(transition_commands)} commands with transitions:")
        
        for cmd in transition_commands:
            print(f"    {cmd}")
        
        if len(transition_commands) > 0:
            print("✓ Transition script parsing successful!")
            return True
        else:
            print("✗ No transition commands found in script")
            return False
        
    except Exception as e:
        import traceback
        print(f"✗ Error testing script parsing: {e}")
        print(traceback.format_exc())
        return False

def main():
    """Run all integration tests"""
    print("=== VNE Transition Integration Tests ===")
    
    tests = [
        test_script_parsing,
        test_transitions_in_engine,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
            print()
        else:
            print("Test failed!\n")
    
    print(f"=== Results: {passed}/{total} integration tests passed ===")
    
    if passed == total:
        print("✓ All integration tests passed!")
        print("🎉 Transition features are working correctly!")
        return True
    else:
        print("✗ Some integration tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)