# How to do a release

Releases are managed using `minchin.releaser`.

To cut a release, commit your desired changed, install the development version
of the package into a virtual environment (e.g. `pip install .[dev]`), and then
run the releaser (e.g. `invoke make-release`).
