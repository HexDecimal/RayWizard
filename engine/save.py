# Used to save the game
import pickle

from engine.world import World  # Used to fetch the current world for saving
import g  # used to set the active world


# This file handles the pickling of world into a file to be loaded later.
def save() -> None:
    filename = "CurrentSave"
    outfile = open(filename, "wb")
    pickle.dump(World, outfile)
    outfile.close()


def load() -> None:
    filename = "CurrentSave"
    infile = open(filename, "rb")
    g.world = pickle.load(infile)
    infile.close()
