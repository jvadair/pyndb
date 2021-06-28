import os

print('PYN DB v2.654 loaded')

"""
PYN DB v2.654

Author: jvadair
Creation Date: 4-3-2021
Last Updated: 6-27-2021
Codename: PynCone

Overview: PYN DB, short for Python Node Database, is a pacakge which makes it
easy to save data to a file while also providing syntactic convenience. It
utilizes a Node structure which allows for easily retrieving nested objects. All
data is wrapped inside of a custom Node object, and stored to file as nested
dictionaries. It provides additional capabilities such as autosave, saving a
dictionary to file, creating a file if none exists, and more. The original
program was developed with the sole purpose of saving dictionaries to files, and
was not released to the public.
"""


# TODO: create a rename function

class PYNDatabase:
    def __init__(self, file, autosave=False):
        if file.__class__ is dict:
            self.file = None
            self.fileObj = file
        else:
            if os.path.exists(file):
                self.file = file
            else:
                t = open(file, 'a+')
                t.close()
            with open(file, 'r') as temp_file_obj:
                try:
                    self.fileObj = eval(temp_file_obj.read())
                except SyntaxError:
                    self.fileObj = {}

        self.val = self.fileObj
        self.autosave = autosave  # Is checked by set() and create() which call universal.save() if True
        self.universal = self.Universal(self.save, self.autosave, self.Node)

        for key in self.fileObj.keys():
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
            if any(char not in universal.VALID_CHARS for char in list(name)):  # Makes sure all names contain valid characters
                raise self.universal.Error.InvalidName(f'{name} cannot contain special characters and/or numbers (excluding _ and -).')

            elif name in self.universal.CORE_NAMES:  # Makes sure the name does not conflict with the Core Names
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

        def get(self, name):
            return getattr(self, name)

        def delete(self, name):
            delattr(self, name)  # Removes the Node object
            del self.val[name]  # Removes the key from the represented dictionary

        def create(self, name, val={}):
            if hasattr(self, name):
                raise self.universal.Error.AlreadyExists(name)

            elif name in self.universal.CORE_NAMES:
                raise self.universal.Error.CoreName(f'Cannot assign name: {name} is a Core Name.')

            elif type(self.val) is not dict:
                raise TypeError(f''
                                f'{self.name} is {str(type(self.val))}, and must be dict. Consider using the '
                                f'transform method to resolve this issue.')

            elif any(char not in universal.VALID_CHARS for char in list(name)):  # Makes sure all names contain valid characters
                raise self.universal.Error.InvalidName(f'{name} cannot contain special characters and/or numbers (excluding _ and -).')
            else:
                setattr(self, name, self.universal.Node(name, val, self.universal))
                self.val[name] = val
                if self.universal.autosave:
                    self.universal.save()

        def transform(self, name, new_name):
            self.set(name, {new_name: self.get(name).val})

    # ----- Universal Resources (accessible by Nodes) -----

    class Universal:

        VALID_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-'

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
                'name'
            ]
            self.MASTER_NAMES = [
                'Universal',
                'Node',
                'save',
                'autosave',
                'file',
                'fileObj'
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

    # ----- Master functions -----

    def get(self, name):
        return getattr(self, name)

    def set(self, name, data, create_if_not_exist=True):
        if any(char not in universal.VALID_CHARS for char in list(name)):  # Makes sure all names contain valid characters
            raise self.universal.Error.InvalidName(f'{name} cannot contain special characters and/or numbers (excluding _ and -).')

        elif name in self.universal.CORE_NAMES + self.universal.MASTER_NAMES:  # If the name is a Core Name
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

    def create(self, name, val={}):
        if hasattr(self, name):
            raise self.universal.Error.AlreadyExists(name)

        # The dict type check is not necessary for a master function, as self.fileObj will always be a dict.

        elif any(char not in universal.VALID_CHARS for char in list(name)):  # Makes sure all names contain valid characters
            raise self.universal.Error.InvalidName(f'{name} cannot contain special characters and/or numbers (excluding _ and -).')

        elif name in self.universal.CORE_NAMES:
            raise self.universal.Error.CoreName(f'Cannot assign name: {name} is a Core Name.')

        else:
            setattr(self, name, self.Node(name, val, self))
            self.fileObj[name] = val
            if self.autosave:
                self.save()

    def delete(self, name):
        delattr(self, name)  # Removes the Node object
        del self.fileObj[name]  # Removes the key from the main dictionary

    def transform(self, name, new_name):
        self.set(name, {new_name: self.get(name).val})

    def save(self, file=None):
        if file:
            with open(file, 'w') as temp_file_obj:
                temp_file_obj.write(str(self.fileObj))

        elif self.file:
            with open(self.file, 'w') as temp_file_obj:
                temp_file_obj.write(str(self.fileObj))
        else:
            raise self.universal.Error.FileError(
                'Cannot open file: Class was initiated with dictionary object rather than filename. '
                'Set the file paramater to save to a file different than the one this class was '
                'initiated with.')
