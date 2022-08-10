# RPDR Converter

## Creating a release

In order to create a release, please first update the version number in `rpdr_converter/_version.py` in accordance with [semantic versioning](https://semver.org/). When that is merged to main, create a tag with the appropriate version number and push it to the remote. Finally, create a release on GitHub using that version tag. An action should run on GitHub creating executable builds of the program.
