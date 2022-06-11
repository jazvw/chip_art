# Intro
This tool takes a bitmap, and outputs a GDS and LEF file that can be used in an sky130 / OpenLANE flow. Furthermore, the necessary files are included that allow this to be directly used as a submission for the (excellent) https://www.zerotoasiccourse.com/.

Note: Since we can only use metals 1-4, metal 5 will still have PDN wires going over our art. If someone can solve that, I'm all ears.
Note2: Depending on your bitmap, you can still cause DRC issues.

# Installation
You'll need to have the Magic VLSI tool installed and configured properly.

# Running
`make clean && make GDS_WIDTH=50 IMAGE=chip_art.png`

The GDS_WIDTH specifies how wide (in um) you want the image to render in the GDS. 

# Output
It will create GDS/LEF files in `gds/` folder. 

# Hacking
Check the `chip_art.py` script for a bunch of stuff that's hardcoded and only tested on sky130 / OpenLANE.

# How does it work?
It maps supported bitmaps to gray scale images, and the pixel values get then mapped to metal layers in the GDS. The Python script outputs a Magic file, and the Makefile uses Magic to generate GDS and LEF. 

In order to satisfy DRC and LVS, the GDS also contains a power and ground rail!

# Like?
If you end up using this, send me a tweet at @jzvw and show off your chip art!
