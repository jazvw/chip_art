# Intro
This tool takes a bitmap, and outputs a GDS and LEF file that can be used in an sky130 / OpenLANE flow. Furthermore, the necessary files are included that allow this to be directly used as a submission for the (excellent) https://www.zerotoasiccourse.com/.

# Installation
You'll need to have the Magic VLSI tool installed and configured properly.

# Running
`make clean && make GDS_WIDTH=50 IMAGE=chip_art.png`

The GDS_WIDTH specifies how wide (in um) you want the image to render in the GDS. 

# Output
It will create GDS/LEF files in `gds/` folder. 

# Hacking
Check the `chip_art.py` script for a bunch of stuff that's hardcoded and only tested on sky130 / OpenLANE.

# Like?
If you end up using this, send me a tweet at @jzvw and show off your chip art!
