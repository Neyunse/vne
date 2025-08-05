#!/usr/bin/env python3
"""Test script to run VNE engine without GUI dependencies"""

import os
import sys

# Set up environment for headless operation
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['DISPLAY'] = ':99'

# Add the current directory to Python path
sys.path.insert(0, '/home/runner/work/vne/vne')

def test_engine():
    try:
        # Import core components directly without main.py to avoid PyQt6
        from vne import Core
        from vne.config import key, file_extension, aes_extension
        from vne.aes import AES, SCRIPT_AAD
        
        # Test project path
        game_path = "projects/test-game"
        
        if not os.path.exists(game_path):
            print(f"Test game not found at {game_path}")
            return False
            
        print(f"Testing VNE engine with project: {game_path}")
        
        # Simple compilation function (from main.py without importing main.py)
        def compile_kag(source_file: str, target_file: str):
            """Compile a script file"""
            with open(source_file, "r", encoding="utf-8") as sf:
                plain_text = sf.read()
            plain_bytes = plain_text.encode("utf-8")
            compiled = AES(key).encrypt(plain_bytes, aad=SCRIPT_AAD)
            mode = "w" if isinstance(compiled, str) else "wb"
            with open(target_file, mode) as tf:
                tf.write(compiled)
            print(f"[compile] {source_file} -> {target_file}")
        
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
        
        # Compile scripts first
        data_folder = get_data_folder(game_path)
        print(f"Compiling scripts in: {data_folder}")
        compile_all_kag_in_folder(data_folder)
        
        # Try to create engine instance
        print("Creating engine instance...")
        engine = Core(game_path, devMode=True)
        
        print("Engine created successfully!")
        return True
        
    except Exception as e:
        import traceback
        print(f"Error testing engine: {e}")
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = test_engine()
    sys.exit(0 if success else 1)