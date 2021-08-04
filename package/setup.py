import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(name="pyndb",
      version='3.0.3',
      packages=["pyndb"],
      author="jvadair",
      author_email="dev@jvadair.com",
      description="A way of saving data to a file with syntactic convenience",
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/jvadair/pyndb",
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ],
)
