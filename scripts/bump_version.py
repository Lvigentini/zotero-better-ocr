import json
import argparse
import os

def bump_version(part='patch'):
    manifest_path = os.path.join(os.path.dirname(__file__), '..', 'addon', 'manifest.json')
    manifest_path = os.path.abspath(manifest_path)

    with open(manifest_path, 'r') as f:
        data = json.load(f)

    # Browser_specific_settings version (Zotero 7 style) or top-level version
    # We maintain top-level version for compatibility
    current_ver = data.get('version', '1.0.0')
    major, minor, patch = map(int, current_ver.split('.'))

    if part == 'major':
        major += 1
        minor = 0
        patch = 0
    elif part == 'minor':
        minor += 1
        patch = 0
    else: # patch
        patch += 1

    new_ver = f"{major}.{minor}.{patch}"
    data['version'] = new_ver
    
    # Save back
    with open(manifest_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Bumped version: {current_ver} -> {new_ver}")
    return new_ver

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('part', choices=['major', 'minor', 'patch'], default='patch', nargs='?')
    args = parser.parse_args()
    bump_version(args.part)
