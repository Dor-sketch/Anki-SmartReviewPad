import subprocess
from PIL import Image, ImageDraw

class ShapeDrawer:
    def __init__(self, shape_name, image_size=(100, 100)):
        self.shape_name = shape_name.lower()
        self.image_size = image_size
        self.image = Image.new("RGB", self.image_size, "white")
        self.draw = ImageDraw.Draw(self.image)
        self._draw_shape()

    def _draw_shape(self):
        if self.shape_name == 'circle':
            self._draw_circle()
        elif self.shape_name == 'square':
            self._draw_square()
        elif self.shape_name == 'triangle':
            self._draw_triangle()
        else:
            raise ValueError(f"Unknown shape: {self.shape_name}")


    def _draw_circle(self):
        radius = min(self.image_size) // 4
        upper_left = (self.image_size[0] // 2 - radius, self.image_size[1] // 2 - radius)
        lower_right = (self.image_size[0] // 2 + radius, self.image_size[1] // 2 + radius)
        self.draw.ellipse([upper_left, lower_right], outline="black", width=2)

    def _draw_square(self):
        side_length = min(self.image_size) // 2
        upper_left = (self.image_size[0] // 2 - side_length // 2, self.image_size[1] // 2 - side_length // 2)
        lower_right = (self.image_size[0] // 2 + side_length // 2, self.image_size[1] // 2 + side_length // 2)
        self.draw.rectangle([upper_left, lower_right], outline="black", width=2)

    def _draw_triangle(self):
        height = min(self.image_size) // 2
        base = min(self.image_size) // 2
        top = (self.image_size[0] // 2, self.image_size[1] // 2 - height // 2)
        bottom_left = (self.image_size[0] // 2 - base // 2, self.image_size[1] // 2 + height // 2)
        bottom_right = (self.image_size[0] // 2 + base // 2, self.image_size[1] // 2 + height // 2)
        self.draw.polygon([top, bottom_left, bottom_right], outline="black", width=2)

    def show_notification(self):
        # Save the image temporarily
        temp_file_path = "/tmp/shape.png"
        self.image.save(temp_file_path)

        # AppleScript to show notification
        apple_script = (
            'display notification "Here is your ' + self.shape_name +
            '" with title "ShapeDrawer" subtitle "Your shape is ready!" ' +
            'sound name "Glass"'
        )
        subprocess.run(["osascript", "-e", apple_script])



# Example usage
drawer = ShapeDrawer('circle')
drawer.show_notification()

drawer = ShapeDrawer('square')
drawer.show_notification()

drawer = ShapeDrawer('triangle')
drawer.show_notification()






import re

def find_shapes(text):
    shapes = ['circle', 'triangle', 'square', 'rectangle']
    found_shapes = re.findall('|'.join(shapes), text, re.IGNORECASE)
    return found_shapes



import base64

def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        # Read the file
        encoded_string = base64.b64encode(image_file.read())
    return encoded_string.decode('utf-8')

image_path = "/Users/dorpascal/Library/Application Support/Anki2/addons21/Anki-SmartReviewPad/square.png"
encoded_string = image_to_base64(image_path)
print(encoded_string)
