# TikZ to SVG Conversion

## Introduction

This part of the repository contains a set of tools to automate the conversion of TikZ LaTeX graphs into Scalable Vector Graphics (SVG) format. The tools are designed for users on Windows and Linux operating systems. A Windows Batch file, a Linux Shell script, and a sample LaTeX file that contains a TikZ graph are included.

## Contents

1. `latex-to-svg.bat`: A Windows Batch file for automating the conversion process on Windows OS.
2. `latex-to-svg.sh`: A Shell script for automating the conversion process on Linux OS.
3. `chart.tex`: A sample LaTeX file containing a TikZ graph.

## Prerequisites

To use these tools, ensure that you have the following installed:

- A TeX distribution (such as MiKTeX or TeX Live) that includes `lualatex`.
- `dvisvgm` tool for converting DVI files to SVG format.

Ensure that the `lualatex` and `dvisvgm` commands are available in your system's PATH.

## Usage

### Windows

1. Place the `latex-to-svg.bat` and `example.tex` in the same directory.
2. Double-click on the `latex-to-svg.bat` file to run it.
3. The script will compile the LaTeX file to DVI and then convert it to SVG format.
4. All output files except for `example.dvi` and `example.svg` will be deleted.

### Linux

1. Place the `latex-to-svg.sh` and `chart.tex` in the same directory.
2. Open a terminal and navigate to the directory containing the files.
3. Make the script executable by running `chmod +x latex-to-svg.sh`.
4. Run the script by typing `./latex-to-svg.sh`.
5. The script will compile the LaTeX file to DVI and then convert it to SVG format.
6. All output files except for `chart.dvi` and `chart.svg` will be deleted.
