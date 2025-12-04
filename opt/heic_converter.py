import os
import sys
from heic2png import HEIC2PNG

def main():
    inp_dir = sys.argv[1]
    out_dir = sys.argv[2]

    files = os.listdir(inp_dir)
    for i, file in enumerate(files):
        png_img = HEIC2PNG(f"{inp_dir}/{file}", quality=50)
        png_img.save(output_image_file_path=f"{out_dir}/{i}.png")
    print(files)

    return

if __name__ == "__main__":
    main()