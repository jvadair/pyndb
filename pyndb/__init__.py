import os
from pickle import HIGHEST_PROTOCOL, UnpicklingError
from pickle import load as load_pickle
from pickle import dump as save_pickle
from pickle import dumps as pickle_to_string
from json import load as load_json
from json import dumps as save_json
from pyndb.encryption import encrypt, decrypt, InvalidToken
from io import BytesIO

print('pyndb v3.4.0 loaded')

"""
pyndb v3.4.0

Author: jvadair
Creation Date: 4-3-2021
Last Updated: 5-28-2022
Codename: Encrpyt

Overview: pyndb, short for Python Node Database, is a package which makes it
easy to save data to a file while also providing syntactic convenience. It
utilizes a Node structure which allows for easily retrieving nested objects.
All data is wrapped inside of a custom Node object, and stored to file as
nested dictionaries. It provides additional capabilities such as autosave, 
saving a dictionary to file, creating a file if none exists, encryption and 
more. The  original program was developed with the sole purpose of saving 
dictionaries to files, and was not released to the public.
"""


# TODO: rename function, has_any function, update function

class PYNDatabase:
    def __init__(self, file, autosave=False, filetype=None, password:str=None, salt:bytes=None, iterations:int=None):
        self.filetype = filetype
        self.password = password.encode() if password else None
        self.salt = salt if salt else b'pyndb_default'
        self.iterations = iterations if iterations else 390000
        isnewfile = False
        if file.__class__ is dict:
            self.file = None
            self.fileObj = file
        elif file.__class__ is str:
            self.file = file
            if not os.path.exists(file):
                # Create if not exists
                t = open(file, 'a+')
                t.close()
                isnewfile = True

            if self.filetype is None:  # If there is no preset filename,
                if '.' in self.file:  # And the file has an extension...
                    if not file.startswith('.') or file.count('.') == 1:
                        # If this is a hidden file, make sure it has an extension
                        extension = self.file.split('.')
                        # Changes the extension to whatever comes after the last period
                        extension = extension[len(extension)-1]
                        if extension in ('json', 'txt', 'pydb'):  # Recognized file extensions (aside from .pyndb)
                            self.filetype = extension
                        else:  # .pyndb and any unrecognized extensions default to a pickled filetype
                            self.filetype = 'pickled'
                else:  # Files without extensions are also pickled by default!
                    self.filetype = 'pickled'

            with open(file, 'rb') as temp_file_obj:
                if self.password and not isnewfile:
                    try:
                        temp_file_obj = decrypt(temp_file_obj.read(), self.password, self.salt, self.iterations)
                        temp_file_obj = BytesIO(temp_file_obj)  # Reconverts the data into its previous form
                    except InvalidToken:
                        print('Invalid token, attempting to load the database without a password.')
                        self.password = None
                        temp_file_obj.seek(0)
                if self.filetype == 'pickled':
                    try:
                        self.fileObj = load_pickle(temp_file_obj)
                    except EOFError:  # Could possibly be a bad solution to this
                        self.fileObj = {}
                    except UnpicklingError:
                        print('WARNING: This database was saved as plaintext, '
                              'but loaded as a pickled database. It has been loaded '
                              'as plaintext, but this may be deprecated in the '
                              'future. Check the documentation for further info.')
                        self.filetype = 'plaintext'
                        with open(self.file, 'r') as fallback_temp_file_obj:
                            if temp_file_obj.read() == '':  # If blank
                                self.fileObj = {}
                            else:
                                temp_file_obj.seek(0)
                                self.fileObj = eval(fallback_temp_file_obj.read())
                elif self.filetype == 'json':
                    if temp_file_obj.read() == b'':  # If blank
                        self.fileObj = {}
                    else:
                        temp_file_obj.seek(0)  # Must seek because the read method above seeks to the end of the file
                        self.fileObj = load_json(temp_file_obj)
                else:  # Assume plaintext otherwise
                    if temp_file_obj.read() == b'':  # If blank
                        self.fileObj = {}
                    else:
                        temp_file_obj.seek(0)
                        self.fileObj = eval(temp_file_obj.read().decode())
        else:
            raise TypeError('<file> must be either a filename or a dictionary.')

        self.val = self.fileObj
        self.autosave = autosave  # Is checked by set() and create() which call universal.save() if True
        self.universal = self.Universal(self.save, self.autosave, self.Node)

        if self.password:
            # This section checks if the file can be loaded properly without a password.
            # If not, pyndb makes sure to throw an error that actually corresponds with the problem.
            try:
                keys = self.fileObj.keys()
            except AttributeError:
                raise InvalidToken(
                    'The authentication you provided is invalid. The database also failed to load without credentials'
                )
        else:
            keys = self.fileObj.keys()

        for key in keys:
            setattr(self, key, self.Node(key, self.fileObj[key], self.universal))
            # consider splitting into separate function to
            # allow easily re-initializing all nodes at once

    class Node:
        def __init__(self, name, val, universal):
            self.val = val
            self.name = name
            self.universal = universal
            if type(self.val) is dict:
                for key in self.val.keys():  # Each node checks for all keys and then spawns a new Node for each one
                    setattr(self, key, self.universal.Node(key, self.val[key], self.universal))
                    # Each node gains the value of the key it represents

        def set(self, name, data, create_if_not_exist=True):
            if name in self.universal.CORE_NAMES:  # Makes sure the name does not conflict with the Core Names
                raise self.universal.Error.CoreName(f'Cannot assign name: {name} is a Core Name.')

            elif not hasattr(self, name):  # Create if not exist
                if create_if_not_exist:
                    self.create(name, val=data)
                else:
                    raise NameError(f'No such node: {name}')

            else:  # Otherwise sets like normal
                target_node = self.get(name)
                self.val[name] = data
                if type(data) is dict:  # If the new data is a dictionary
                    target_node.__init__(name, self.val[name], self.universal)
                    # Re-initializes the Node with its new data
                else:
                    target_node.val = data
                if self.universal.autosave:
                    self.universal.save()

        def get(self, *names):
            if len(names) == 1:  # If the user requests a single name,
                return getattr(self, names[0])  # Return a single Node, not a tuple.
            else:
                return tuple(getattr(self, name) for name in names)

        def delete(self, *names):
            for name in names:  # Makes sure that all the names exist
                if not hasattr(self, name):
                    raise self.universal.Error.DoesntExist(name)

            for name in names:  # Deletes all selected Nodes
                delattr(self, name)  # Removes the Node object
                del self.val[name]  # Removes the key from the represented dictionary

            if self.universal.autosave:  # Finally, save
                self.universal.save()

        def create(self, *names, val=None):
            # Prevents val from being mutable
            if val is None:
                val = {}

            if type(self.val) is not dict:
                raise TypeError(f''
                                f'{self.name} is {str(type(self.val))}, and must be dict. Consider using the '
                                f'transform method to resolve this issue.')

            for name in names:  # Error checking occurs first
                if hasattr(self, name):
                    raise self.universal.Error.AlreadyExists(name)

                elif name in self.universal.CORE_NAMES:
                    raise self.universal.Error.CoreName(f'Cannot assign name: {name} is a Core Name.')

            for name in names:  # Then, if no errors are found, create the Nodes
                setattr(self, name, self.universal.Node(name, val, self.universal))
                self.val[name] = val

            if self.universal.autosave:  # Finally, save all changes
                self.universal.save()

        def transform(self, name, new_name):
            if type(new_name) is not str:
                raise self.universal.Error.InvalidName(f'{new_name} is {type(new_name)}, and must be str')

            elif name in self.universal.CORE_NAMES:  # Makes sure the name does not conflict with the Core Names
                raise self.universal.Error.CoreName(f'Cannot assign name: {new_name} is a Core Name.')

            else:
                self.set(name, {new_name: self.get(name).val})
                if self.universal.autosave:
                    self.universal.save()

        def has(self, *names):
            attrs = dir(self)
            attrs[:] = [a for a in attrs if
                        not (a.startswith('__') and a.endswith('__')) and a not in self.universal.CORE_NAMES]
            for name in names:
                if name not in attrs:
                    return False  # If any aren't found
            return True  # If all are found

        def values(self):
            attrs = dir(self)
            attrs[:] = [a for a in attrs if
                        not (a.startswith('__') and a.endswith('__')) and a not in self.universal.CORE_NAMES]
            return attrs

    # ----- Universal Resources (accessible by Nodes) -----

    class Universal:

        VALID_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_'

        def __init__(self, save, autosave, node):
            self.save = save
            self.autosave = autosave
            self.Node = node
            self.CORE_NAMES = [
                'get',
                'set',
                'create',
                'delete',
                'transform',
                'universal',
                '__init__',
                'val',
                'name',
                'has',
                'values'
            ]
            self.MASTER_NAMES = [
                'Universal',
                'Node',
                'save',
                'autosave',
                'file',
                'fileObj',
                'filetype'
            ]

        class Error:
            class FileError(Exception):
                pass

            class AlreadyExists(Exception):
                pass

            class CoreName(Exception):
                pass

            class InvalidName(Exception):
                pass

            class DoesntExist(Exception):
                pass

    # ----- Master functions -----

    def get(self, *names):
        if len(names) == 1:  # If the user requests a single name,
            return getattr(self, names[0])  # Return a single Node, not a tuple.
        else:
            return tuple(getattr(self, name) for name in names)

    def set(self, name, data, create_if_not_exist=True):
        if name in self.universal.CORE_NAMES + self.universal.MASTER_NAMES:  # If the name is a Core Name
            # Master names are only taken into account in this statement, not in the Node version of set()
            raise self.universal.Error.CoreName(f'Cannot assign name: {name} is a Core Name.')

        elif not hasattr(self, name):  # If no Node is found
            if create_if_not_exist:
                self.create(name, val=data)
            else:
                raise NameError(f'No such node: {name}')

        else:  # Sets normally
            target_node = self.get(name)
            self.fileObj[name] = data
            if type(data) is dict:  # If the new data is a dictionary
                target_node.__init__(name, self.fileObj[name], self.universal)
            else:
                target_node.val = data
            if self.autosave:
                self.save()

    def create(self, *names, val=None):
        # Prevents val from being mutable
        if val is None:
            val = {}

        # The dict type check is not necessary for a master function, as self.fileObj will always be a dict.

        for name in names:  # Error checking occurs first
            if hasattr(self, name):
                raise self.universal.Error.AlreadyExists(name)

            elif name in self.universal.CORE_NAMES:
                raise self.universal.Error.CoreName(f'Cannot assign name: {name} is a Core Name.')

        for name in names:  # Then, if no errors are found, create the Nodes
            setattr(self, name, self.Node(name, val, self.universal))
            self.fileObj[name] = val

        if self.autosave:  # Finally, save all changes
            self.save()

    def delete(self, *names):
        for name in names:  # Makes sure that all the names exist
            if not hasattr(self, name):
                raise self.universal.Error.DoesntExist(name)

        for name in names:  # Deletes all selected Nodes
            delattr(self, name)  # Removes the Node object
            del self.fileObj[name]  # Removes the key from the main dictionary

        if self.autosave:  # Finally, save
            self.save()

    def transform(self, name, new_name):
        if type(new_name) is not str:
            raise self.universal.Error.InvalidName(f'{new_name} is {type(new_name)}, and must be str')

        elif name in self.universal.CORE_NAMES:  # Makes sure the name does not conflict with the Core Names
            # Master name check is not necessary, as the new_name object will be inside of the name Node
            raise self.universal.Error.CoreName(f'Cannot assign name: {new_name} is a Core Name.')

        else:
            self.set(name, {new_name: self.get(name).val})
            if self.autosave:
                self.save()

    def has(self, *names):
        attrs = dir(self)
        attrs[:] = [a for a in attrs if not (a.startswith('__') and a.endswith(
            '__')) and a not in self.universal.CORE_NAMES + self.universal.MASTER_NAMES]
        for name in names:
            if name not in attrs:
                return False  # If any aren't found
        return True  # If all are found

    def values(self):
        attrs = dir(self)
        attrs[:] = [a for a in attrs if not (a.startswith('__') and a.endswith(
            '__')) and a not in self.universal.CORE_NAMES + self.universal.MASTER_NAMES]
        return attrs

    def save(self, file=None):
        if file:
            pass
        elif self.file:
            file = self.file
        else:
            raise self.universal.Error.FileError(
                'Cannot open file: Class was initiated with dictionary object rather than filename. '
                'Set the file argument on this method to save to a file different than the one this class was '
                'initiated with, or change its file paramater.')

        if self.filetype == 'pickled':
            with open(file, 'wb') as temp_file_obj:
                if self.password:
                    data = pickle_to_string(self.fileObj, HIGHEST_PROTOCOL)
                    data = encrypt(data, self.password, self.salt, self.iterations)
                    temp_file_obj.write(data)
                else:
                    save_pickle(self.fileObj, temp_file_obj, HIGHEST_PROTOCOL)
        elif self.filetype == 'json':  # plaintext
            if self.password:
                with open(file, 'wb') as temp_file_obj:
                    data = save_json(self.fileObj, indent=2, sort_keys=True)
                    data = encrypt(data.encode(), self.password, self.salt, self.iterations)
                    temp_file_obj.write(data)
            else:
                with open(file, 'w') as temp_file_obj:
                    temp_file_obj.write(save_json(self.fileObj, indent=2, sort_keys=True))
        else:  # plaintext
            if self.password:
                with open(file, 'wb') as temp_file_obj:
                    data = encrypt(str(self.fileObj).encode(), self.password, self.salt, self.iterations)
                    temp_file_obj.write(data)
            else:
                with open(file, 'w') as temp_file_obj:
                    temp_file_obj.write(str(self.fileObj))
