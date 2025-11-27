# MAS417 Project

## Intro
This program fetches Simple 3D Building (S3DB) data for a desired area from OpenStreetMap through Overpass API.
Meshes are created from this data, and saved as an STL ready for 3D printing.

## How to run:
install dependencies:
```sh
pip install -r requirements.txt
```
run program:
```sh
python main.py
```
the program is interactive, and lists options when promping for input.

STL file will be saved to output/mesh.stl
