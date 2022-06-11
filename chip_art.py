#!/usr/bin/python3

# SPDX-FileCopyrightText: 2022 Jasper van Woudenberg
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0




# This script converts an input bitmap into a Magic file that can be converted to GDS
# It adds a ground and a power wire in order to keep openlane / drc / lvs etc happy
# On 2022-06 has only had minimal testing

from PIL import Image
import numpy as np
from itertools import groupby
import time
import sys

BACKGROUND = 0 # metal layer to consider 'background', i.e. no metal
MIN_METAL = 0 # "metal0" means no pixel is drawn
MAX_METAL = 4 # max metal layer

MAGIC_LAMBDA = 0.01 # this is size of each unit in Magic coordinates in um
MIN_PIXEL_SIZE = 0.2 # Safety measure, make sure pixels are at least this size
MIN_HEIGHT = 220 # Minimum height in um so PDN stays happy

PIN_WIDTH = 1.75 # in um
PIN_METAL = 4 # Metal on which to draw the pins
PIN_MARGIN = 5 # in um, margin between picture and pins

def wire2str(wire):
    """ Convert a wire 4-tuple to Magic coordinates as string """
    scaled = np.int64(np.asarray(wire,dtype=np.int64) / MAGIC_LAMBDA) # Scale rect
    return " ".join((str(x) for x in scaled))

# Hacky command line parse
try:
    _, image_in, magic_out, gds_width = sys.argv
    gds_width = float(gds_width)
except:
    print("./chip_art.py <image_in> <magic_out> <gds_width_in_um>")
    sys.exit(-1)

# Read input image
image = Image.open(image_in).convert('L').transpose(Image.FLIP_TOP_BOTTOM) # Load and convert to grayscale, flip to get right orientation in GDS
scale = gds_width / image.size[0] # Pixel size in um
print(f"Image {image_in} has size {image.size}, output GDS is {gds_width:.2f}um wide, giving us a GDS pixel size of {scale:.2f}um")
if 1 * scale < MIN_PIXEL_SIZE:
    print(f"Pixel size is smaller than the minimum {MIN_PIXEL_SIZE}um. Please decrease width of input image to below {gds_width / MIN_PIXEL_SIZE:.0f} pixels or increase gds_width_in_um to at least {image.size[0] * MIN_PIXEL_SIZE:.2f}um")
    sys.exit(-2)

# Normalize pixels values to metal layers
pixels = np.asarray(image, dtype=np.uint64)
pixels = (pixels - pixels.min()) * (MAX_METAL-MIN_METAL+0.49) / (pixels.max() - pixels.min()) + MIN_METAL
pixels = np.uint8(pixels)

# init wire arrays. Each metal will have a set of horizontal wires representing image pixels on that metal layer.
wires = dict()
for metal in range(MIN_METAL, MAX_METAL+1):
    wires[metal] = []

# Loop over pixels in image, creating horizontal wire segments
for y in range(image.size[1]):
    line = pixels[y,:]
    rle = [(k, sum(1 for i in g)) for k,g in groupby(line)] # Run length encoding;  [2,2,2,1,1,2,2,3,3,3,3] becomes [(2, 3), (1, 2), (2, 2), (3, 4)]
    cur_x = 0
    for (metal, length) in rle:
        # If not background, add a strip of wire to correct metal layer
        if metal != BACKGROUND:
            wire = (cur_x * scale, y * scale, (cur_x+length) * scale, (y+1) * scale)
            wires[metal].append(wire)
        cur_x += length

# Create power and ground wires
image_width, image_height = (image.size)
image_width *= scale # Make in um
image_height *= scale 

# Vertical wires
wire_height = max(image_height, MIN_HEIGHT)
if image_height < MIN_HEIGHT:
    print(f"Note: extending image height from {image.size[1]} to {wire_height / scale}")
y_offset = wire_height / 2 - (image_height / 2)
VGND_miny = -y_offset
VGND_maxy = wire_height - y_offset
VGND_minx = -PIN_MARGIN - PIN_WIDTH
VGND_maxx = -PIN_MARGIN

VPWR_miny = -y_offset
VPWR_maxy = wire_height - y_offset
VPWR_minx = image_width + PIN_MARGIN
VPWR_maxx = image_width + PIN_MARGIN + PIN_WIDTH

# Add to our wires
gnd_wire = (VGND_minx, VGND_miny, VGND_maxx, VGND_maxy)
wires[PIN_METAL].append(gnd_wire)
pwr_wire = (VPWR_minx, VPWR_miny, VPWR_maxx, VPWR_maxy)
wires[PIN_METAL].append(pwr_wire)

# Write magic 
with open(magic_out, "w") as out:
    out.write("magic\n")
    out.write("tech sky130A\n")
    out.write(f"timestamp {int(time.time())}\n")

    # Loop over wires and print out magic rects
    for metal in range(MIN_METAL, MAX_METAL+1):
        if len(wires[metal]) > 0:
            out.write(f"<< metal{metal} >>\n")
            print(f"Writing {len(wires[metal])} wires to metal {metal}")
        for wire in wires[metal]:
            wire_str = wire2str(wire)
            out.write(f"rect {wire_str}\n")

    # Create power and ground lines to satisfy some power routing later
    out.write(f"""<< labels >>
rlabel metal{PIN_METAL} s {wire2str(pwr_wire)} 6 vccd1
port 1 nsew power input
rlabel metal{PIN_METAL} s {wire2str(gnd_wire)} 6 vssd1
port 2 nsew ground input
""")
    # Done
    out.write("<< end >>\n")
