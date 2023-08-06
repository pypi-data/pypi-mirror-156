import setuptools

with open("pypi.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='pipse',
    version='0.0.1',
    author='Junpu Fan',
    author_email='junpufan@gmail.com ',
    description='pip, secured. [temporary placeholder, code is coming soon...]',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/junpuf/pips',
    license='Apache License 2.0',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)