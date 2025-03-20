import qrcode
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import argparse

def create_custom_qr(data="1", output_file="ar_marker.png", size=400):
    """
    Creates a QR code compatible with AR.js that contains the marker ID.
    
    Args:
        data: The marker ID to encode (default: "1")
        output_file: The filename to save the QR code to
        size: Size of the QR code image in pixels
    """
    # Create QR code instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    
    # Add data
    qr.add_data(data)
    qr.make(fit=True)
    
    # Create an image from the QR Code
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_img = qr_img.resize((size, size))
    
    # Add a border and title
    canvas = Image.new('RGB', (size + 80, size + 120), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)
    
    # Try to load a font, use default if not available
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    # Add text
    draw.text((40, 20), "AR Hologram Marker", fill=(0, 0, 0), font=font)
    draw.text((40, size + 60), "Scan with AR app", fill=(0, 0, 0), font=font)
    
    # Paste QR code
    canvas.paste(qr_img, (40, 40))
    
    # Save the QR code
    canvas.save(output_file)
    print(f"QR code saved to {output_file}")
    
    return output_file

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate QR code for AR app')
    parser.add_argument('--data', default="1", help='The marker ID to encode (default: 1)')
    parser.add_argument('--output', default="ar_marker.png", help='Output filename')
    parser.add_argument('--size', type=int, default=400, help='Size of QR code in pixels')
    
    args = parser.parse_args()
    create_custom_qr(args.data, args.output, args.size)