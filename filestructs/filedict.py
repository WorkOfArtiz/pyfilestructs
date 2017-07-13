#!/usr/bin/env python3
import os
import pickle
import time
from threading import Thread, Lock

class FileDict(object):
    """
    A file-backed dictionairy. 
    
    The use-case is rather simple, you 'open' a file backed dictionairy, which then
    makes sure that the changes to the dictionairy are saved to persistent memory.

    The interface is as follows:

    with FileDict('/path/to/dict.bin') as file_dict:
        file_dict['hi'] = 'there'

    Afterwards, a file at /path/to/dict.bin will have been created if it doesn't exist, 
    containing a serialised dictionairy. If it already existed file_dict will contain the 
    read in data.

    Optionally can save the dictionairy to file every N seconds, allowing for more temperproof
    solutions. However, this goes at the cost of performance
    """
    
    def __init__(self, filepath, save_every=None, serialiser=pickle.dump, deserialiser=pickle.load):
        """
        @param filepath   - obligatory file path to write to
        @param save_every - if specified, will save dict to memory every `save_every` seconds
        @param serialiser - function taking (object, file) and serialising the object to that file
                            examples: pickle.dump, json.dump (limited), etc.
        @param unserialiser - function taking (file) and deserializing an object from it
                            examples: pickle.load, json.load (limited), etc.
        """
        if os.path.dirname(filepath) != '':
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

        self.serialiser = serialiser

        # we don't keep an open file descriptor due to descriptor limit
        self.filepath = filepath

        # handle not existing file
        if os.path.exists(filepath):
            try:
                with open(filepath, 'rb') as fh:
                    self.__internal = deserialiser(fh)
            except TypeError:
                with open(filepath, 'r') as fh:
                    self.__internal = deserialiser(fh)
        else:
            self.__internal = dict()

        # if save_every is a valid time, it sets up a background thread
        # saving it every N seconds, otherwise only saves on exit
        try:
            self.__file_lock   = Lock()
            self.__save_background = True
            save_every = float(save_every)
            
            thread = Thread(target=lambda:self.__updater_loop(save_every))
            thread.daemon = True
            thread.start()
        except TypeError:
            self.__save_background = False

    def __updater_loop(self, save_every):
        """
        Internal function to continuously update the object until 
        file descriptor is closed.
        """
        while self.__save_background:
            try:
                with open(self.filepath, 'w+b') as fh:
                    self.serialiser(self.__internal, fh)
            except TypeError:
                with open(self.filepath, 'w+') as fh:
                    self.serialiser(self.__internal, fh)

            time.sleep(save_every)
        
    def __enter__(self):
        return self.__internal

    def __exit__(self, type, value, traceback):
        try:
            with open(self.filepath, 'w+b') as fh:
                self.serialiser(self.__internal, fh)
        except TypeError:
            with open(self.filepath, 'w+') as fh:
                self.serialiser(self.__internal, fh)