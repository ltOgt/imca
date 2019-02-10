#!/usr/bin/env python3
# -*- coding: utf-8 -*-

NUM_NEIGHBOURS = 8

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
    nh_seed="01010101", nh_order="01234567",
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
        nh_seed:
            (str)
            Neighbourhood seed: Which neighbours are able to attack the current pixel.
            Default: 01010101
            "{top-left}{top}{top-right}{right}{right-bottom}{bottom}{left-bottom}{left}"
            Input is EXPECTED padded with 0 to len()=8 or cut off after 8.

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
    losses = 0

    # allowed to wrap or no border to left
    can_left  = overlap_x or x > 0
    # allowed to wrap or no border above
    can_up    = overlap_y or y > 0
    # allowed to wrap or no border to right
    can_right = overlap_x or x < x_max
    # allowed to wrap or no border below
    can_down  = overlap_y or y < y_max

    attackers = [
        # (-X,-Y) TOP-LEFT
        (
            int(nh_seed[0]) and can_up and can_left,
            ((x-1) % x_len, (y-1) % y_len)
        ),
        # ( X,-Y) TOP
        (
            int(nh_seed[1]) and can_up,
            (x, (y-1) % y_len)
        ),
        # (+X,-Y) TOP-RIGHT
        (
            int(nh_seed[2]) and can_up and can_right,
            ((x+1) % x_len, (y-1) % y_len)
        ),
        # (+x, Y) RIGHT
        (
            int(nh_seed[3]) and can_right,
            ((x+1) % x_len, y)
        ),
        # (+X,+Y) BOTTOM-RIGHT
        (
            int(nh_seed[4]) and can_down and can_right,
            ((x+1) % x_len, (y+1) % y_len)
        ),
        # ( X,+Y) BOTTOM
        (
            int(nh_seed[5]) and can_down,
            (x, (y+1) % y_len)
        ),
        # (-X,+Y) BOTTOM-LEFT
        (
            int(nh_seed[6]) and can_down and can_left,
            ((x-1) % x_len, (y+1) % y_len)
        ),
        # (-X, Y) LEFT
        (
            int(nh_seed[7]) and can_left,
            ((x-1) % x_len, y)
        ),
    ]

    for order_to_neighbour in nh_order:
        attacker = attackers[int(order_to_neighbour)]
        if attacker[0]:
            enemy_weapon = src.getpixel(attacker[1])
            won = defend(
                own_weapon=own_weapon,
                enemy_weapon=enemy_weapon,
                number_of_weapons=number_of_weapons,
                weapon_range=weapon_range
            )
            if not won:
                losses += 1
                if losses >= loss_threshold:
                    return enemy_weapon

    return own_weapon


def discretize(src, levels):
    out = src.convert('P', palette=Image.ADAPTIVE, colors=levels)
    p_ = out.getpalette()
    weapons = {(p_[i*3], p_[i*3+1], p_[i*3+2]) : i for i in range(levels)}
    return out, weapons


def gen_file_name(loc_path, number, total):
    return loc_path + "/" + "0" * (
        len(str(total)) - len(str(number))
    ) + str(number) + ".png"


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
    nh_seed,
    nh_order,
    new_image
):
    print("Running imca: rock-paper-scissor\n")
    print("> Number of weapons:\n  : " + str(number_of_weapons))
    print("> Weapon range:\n  : " + str(weapon_range))
    print("> Loss threshold:\n  : " + str(loss_threshold))
    print("> Fix threshold:\n  : " + str(fixed_threshold))
    print("> Overlap-x:\n  : " + str(overlap_x))
    print("> Overlap-y:\n  : " + str(overlap_y))
    print("> Neighbourhood-Seed:\n  : " + str(nh_seed))
    print("> Neighbourhood-Order:")
    for i in range(len(nh_order)):
        print("  #{} -> NH-Index-{}".format(i, nh_order[i]))
    print("> New image:\n  : " + str(new_image))

    print("> Loading image: " + img_path)
    img = Image.open(img_path)

    # TODO: use discretized for calculations but original for rendering
    img, weapons = discretize(img, number_of_weapons)
    print("> Discretizing image to {} levels: \n  : {}".format(number_of_weapons, weapons))

    # Create out folder
    loc_path = "{name}-Src_{img}-Lvl_{lvl}-Rng_{wr_pre}_{wr_post}-TH_{th}_{fth}-Ref_{ni}-NhS_{nhs}-NhO_{nho}-wXY_{wx}_{wy}".format(
        name=name,
        img="".join(img_path.split(".")[:-1]),
        lvl=number_of_weapons,
        wr_pre=weapon_range[0],
        wr_post=weapon_range[1],
        th=loss_threshold,
        fth=fixed_threshold,
        ni=new_image,
        nhs=nh_seed,
        nho=nh_order,
        wx=int(overlap_x),
        wy=int(overlap_y),
    )

    print(">>> " + loc_path)

    iteration = 1

    if os.path.isdir(loc_path):
        d = input("Directory already exists. Create anyway? [y/n/continue] ")
        if d.lower() in ["c", "continue"]:
            max_it = 0
            load_file = ""
            for f in os.listdir(loc_path):
                print(f)
                # find largest existing iteration
                if not os.path.isfile(loc_path + "/" + f):
                    continue
                try:
                    # get only the number component
                    new_ = int(f.split(".")[0])
                    if new_ > max_it:
                        load_file = f
                        max_it = new_
                except Exception:
                    continue
            # last iteration and the image of that iteration
            iteration = max_it + 1
            load_path = loc_path + '/' + load_file

            # ask user how to proceed
            if iteration < iterations:
                d = input("{iteration}(+initial) iterations exist. Add {iterations} more (1) or fill up to {iterations} (2): ".format(
                    iteration=iteration-1,
                    iterations=iterations
                ))
                if d == "1":
                    iterations = iterations + iteration
                elif d == "2":
                    # Nothing needed to do.
                    pass
                else:
                    print("Not an option! Exit...")
                    return
            else:
                d = input("{iteration}(+initial) iterations exist. Add {iterations}? [y/n] ".format(
                    iteration=iteration-1,
                    iterations=iterations
                ))
                if d in ["y", "Y"]:
                    iterations = iterations + iteration
                else:
                    print("Exit...")
                    return
            print("Starting: {}/{}".format(iteration, iterations))

            # LOAD IMAGE ------------------------------
            print("Loading " + load_path)
            img, weapons = discretize(Image.open(load_path), number_of_weapons)

        elif d in ["y", "Y"]:
            from shutil import rmtree
            abs_path=os.path.abspath(loc_path)
            rmtree(abs_path)
            os.mkdir(loc_path)
        else:
            print("Aborted!")
            return
    else:
        os.mkdir(loc_path)

    total_pixels = img.width * img.height

    _l_t = loss_threshold

    # save initial image as well
    if iteration == 1:
        # Only if not a continuation from before
        file_name = gen_file_name(loc_path, 0, iterations + 1)
        img.save(
            file_name,
            "PNG"
        )
        print("\tSaved to " + file_name)

    # generate following images
    for iteration in range(iteration, iterations + 1):
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
                    nh_seed=nh_seed,
                    nh_order=nh_order,
                )
            )
            finished_pixels += 1

        # save after every pixel has been updated
        file_name = gen_file_name(loc_path, iteration, iterations + 1)
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
        "--nh-seed",
        metavar="SEED",
        dest="nh_seed",
        help='Neighbourhood seed: Which neighbours are able to attack the current pixel. Default: "01010101" ("{top-left}{top}{top-right}{right}{right-bottom}{bottom}{left-bottom}{left}"). Input is padded with 0 to len()=str(NUM_NEIGHBOURS) or cut off after "+str(NUM_NEIGHBOURS)".',
        default="01010101",
        type=str
    )
    parser.add_argument(
        "--new-image",
        metavar="NEW_IMAGE",
        dest="new_image",
        help="Whether or not (1/0) to calculate the results from a copy of the picture (otherwise on same image).",
        default=1,
        type=int
    )
    parser.add_argument(
        "--nh-order",
        metavar="ORDER",
        dest="nh_order",
        help='Neighbourhood ordering number: In which order neighbours are defended against. Default: "01234567" ("{top-left}{top}{top-right}{right}{right-bottom}{bottom}{left-bottom}{left}"). Input is padded with the remaining numbers in ascending order. Double numbers may not be entered. Only the "+str(NUM_NEIGHBOURS)+" first chars are kept.',
        default="01234567",
        type=str
    )

    args = parser.parse_args()

    # Neighbourhood indexes:
    # +-----+
    # | 012 |
    # | 7.3 |
    # | 654 |
    # +-----+

    # Turn on or of neighbours ability to attack
    _nhs = args.nh_seed
    args.nh_seed = str(_nhs + "0"*max(0, NUM_NEIGHBOURS - len(_nhs)))[:NUM_NEIGHBOURS]

    # Change the order of attack by defining their position in the order by index
    _nho = args.nh_order
    _nho = str(_nho[:max(len(_nho), NUM_NEIGHBOURS)])

    # Keep track of unfilled with None
    order_mapping = [None]*NUM_NEIGHBOURS
    # Itterate over the neighbourhood index
    for neighbour_index in range(len(_nho)):
        _char = _nho[neighbour_index]
        if order_mapping[int(_char)] is not None:
            # The positions assigned by the argument have to be unique
            raise ValueError("No double values: {} at index {}".format(_char, neighbour_index))
        elif int(_char) > NUM_NEIGHBOURS - 1:
            raise ValueError("Ordering number can not exceed number of neighbours: {} > {}".format(_char, NUM_NEIGHBOURS))
        else:
            # The first position of the _nho defines the ordering of the top-left corner ...
            # Use this ordering number to index the current i (top-left ...).
            order_mapping[int(_char)] = neighbour_index

    def first_remaining_ordering_number(order_mapping):
        for ordering_number in range(NUM_NEIGHBOURS):
            if order_mapping[ordering_number] is None:
                return ordering_number

    # if not all indexes were ordered
    num_unordered = NUM_NEIGHBOURS - len(_nho)
    if num_unordered > 0:
        # add the remaining ordering numbers to the last neighbourhood indexes
        first_unordered = len(_nho)
        for offset in range(num_unordered):
            # find the first remaining ordering number
            ordering_number = first_remaining_ordering_number(order_mapping)
            print("{}: {} + {}".format(ordering_number, first_unordered, offset))
            order_mapping[ordering_number] = first_unordered + offset

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
        nh_seed=args.nh_seed,
        nh_order="".join(str(i) for i in order_mapping),
        new_image=args.new_image
    )
