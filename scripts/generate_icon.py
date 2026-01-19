import base64
import os

def create_icon():
    # 1x1 red pixel PNG
    data = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDAT\x08\xd7c\xf8\xcf\xc0\x00\x00\x03\x01\x01\x00\x18\xdd\x8d\xb0\x00\x00\x00\x00IEND\xaeB`\x82"
    
    addon_dir = os.path.join(os.path.dirname(__file__), '..', 'addon')
    icon_path = os.path.join(addon_dir, 'icon.png')
    
    with open(icon_path, 'wb') as f:
        f.write(data)
    print("Created icon.png")

if __name__ == "__main__":
    create_icon()

