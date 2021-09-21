# Used to save the game
import pickle

from engine.world import World


# This file handles the pickling of world into a file to be loaded later.
def save() -> None:
    filename = "CurrentSave"
    outfile = open(filename, "wb")
    pickle.dump(World, outfile)
    outfile.close()


def load() -> World:
    filename = "CurrentSave"
    infile = open(filename, "rb")
    loadedWorld = pickle.load(infile)
    infile.close()
    return loadedWorld
