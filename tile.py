#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from PIL import Image
def generate_tiling(
    img_dir,
    x_times,
    y_times,
):
    print("Running imca: tiler.\n")
    print("> Tiling images from:\n  : " + str(img_dir))
    print("> Dimensions:\n  : ({},{})".format(x_times, y_times))

    out_dir = os.path.join(img_dir, "tiled_{}_{}".format(x_times, y_times))
    print("> Writing images to:\n  : " + str(out_dir))

    if os.path.isdir(out_dir):
        d = input("Directory already exists. Create anyway? [y/n] ")
        if d in ["y", "Y"]:
            from shutil import rmtree
            abs_path = os.path.abspath(out_dir)
            rmtree(abs_path)
        else:
            print("Aborted!")
            return
    os.mkdir(out_dir)

    img_number = 0
    img_files = os.listdir(img_dir)
    img_files = sorted(img_files)
    img_files_str_len = len(str(len(img_files)))

    print(img_files)
    for img_file in img_files:
        if img_file[-4:] == ".png":
            src_img = Image.open(os.path.join(img_dir, img_file))
            x_size, y_size = src_img.size
            new_size = (x_size  * x_times, y_size * y_times)
            out_img = Image.new("RGB", new_size)

            print("Tiling image {}...".format(img_file))
            for xi in range(x_times):
                for yi in range(y_times):
                    print("\t({},{})/({},{})".format(xi+1, yi+1, x_times, y_times))
                    out_img.paste(
                        im=src_img,
                        box=(
                            xi * x_size,
                            yi * y_size
                        )
                    )

            curr_number = str(img_number)
            file_name = os.path.join(out_dir, "0"*(img_files_str_len - len(curr_number)) + curr_number + ".png")
            out_img.save(
                file_name,
                "PNG"
            )
            print("\tSaved to " + file_name)
            img_number += 1

    # Generate GIF
    if img_number > 0:
        gif_path = os.path.join(img_dir, "..", img_dir + "-" + os.path.basename(out_dir) + ".gif")
        ffmpeg_gen = "ffmpeg -i {path}/%0{len}d.png".format(path=out_dir, len=img_files_str_len)
        os.system(ffmpeg_gen + " " + gif_path)
        print("Wrote gif to " + gif_path)
    else:
        print("Failed, no images found.")


# ENTRY =============================================================
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "img_dir",
        help="Path to the generated image sequence."
    )
    parser.add_argument(
        "--x",
        metavar="X-TILING",
        dest="x",
        help="The number of tiles horizontally.",
        default=2,
        type=int
    )
    parser.add_argument(
        "--y",
        metavar="Y-TILING",
        dest="y",
        help="The number of tiles vertically.",
        default=2,
        type=int
    )
    args = parser.parse_args()

    print(args)

    generate_tiling(
        args.img_dir,
        args.x,
        args.y,
    )
