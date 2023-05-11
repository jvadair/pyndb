[![PyPI version pyndb](https://raw.githubusercontent.com/jvadair/pyndb/main/github_assets/pypi_badge.svg)](https://pypi.org/project/pyndb/)
# What happened?
pyndb has been replaced by [pyntree](https://github.com/jvadair/pyntree)

The transtition was necessary in large part due to maintainability issues now resolved in pyntree. Additionally, pyntree was created from the ground up and built around Python's magic methods for easier and more syntactical usage.

pyntree has all of the features of pyndb - and more - and is largely backwards compatible (new encryption method and .val -> .\_val or ())

# pyndb
pyndb, short for Python Node Database, is a pacakge which makes it easy to save data to a file while also providing syntactic convenience. It utilizes a Node structure which allows for easily retrieving nested objects. All data is wrapped inside of a custom Node object, and stored to file as nested dictionaries. It  provides additional capabilities such as autosave, saving a dictionary to file, creating a file if none exists, and more. The original program was developed with  the sole purpose of saving dictionaries to files, and was not released to the public.

## Documentation
The documentation is available at <https://pen.jvadair.com/books/pyndb>
