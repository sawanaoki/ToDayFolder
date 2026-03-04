from PIL import Image
import sys

def make_transparent_and_crop(input_path, output_path):
    img = Image.open(input_path).convert("RGBA")
    data = img.getdata()
    
    new_data = []
    # threshold for white
    threshold = 240
    for item in data:
        if item[0] > threshold and item[1] > threshold and item[2] > threshold:
            # Change white (also shades of white) to transparent
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
            
    img.putdata(new_data)
    
    # Get bounding box of non-transparent areas
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
        
    # Make it a square for proper icon scaling
    width, height = img.size
    max_dim = max(width, height)
    
    # Create new square transparent image
    square_img = Image.new('RGBA', (max_dim, max_dim), (255, 255, 255, 0))
    paste_x = (max_dim - width) // 2
    paste_y = (max_dim - height) // 2
    square_img.paste(img, (paste_x, paste_y), img)
    
    # Save as ico
    square_img.save(output_path, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])

if __name__ == '__main__':
    make_transparent_and_crop(
        r'C:\Users\N_Sawae\.gemini\antigravity\brain\d827eb1e-e649-4a21-8d50-d014503ebfbe\green_folder_icon_1772582740138.png', 
        r'd:\ソフト開発\ToDays\folder.ico'
    )
