[![PyPI version pyndb](https://raw.githubusercontent.com/jvadair/pyndb/main/package/pypi_badge.svg)](https://pypi.org/project/pyndb/)
# pyndb
 PYN DB, originally named DataManager, is a method for easily saving data to a file, while also providing syntactic convenience. It utilizes a Node structure which allows for easily retrieving nested objects. All data is stored to file as nested dictionaries, and wrapped inside of a custom Node object. It  provides additional capabilities such as autosave, saving a dictionary to file, creating a file if none exists, and more. The original program was developed with  the sole purpose of saving dictionaries to files, and was not released to the public.

## Install
To install, you can either install via pip:  
`pip install pyndb`  
Or, you can download the package folder and run:  
`python -m pip install dist/*.whl`  

## How values are represented
All keys in a dictionary managed by a PYNDatabase object will be represented as Node objects. Each Node object scans the dictionary it represents, and creates new Nodes for each key. This process repeats recursively. A Node object can also represent any other class, but you must then use the `transform` method - or replace the value with a dictionary - in order to create a subnode.

## Creating a new database
To create a new database, first import the PYNDatabase object. Once you have done this, you can initialize it and then store it in a variable. A PYNDatabase object can be initialized with a filename (string), or a dictionary. You can also set the autosave flag. These values CAN be changed later, by changing `PYNDatabase.<file | autosave>`.

## Saving
If a PYNDatabase object is initialized with a dictionary, it will update the original dictionary object as changes are made. Otherwise, you must call `PYNDatabase.save()` (unless autosave is set to `True`). The `save` method also has a `file` flag, which allows for easily saving to another file.

## Retrieving values
Since values are stored as Node objects, object retrieval will look something like this:  
`PYNDatabase.Node.Node.val`  
  
`val` is a variable which contains the value of the Node, and is linked to the original dictionary object.  
  
To retrieve a dynamic object, you can use the `get` method like this:  
`PYNDatabase.Node.get('name_of_node').Node.val`  
  
This way, you can avoid writing code like this:  
`eval(f'PYNDatabase.Node.{name_of_node}.Node.val')`  

## Changing values
To change the value of a Node, you must use the `set` method from the parent Node. The set method uses the following arguments:  
`set(name, val, create_if_not_exist=True)`  
  
Sample usage would look something like this:  
`PYNDatabase.Node.set('name_of_node', new_value)`  
  
`set` will create new values if they don't exist, but this can be changed by setting `create_if_not_exist` to False. This way it will just raise a NameError.  
  
## Creating new values
To create a new subnode, you can use the `create` method. It uses the following arguments:  
`create(name, val=None)`  
As you can see, the value is set to None by default, but can easily be changed by modifying the `val` flag, or using the `set` method.  
If the name given is already in use, an `AlreadyExists` Exception will be raised.  
  
## Deleting values
To delete a Node, you can use the `delete` method. The only argument it takes is the `name` parameter.  
  
## The transform method
The `transform` method places the existing value of a Node into a dictionary under a user-defined key. The arguments for this method are shown below:  
`transform(name, new_name)`  
  
This method can be easily understood with the aid of a before and after diagram:  
### Before
> None
### After
> {'new_name': None}
