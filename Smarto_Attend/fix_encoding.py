
import os

def fix_file(filename):
    with open(filename, 'rb') as f:
        content = f.read()
    
    # Remove null bytes
    new_content = content.replace(b'\x00', b'')
    
    if len(content) != len(new_content):
        print(f"Removed {len(content) - len(new_content)} null bytes from {filename}")
        with open(filename, 'wb') as f:
            f.write(new_content)
    else:
        print(f"No null bytes found in {filename}")

fix_file('app.py')
