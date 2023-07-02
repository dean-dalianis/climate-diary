@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

REM Set the filename
set "filename=chart"

REM Step 1: Compile LaTeX file to DVI using lualatex
lualatex --output-format=dvi "%filename%.tex"

REM Check if lualatex succeeded
if errorlevel 1 (
    echo lualatex failed to compile the file.
    pause
    exit /b 1
)

REM Step 2: Convert DVI to SVG using dvisvgm
REM Check if dvisvgm is installed
where /q dvisvgm
if errorlevel 1 (
    echo dvisvgm is not installed. Please install a TeX distribution like MiKTeX or TeX Live and rerun the script.
    pause
    exit /b 1
)

REM Convert DVI to SVG
dvisvgm --no-fonts "%filename%.dvi"
REM  For retaining fonts use the command bellow and comment-out the above
REM  dvisvgm --font-format=woff --exact "%filename%.dvi"

REM Check if dvisvgm succeeded
if errorlevel 1 (
    echo dvisvgm failed to convert the DVI to SVG.
    pause
    exit /b 1
)

echo Conversion to SVG completed successfully. Output file: %filename%.svg

REM Delete all output files except for .dvi and .svg
for %%i in (%filename%*.*) do (
    if not "%%i"=="%filename%.dvi" (
        if not "%%i"=="%filename%.svg" (
           if not "%%i"=="%filename%.tex" (		
              del "%%i"
   	   )
        )
    )
)

pause
