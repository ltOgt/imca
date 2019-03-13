#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import imageio
from PIL import Image
def generate_pulse(
    img_dir,
    out_path,
    duration=None
):
    print("Running imca: pulse.\n")
    print("> Generating pulse for:\n  : " + str(img_dir))

    print("> Writing gif to:\n  : " + str(out_path))

    img_files = sorted([os.path.join(img_dir, i_file) for i_file in os.listdir(img_dir) if i_file[-4:] == ".png"])
    if len(img_files) < 2:
        print("Not enough images in dir!")
        sys.exit()

    imageio.mimsave
    imageio.mimsave(out_path,
        [imageio.imread(f_name) for f_name in img_files] +
        [imageio.imread(f_name) for f_name in img_files[::-1]],
        duration=duration
    )

    print("Wrote gif to " + out_path)



# ENTRY =============================================================
if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) not in [2, 3]:
        print("Usage:   python3 pulse.py <img_dir> <gif_path> [duration]")
        print("            <img_dir>  : path/to/src_dir   containing the source images.")
        print("            <gif_path> : path/to/file.gif  to which the gif is written.")
        sys.exit()

    generate_pulse(
        args[0],
        args[1],
        args[2] if len(args) == 3 else None
    )
