# SPDX-FileCopyrightText: 2021 Uri Shaked, Jasper van Woudenberg
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

TARGETS = gds/chip_art.gds gds/chip_art.lef gds/chip_art.mag

# Input image
IMAGE ?= chip_art.png
# Output width in um
GDS_WIDTH ?= 50 

all: gds $(TARGETS)
clean: 
	rm -f $(TARGETS)

.PHONY: all clean

gds/chip_art.mag: $(IMAGE)
	./chip_art.py $^ $@ ${GDS_WIDTH} 

magic: gds/chip_art.mag
	magic -rcfile $(PDK_ROOT)/sky130A/libs.tech/magic/sky130A.magicrc $<

gds:
	mkdir gds

gds/chip_art.gds: gds/chip_art.mag
	echo "gds write \"$@\"" | magic -rcfile $(PDK_ROOT)/sky130A/libs.tech/magic/sky130A.magicrc -noconsole -dnull $<

gds/chip_art.lef: gds/chip_art.mag
	echo "lef write \"$@\"" | magic -rcfile $(PDK_ROOT)/sky130A/libs.tech/magic/sky130A.magicrc -noconsole -dnull $<
