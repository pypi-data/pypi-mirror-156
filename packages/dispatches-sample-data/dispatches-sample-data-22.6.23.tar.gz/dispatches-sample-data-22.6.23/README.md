# dispatches-sample-data

Various datasets for use in examples of the [DISPATCHES project](https//github.com/gmlc-dispatches/dispatches), distributed as a Python package for ease of access.

## Datasets

- `dispatches_sample_data.rts_gmlc`: A subset of the data available at https://github.com/GridMod/RTS-GMLC

## Usage

To install the package:

```sh
pip install dispatches-sample-data
pip install "dispatches-sample-data @ https://github.com/gmlc-dispatches/sample-data"
```

Importing and using the package in Python code:

```py
from dispatches_sample_data import rts_gmlc

print(rts_gmlc.path)  # .path is a pathlib.Path object with the absolute path to the directory containing the data

for csv_path in sorted(rts_gmlc.path.rglob("*.csv")):
    print(csv_path)
```
