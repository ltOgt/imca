#!/usr/bin/env python3
# -*- coding: utf-8 -*-
def defend(own_weapon, enemy_weapon, number_of_weapons, weapon_range):
    # survive same color
    if own_weapon == enemy_weapon:
        return True
    # survive pre-neighbours
    for pre in range(weapon_range[0]):
        if (own_weapon - 1 - pre) % number_of_weapons == enemy_weapon:
            return True
    # survive post-neighbours
    for post in range(weapon_range[1]):
        if (own_weapon + 1 + post) % number_of_weapons == enemy_weapon:
            return True
    return False


def defend_against_neighbours(
    xy, src,
    number_of_weapons, weapon_range,
    loss_threshold,
    overlap_x=True, overlap_y=True,
):
    """Get the values from all neighbours

        xy:
            (pair)
            (X,Y) pixel-coordinates.
            Grid from top-left (0,0) to bottom-right (max_x, max_y).
        src:
            (PIL.Image.Image)
            The source image.
        number_of_weapons:
            (int)
            The number of color levels, each representing a "weapon" in rock-paper-scissor-... game.
        weapon_range:
            (pair(int,int))
            The size of the defendable neighbourhood. (BEFORE, AFTER)
        loss_threshold:
            (int)
            After how many losses a cell dies.

        OPTIONALS
        overlap_x:
            (bool)
            Whether or not x-neighbours should wrap at the edges.
        overlap_y:
            (bool)
            Whether or not y-neighbours should wrap at the edges.

        RETURNS
        The new value for the specified coordinate.
    """
    # ============================================================ setup
    # easier access
    x, y = xy
    x_len = src.width
    x_max = x_len - 1
    y_len = src.height
    y_max = y_len - 1

    # ============================================================ calculation
    # NOTE: getpixel returns index of the palette if palette is used
    own_weapon = src.getpixel(xy)

    def on_loss(enemy_weapon):
        return enemy_weapon

    losses = 0

    # X- : add x above
    if overlap_x or x > 0:
        enemy_xy = ((x-1) % x_len, y)
        enemy_weapon = src.getpixel(enemy_xy)
        result = defend(
            own_weapon=own_weapon,
            enemy_weapon=enemy_weapon,
            number_of_weapons=number_of_weapons,
            weapon_range=weapon_range
        )
        if not result:
            losses += 1
            if losses == loss_threshold:
                return on_loss(enemy_weapon)

    # X+ : add x below
    if overlap_x or x < x_max:
        enemy_xy = ((x+1) % x_len, y)
        enemy_weapon = src.getpixel(enemy_xy)
        result = defend(
            own_weapon=own_weapon,
            enemy_weapon=enemy_weapon,
            number_of_weapons=number_of_weapons,
            weapon_range=weapon_range
        )
        if not result:
            losses += 1
            if losses == loss_threshold:
                return on_loss(enemy_weapon)

    # Y- : add y left
    if overlap_y or y > 0:
        enemy_xy = (x, (y-1) % y_len)
        enemy_weapon = src.getpixel(enemy_xy)
        result = defend(
            own_weapon=own_weapon,
            enemy_weapon=enemy_weapon,
            number_of_weapons=number_of_weapons,
            weapon_range=weapon_range
        )
        if not result:
            losses += 1
            if losses == loss_threshold:
                return on_loss(enemy_weapon)

    # Y+ : add y right
    if overlap_y or y < y_max:
        enemy_xy = (x, (y+1) % y_len)
        enemy_weapon = src.getpixel(enemy_xy)
        result = defend(
            own_weapon=own_weapon,
            enemy_weapon=enemy_weapon,
            number_of_weapons=number_of_weapons,
            weapon_range=weapon_range
        )
        if not result:
            losses += 1
            if losses == loss_threshold:
                return on_loss(enemy_weapon)

    return own_weapon


def discretize(src, levels):
    out = src.convert('P', palette=Image.ADAPTIVE, colors=levels)
    p_ = out.getpalette()
    weapons = {(p_[i*3], p_[i*3+1], p_[i*3+2]) : i for i in range(levels)}
    return out, weapons


import numpy as np
from PIL import Image
import os
def generate_images(
    img_path,
    iterations,
    name,
    number_of_weapons,
    weapon_range,
    log_dist,
    loss_threshold,
    fixed_threshold,
    overlap_x,
    overlap_y,
    new_image
):
    print("Running imca: rock-paper-scissor\n")
    print("> Number of weapons:\n  : " + str(number_of_weapons))
    print("> Weapon range:\n  : " + str(weapon_range))
    print("> Loss threshold:\n  : " + str(loss_threshold))
    print("> Fix threshold:\n  : " + str(fixed_threshold))
    print("> Overlap-x:\n  : " + str(overlap_x))
    print("> Overlap-y:\n  : " + str(overlap_y))
    print("> New image:\n  : " + str(new_image))

    print("> Loading image: " + img_path)
    img = Image.open(img_path)

    # TODO: use discretized for calculations but original for rendering
    img, weapons = discretize(img, number_of_weapons)
    print("> Discretizing image to {} levels: \n  : {}".format(number_of_weapons, weapons))

    # Create out folder
    loc_path = "{name}-Src_{img}-Lvl_{lvl}-Rng_{wr_pre}_{wr_post}-TH_{th}_{fth}-Ref_{ni}".format(
        name=name,
        img="".join(img_path.split(".")[:-1]),
        lvl=number_of_weapons,
        wr_pre=weapon_range[0],
        wr_post=weapon_range[1],
        th=loss_threshold,
        fth=fixed_threshold,
        ni=new_image
    )

    print(">>> " + loc_path)
    if os.path.isdir(loc_path):
        d = input("Directory already exists. Create anyway? [y/n]")
        if d not in ["y", "Y"]:
            print("Aborted!")
            return
        from shutil import rmtree
        abs_path=os.path.abspath(loc_path)
        rmtree(abs_path)
    os.mkdir(loc_path)

    total_pixels = img.width * img.height

    _l_t = loss_threshold

    for iteration in range(iterations):
        print("Iteration {}/{};".format(
            "0"*(len(str(iterations)) - len(str(iteration))) + str(iteration),
            iterations
        ))

        # The source image to look up weapons
        img_ref=None
        if new_image:
            # store previous values separately
            img_ref = img.copy()
        else:
            # read values from the changing image
            img_ref = img

        finished_pixels = 0
        current_progress = -1

        # loop over coordinates
        for x, y in np.ndindex(img.size):
            # log progress
            if log_dist is not None:
                progress = (finished_pixels / total_pixels) * 100
                if current_progress != progress and ( progress % log_dist) == 0:
                    current_progress = progress
                    print("\tPixel {}/{}".format(
                        "0"*(len(str(total_pixels)) - len(str(finished_pixels))) + str(finished_pixels),
                        total_pixels
                    ))

            # change loss threshold based on iteration
            if not fixed_threshold:
                loss_threshold = iteration % _l_t

            # set each pixel by channel
            img.putpixel(
                xy=(x,y),
                value=defend_against_neighbours(
                    xy=(x,y),
                    src=img_ref,
                    number_of_weapons=number_of_weapons,
                    weapon_range=weapon_range,
                    loss_threshold=loss_threshold,
                    overlap_x=overlap_x,
                    overlap_y=overlap_y,
                )
            )
            finished_pixels += 1

        # save after every pixel has been updated
        file_name = loc_path + "/" + "0" * (
            len(str(iterations)) - len(str(iteration))
        ) + str(iteration) + ".png"
        img.save(
            file_name,
            "PNG"
        )
        print("\tSaved to " + file_name)

    # Generate GIF
    os.system("ffmpeg -i "+loc_path+"/%0"+str(len(str(iterations)))+"d.png "+loc_path+".gif")
    print("Wrote gif to "+loc_path+".gif")


# ENTRY =============================================================
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "img_path",
        help="Path to the input image."
    )
    parser.add_argument(
        "--i",
        metavar="ITERATIONS",
        dest="iterations",
        help="The number of iterations to run.",
        default=100,
        type=int
    )
    parser.add_argument(
        "--nw",
        metavar="NUMBER_OF_WEAPONS",
        dest="number_of_weapons",
        help="The number of weapons/colorlevels.",
        default=3,
        type=int
    )
    parser.add_argument(
        "--wr-pre",
        metavar="PRE",
        dest="wr_pre",
        help="Each defender can survive attacks by its PRE previous neighbours.",
        default=0,
        type=int
    )
    parser.add_argument(
        "--wr-post",
        metavar="POST",
        dest="wr_post",
        help="Each defender can survive attacks by its POST following neighbours.",
        default=1,
        type=int
    )
    parser.add_argument(
        "--log-dist",
        metavar="LOG_DIST",
        dest="log_dist",
        help="Progress is reported in LOG_DIST % steps. (None->No logging)",
        default=None,
        type=int
    )
    parser.add_argument(
        "--lt",
        metavar="LOSS_THRESHOLD",
        dest="loss_threshold",
        help="Defender needs to loose LOSS_THRESHOLD matches to be replaced.",
        default=2,
        type=int
    )
    parser.add_argument(
        "--f-lt",
        metavar="FIXED_THRESHOLD",
        dest="fixed_threshold",
        help="Whether or not to cycle 0..LOSS_THRESHOLD (0/1)",
        default=1,
        type=int
    )
    parser.add_argument(
        "--overlap_x",
        metavar="OVERLAP_x",
        dest="overlap_x",
        help="Whether or not (1/0) the x-borders should wrap.",
        default=1,
        type=int
    )
    parser.add_argument(
        "--overlap_y",
        metavar="OVERLAP_Y",
        dest="overlap_y",
        help="Whether or not (1/0) the y-borders should wrap.",
        default=1,
        type=int
    )
    parser.add_argument(
        "--new-image",
        metavar="NEW_IMAGE",
        dest="new_image",
        help="Whether or not (1/0) to calculate the results from a copy of the picture (otherwise on same image).",
        default=1,
        type=int
    )

    args = parser.parse_args()
    print(args)

    generate_images(
        img_path=args.img_path,
        iterations=args.iterations,
        name="rps",
        number_of_weapons=args.number_of_weapons,
        weapon_range=(args.wr_pre, args.wr_post),
        log_dist=args.log_dist,
        loss_threshold=args.loss_threshold,
        fixed_threshold=args.fixed_threshold,
        overlap_x=args.overlap_x,
        overlap_y=args.overlap_y,
        new_image=args.new_image
    )
