#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author:     ltogt
Started:    2019-05-19
Purpose:    Base Class for Image Manipulating Simulations
"""
# =============================================== IMPORTS
import sys
import os
from abc import ABC, abstractmethod
#import os

# =============================================== GLOBALS


# =============================================== FUNCTIONS

class Simulation(ABC):
    """Base Class for Image Manipulating Simulations."""

    """Holds the description and default value for each <argument_name>.
        Defines the interface of the Simulation.
        Flag name is "--<argument_name>".
        Default Value is None <-> Non-Optional
    """
    DEFAULT_ARGUMENTS = {
        "itterations" : {
            "help" : "Number of iterations to run the Simulation.", # Help Message
            "value" : 10,                                           # Default Value; Overwrite!
            "type" : int                                            # Conversion from str
        },
        "same-image" : {
            "help" : "Output becomes Input for the next steps of the same iteration.",
            "value" : 0,
            "type" : int
        },
        "image-path" : {
            "help" : "Path to the input image.",
            "value" : None,
            "type" : str
        },
    }
    """Only used in help message."""
    SIMULATION_NAME = "Simulation Base Class."
    """Only used in help message."""
    SIMULATION_DESCRIPTION = "Base Class for IMCAs."

    @classmethod
    def print_usage(cls):
        """Generate a --help message from DEFAULT_ARGUMENTS."""
        required_args = []
        optional_args = []
        for argument in cls.DEFAULT_ARGUMENTS.keys():
            # Required arguments do not have a default value (i.e. None)
            if cls.DEFAULT_ARGUMENTS[argument]["value"] is None:
                required_args.append(argument)
            else:
                optional_args.append(argument)

        def print_argument_usage(argument, optional):
            """Print a single argument."""
            print("  --" + argument, end="" if optional else "\n")
            if optional:
                print(" [{}]".format(cls.DEFAULT_ARGUMENTS[argument]["value"]), )
            print("      " + cls.DEFAULT_ARGUMENTS[argument]["help"])

        print("Help Message for:")
        print("  " + cls.SIMULATION_NAME)
        print("Description:")
        print("  " + cls.SIMULATION_DESCRIPTION)
        print("\nRequired Arguments:")
        for argument in required_args:
            print_argument_usage(argument, False)
        print("\nOptional Arguments:")
        for argument in optional_args:
            print_argument_usage(argument, True)
        print("\n((--help|-h) to print this message.)")


    # CONSTRUCTORS ==================================================
    def __init__(self, _args=None):
        """Initialize the Simulation.

            _args:
                (dict), [None]
                See alternative constructors.

            (return an initialized Simulation)
        """
        if _args is not None:
            self.args = _args
        else:
            self.args = self.DEFAULT_ARGUMENTS

        # Check if any value is None, i.e. not filled
        for arg in self.args:
            if self.args[arg]["value"] is None:
                raise ValueError(arg + " is not filled!")
            else:
                print("{}={}".format(arg, self.args[arg]["value"]))

    @classmethod
    def from_clargs(cls, clargs=None):
        """Initialize the Simulation from the command line arguments.

            clargs:
                (list), [sys.argv[:1]]
                Command Line Arguments.

            return an initialized Simulation.
        """
        # Read argv if no prepared vector is passed
        clargs = self.argv[:1] if clargs is None else clargs
        # Use the template
        args = cls.DEFAULT_ARGUMENTS.copy()

        # map each flag to its parameter
        for i in range(len(clargs))[::2]:
            # Get current flag
            arg = clargs[i]

            # Listen for help flag (should be used only )
            if arg in ["--help", "-h"]:
                cls.print_usage()
                sys.exit()

            # . Check if conforms to flag syntax (E.g. flag / value might be missing)
            if arg[0:2] == "--":
                arg = arg[2:]
            else:
                raise ValueError("Flags should start with '--', read: " + arg)

            # Get value to flag
            val = clargs[i+1]

            # Populate dictionary with values
            args[arg]["value"] = cls._check_arg_and_value(arg, val)

        # Call the default constructor with the prepared args
        return cls(_args=args)


    @classmethod
    def from_config(cls, config_path):
        """Initialize the Simulation from a configuration file.
            (See _read_conf() / _write_conf()).

            config_path:
                (str->File)
                The path to the configuration file.

            return an initialized Simulation.
        """
        if not os.path.isfile(config_path):
            raise ValueError(config_path + " does not exist! ")

        args = cls.DEFAULT_ARGUMENTS.copy()
        with open(config_path, 'r') as config_file:
            print("Reading from " + config_file + " ...")
            for line in config_file:
                line = line.strip()
                if not line[0] == "#":
                    arg, val = line.split("=")
                    args[arg]["value"] = cls._check_arg_and_value(arg, val)

        print("Done")
        # Call the default constructor with the prepared args
        return cls(_args=args)


    # HELPERS =======================================================
    @classmethod
    def _check_arg_and_value(cls, arg, val):
        args = cls.DEFAULT_ARGUMENTS
        # Check if the parameter exists at all
        if arg in args:
            # Update the value (with conversion if one is specified)
            if "type" in args[arg]:
                return args[arg]["type"](val)
            else:
                return val
        else:
            raise ValueError("'{}' not a valid parameter! Try --help.".format(key))


    # FUNCTIONALITY =================================================
    def export_config(self, config_out_path=None, overwrite=False):
        """Export the configuration of this Simulation to a file for later re-use."""
        if config_out_path is None:
            path = self._gen_out_path(ftype="imca")
        else:
            path = config_out_path

        if os.path.isfile(path) and not overwrite:
            raise FileExistsError(path + ", call function with overwrite=True to overwrite.")

        with open(path, 'w') as out_file:
            for arg in self.args:
                out_file.write("# {}\n".format(self.args[arg]["help"]))
                out_file.write("{}={}\n".format(arg, self.args[arg]["value"]))


    def run(self):
        """Run the Simulation.

            workers: !!!!!!!!!!!1 Should be in args
                (int), [1]
                Number of parallel workers to dispatch.
                Using multiple workers segments the image.
                !When working on the same image this introduces non-deterministic behaviour!
        """#TODO reference worker non-determinism
        # TODO
        raise NotImplementedError()

    def pause():
        """Pause the Simulation."""
        # TODO
        raise NotImplementedError()

    def stop():
        """End the Simulation."""
        # TODO
        raise NotImplementedError()

    def save():
        """Save the configuration and gif for this Simulation."""
        # TODO
        raise NotImplementedError()


def main():
    args = sys.argv[1:]

    if not args:
        Simulation.print_usage()
        sys.exit(1)
    else:
        sim = Simulation.from_clargs(args)
        sim.run()
        sim.save()


# =============================================== ENTRY
if __name__ == '__main__':
    main()

