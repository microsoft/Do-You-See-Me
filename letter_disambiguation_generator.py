import json
import colorsys
import string
import itertools
import pandas as pd
def hex_to_hsv(hex_color):
    """Convert hex color to HSV."""
    # Remove '#' if present
    hex_color = hex_color.lstrip('#')
    
    # Convert hex to RGB
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    
    # Convert RGB to HSV
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    return h, s, v

def hsv_to_hex(h, s, v):
    """Convert HSV to hex color."""
    # Convert HSV to RGB
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    
    # Convert RGB to hex
    hex_color = "#{:02x}{:02x}{:02x}".format(
        int(r * 255),
        int(g * 255),
        int(b * 255)
    )
    return hex_color.upper()

def generate_variations(base_color):
    """
    1. Hard (very close/slight variation)
    2. Medium (moderate variation)
    3. Easy (very different / significant variation)
    """
    h, s, v = hex_to_hsv(base_color)

    variations = {
        "original": base_color,
        "hard": None,
        "medium": None,
        "easy": None
    }

    # Hard: tiny hue shift, minimal saturation/value changes
    variations["hard"] = hsv_to_hex(
        (h + 10/360) % 1.0,     
        min(1.0, s * 1.05),
        min(1.0, v * 0.95)
    )

    # Medium: moderate hue shift
    variations["medium"] = hsv_to_hex(
        (h + 60/360) % 1.0,
        min(1.0, s * 1.2),
        min(1.0, v * 0.9)
    )

    # Easy: large shift for maximum contrast (complementary)
    variations["easy"] = hsv_to_hex(
        (h + 180/360) % 1.0,
        min(1.0, s * 1.2),
        min(1.0, v * 0.85)
    )

    return variations



class LetterIconGenerator:
    def __init__(self):
        # Standard 7x5 dot matrix patterns
        self.letters = {
            'A': [
                [0,1,1,1,0],
                [1,0,0,0,1],
                [1,0,0,0,1],
                [1,1,1,1,1],
                [1,0,0,0,1],
                [1,0,0,0,1],
                [1,0,0,0,1]
            ],
            'B': [
                [1,1,1,1,0],
                [1,0,0,0,1],
                [1,0,0,0,1],
                [1,1,1,1,0],
                [1,0,0,0,1],
                [1,0,0,0,1],
                [1,1,1,1,0]
            ],
            'C': [
                [0,1,1,1,0],
                [1,0,0,0,1],
                [1,0,0,0,0],
                [1,0,0,0,0],
                [1,0,0,0,0],
                [1,0,0,0,1],
                [0,1,1,1,0]
            ],
            'D': [
                [1,1,1,1,0],
                [1,0,0,0,1],
                [1,0,0,0,1],
                [1,0,0,0,1],
                [1,0,0,0,1],
                [1,0,0,0,1],
                [1,1,1,1,0]
            ],
            'E': [
                [1,1,1,1,1],
                [1,0,0,0,0],
                [1,0,0,0,0],
                [1,1,1,1,0],
                [1,0,0,0,0],
                [1,0,0,0,0],
                [1,1,1,1,1]
            ],
            'F': [
                [1,1,1,1,1],
                [1,0,0,0,0],
                [1,0,0,0,0],
                [1,1,1,1,0],
                [1,0,0,0,0],
                [1,0,0,0,0],
                [1,0,0,0,0]
            ],
            'G': [
                [0,1,1,1,0],
                [1,0,0,0,1],
                [1,0,0,0,0],
                [1,0,1,1,1],
                [1,0,0,0,1],
                [1,0,0,0,1],
                [0,1,1,1,0]
            ],
            'H': [
                [1,0,0,0,1],
                [1,0,0,0,1],
                [1,0,0,0,1],
                [1,1,1,1,1],
                [1,0,0,0,1],
                [1,0,0,0,1],
                [1,0,0,0,1]
            ],
            'I': [
                [1,1,1,1,1],
                [0,0,1,0,0],
                [0,0,1,0,0],
                [0,0,1,0,0],
                [0,0,1,0,0],
                [0,0,1,0,0],
                [1,1,1,1,1]
            ],
            'J': [
                [0,0,1,1,1],
                [0,0,0,1,0],
                [0,0,0,1,0],
                [0,0,0,1,0],
                [1,0,0,1,0],
                [1,0,0,1,0],
                [0,1,1,0,0]
            ],
            'K': [
                [1,0,0,0,1],
                [1,0,0,1,0],
                [1,0,1,0,0],
                [1,1,0,0,0],
                [1,0,1,0,0],
                [1,0,0,1,0],
                [1,0,0,0,1]
            ],
            'L': [
                [1,0,0,0,0],
                [1,0,0,0,0],
                [1,0,0,0,0],
                [1,0,0,0,0],
                [1,0,0,0,0],
                [1,0,0,0,0],
                [1,1,1,1,1]
            ],
            'M': [
                [1,0,0,0,1],
                [1,1,0,1,1],
                [1,0,1,0,1],
                [1,0,0,0,1],
                [1,0,0,0,1],
                [1,0,0,0,1],
                [1,0,0,0,1]
            ],
            'N': [
                [1,0,0,0,1],
                [1,1,0,0,1],
                [1,0,1,0,1],
                [1,0,0,1,1],
                [1,0,0,0,1],
                [1,0,0,0,1],
                [1,0,0,0,1]
            ],
            'O': [
                [0,1,1,1,0],
                [1,0,0,0,1],
                [1,0,0,0,1],
                [1,0,0,0,1],
                [1,0,0,0,1],
                [1,0,0,0,1],
                [0,1,1,1,0]
            ],
            'P': [
                [1,1,1,1,0],
                [1,0,0,0,1],
                [1,0,0,0,1],
                [1,1,1,1,0],
                [1,0,0,0,0],
                [1,0,0,0,0],
                [1,0,0,0,0]
            ],
            'Q': [
                [0,1,1,1,0],
                [1,0,0,0,1],
                [1,0,0,0,1],
                [1,0,0,0,1],
                [1,0,1,0,1],
                [1,0,0,1,0],
                [0,1,1,0,1]
            ],
            'R': [
                [1,1,1,1,0],
                [1,0,0,0,1],
                [1,0,0,0,1],
                [1,1,1,1,0],
                [1,0,1,0,0],
                [1,0,0,1,0],
                [1,0,0,0,1]
            ],
            'S': [
                [0,1,1,1,0],
                [1,0,0,0,1],
                [1,0,0,0,0],
                [0,1,1,1,0],
                [0,0,0,0,1],
                [1,0,0,0,1],
                [0,1,1,1,0]
            ],
            'T': [
                [1,1,1,1,1],
                [0,0,1,0,0],
                [0,0,1,0,0],
                [0,0,1,0,0],
                [0,0,1,0,0],
                [0,0,1,0,0],
                [0,0,1,0,0]
            ],
            'U': [
                [1,0,0,0,1],
                [1,0,0,0,1],
                [1,0,0,0,1],
                [1,0,0,0,1],
                [1,0,0,0,1],
                [1,0,0,0,1],
                [0,1,1,1,0]
            ],
            'V': [
                [1,0,0,0,1],
                [1,0,0,0,1],
                [1,0,0,0,1],
                [1,0,0,0,1],
                [1,0,0,0,1],
                [0,1,0,1,0],
                [0,0,1,0,0]
            ],
            'W': [
                [1,0,0,0,1],
                [1,0,0,0,1],
                [1,0,0,0,1],
                [1,0,0,0,1],
                [1,0,1,0,1],
                [1,1,0,1,1],
                [1,0,0,0,1]
            ],
            'X': [
                [1,0,0,0,1],
                [1,0,0,0,1],
                [0,1,0,1,0],
                [0,0,1,0,0],
                [0,1,0,1,0],
                [1,0,0,0,1],
                [1,0,0,0,1]
            ],
            'Y': [
                [1,0,0,0,1],
                [1,0,0,0,1],
                [0,1,0,1,0],
                [0,0,1,0,0],
                [0,0,1,0,0],
                [0,0,1,0,0],
                [0,0,1,0,0]
            ],
            'Z': [
                [1,1,1,1,1],
                [0,0,0,0,1],
                [0,0,0,1,0],
                [0,0,1,0,0],
                [0,1,0,0,0],
                [1,0,0,0,0],
                [1,1,1,1,1]
            ]
        }

    def generate_svg(self, letter, background_color='#FFEB3B', square_color='#03A9F4', size=800, box_spacing=0.1):
        if letter.upper() not in self.letters:
            raise ValueError(f"Letter {letter} not supported")
            
        pattern = self.letters[letter.upper()]
        
        outer_padding = size * 0.1
        inner_spacing = size * box_spacing
        
        effective_width = size - (2 * outer_padding)
        effective_height = size - (2 * outer_padding)
        
        dot_size = min(effective_width / 5, effective_height / 7) - inner_spacing
        
        grid_width = (5 * dot_size) + (4 * inner_spacing)
        grid_height = (7 * dot_size) + (6 * inner_spacing)
        
        start_x = (size - grid_width) / 2
        start_y = (size - grid_height) / 2
        
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}">
            <!-- Background -->
            <rect width="{size}" height="{size}" rx="{size * 0.1}" fill="{background_color}"/>
            '''
        border_radius = dot_size * 0.1
        


        for row in range(7):
            for col in range(5):
                if pattern[row][col] == 1:
                    x = start_x + (col * (dot_size + inner_spacing))
                    y = start_y + (row * (dot_size + inner_spacing))
                    if x<0:
                        print(letter)
                    # svg += f'''
                    # <circle 
                    #     cx="{x + dot_size/2}" 
                    #     cy="{y + dot_size/2}" 
                    #     r="{dot_size/2}"
                    #     fill="{square_color}"
                    # />'''
                    svg+= f'''<rect 
                            x="{x}" 
                            y="{y}" 
                            width="{dot_size}" 
                            height="{dot_size}" 
                            rx="{border_radius}"
                            fill="{square_color}"
                                />'''
                            # stroke="black" stroke-width="{border_radius}"

        svg += '</svg>'
        return svg

    def generate_multiple_letters(self, word, spacing_factor=0.2, **kwargs):
        word = word.upper()
        size = kwargs.get('size', 400)
        letter_spacing = size * spacing_factor
        total_width = (size * len(word)) + (letter_spacing * (len(word) - 1))
        
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {total_width} {size}">
            <!-- Main Background -->
            <rect width="{total_width}" height="{size}" fill="{kwargs.get('background_color', '#FFEB3B')}" rx="{size * 0.1}"/>
        '''
        
        for i, letter in enumerate(word):
            if letter not in self.letters:
                continue
                
            x_offset = i * (size + letter_spacing)
            letter_svg = self.generate_svg(letter, **kwargs)
            letter_content = letter_svg.split('>', 1)[1].rsplit('<', 1)[0]
            
            svg += f'''<g transform="translate({x_offset}, 0)">
                {letter_content}
            </g>'''
        
        svg += '</svg>'
        return svg

    def save_svg(self, letter, filename, **kwargs):
        svg_content = self.generate_svg(letter, **kwargs)
        with open(filename, 'w') as f:
            f.write(svg_content)
            
    def save_multiple_letters(self, word, filename, **kwargs):
        svg_content = self.generate_multiple_letters(word, **kwargs)
        with open(filename, 'w') as f:
            f.write(svg_content)
            
    def generate_preview(self, filename='alphabet_preview.svg'):
        preview_size = 1200
        letter_size = preview_size / 6  # 6 letters per row
        
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {preview_size} {preview_size}">
            <rect width="{preview_size}" height="{preview_size}" fill="#ffffff"/>
            '''
            
        for i, letter in enumerate(self.letters.keys()):
            row = i // 6
            col = i % 6
            x = col * letter_size
            y = row * letter_size
            
            letter_svg = self.generate_svg(letter, size=letter_size * 0.9)
            letter_content = letter_svg.split('>', 1)[1].rsplit('<', 1)[0]
            
            svg += f'''<g transform="translate({x}, {y})">
                {letter_content}
            </g>'''
            
        svg += '</svg>'
        
        with open(filename, 'w') as f:
            f.write(svg)
        return svg


# Example usage
generator = LetterIconGenerator()

# # # Generate preview of all letters
generator.generate_preview()



import random
import os
import shutil

# box_spacing -> [0.05, 0.1, 0.15]
background_color_list = [
    '#FAF3DD',  # Cream
    '#E8F3D6',  # Light Sage
    '#FCE4EC',  # Light Pink
    '#F0F4F8',  # Ice Blue,
    '#FFE66D',  # Light Yellow
]

square_color_list = [
    '#1B1B1B',  # Almost Black
    '#2D3436',  # Charcoal
    '#273C75',  # Navy Blue
    '#192A56',  # Dark Navy
    '#2C3A47'   # Dark Slate
]






letter_to_display = [1, 5, 9]
# 1 -> easy, 2 -> medium, 3 -> hard
color = [1, 2, 3]
box_spacing = [0.04, 0.08, 0.1]




def generate_letter_svg(background_color, square_color, box_spacing):
    letter = random.choice(list(generator.letters.keys()))
    svg = generator.generate_svg(letter, background_color=background_color, square_color=square_color, size=400, box_spacing=box_spacing)
    return letter, svg

def generate_word_svg(word_len, background_color, square_color, box_spacing):
    word = ''.join([random.choice(string.ascii_uppercase) for _ in range(word_len)])
    svg = generator.generate_multiple_letters(word, background_color=background_color, square_color=square_color, size=400, box_spacing=box_spacing)
    return word, svg


base_dir = "visual_discrimination/sweep"
sweep_dir = "letter_disambiguation"
save_path = os.path.join(base_dir, sweep_dir)

if not os.path.exists(save_path):
    os.makedirs(save_path)

sweep_list = itertools.product(letter_to_display, color, box_spacing)
data = []
idx = 0

for sweep in sweep_list:
    for i in range(5):
        letter_display, color_choice, spacing_choice = sweep
        generator = LetterIconGenerator()
        background_color = random.choice(background_color_list)
        color_map = generate_variations(base_color=background_color)
        if color_choice == 1:
            square_color = color_map["easy"]
        elif color_choice == 2:
            square_color = color_map["medium"]
        else:
            square_color = color_map["hard"]
        print(square_color)

        # if square_color == background_color:
        print(square_color, background_color)


        if letter_display == 1:
            letter, svg = generate_letter_svg(background_color, square_color, spacing_choice)
        else:
            letter, svg = generate_word_svg(letter_display, background_color, square_color, spacing_choice)
        filename = os.path.join(save_path, f'{idx}.svg')
        with open(filename, 'w') as f:
            f.write(svg)

        data.append({"filename": f'{idx}.svg', "answer": letter, "sweep": sweep})
        idx+=1
pd.DataFrame(data).to_csv(os.path.join(save_path, "dataset_info.csv"), index=False)
