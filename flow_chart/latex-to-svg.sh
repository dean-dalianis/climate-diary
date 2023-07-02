#!/bin/bash

# Set the filename
filename="chart"

# Step 1: Compile LaTeX file to DVI using lualatex
lualatex --output-format=dvi "$filename.tex"

# Check if lualatex succeeded
if [ $? -ne 0 ]; then
    echo "lualatex failed to compile the file."
    read -p "Press enter to exit"
    exit 1
fi

# Step 2: Convert DVI to SVG using dvisvgm
dvisvgm --no-fonts "$filename.dvi"
# For retaining fonts, use the command below and comment-out the above
# dvisvgm --font-format=woff --exact "$filename.dvi"

# Check if dvisvgm succeeded
if [ $? -ne 0 ]; then
    echo "dvisvgm failed to convert the DVI to SVG."
    read -p "Press enter to exit"
    exit 1
fi

echo "Conversion to SVG completed successfully. Output file: $filename.svg"

# Delete all output files except for .dvi and .svg
find . -maxdepth 1 -type f \( -name "$filename.*" ! -name "$filename.dvi" ! -name "$filename.svg" ! -name "$filename.tex" \) -exec rm -f {} +

read -p "Press enter to exit"
