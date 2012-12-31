#!/bin/bash
echo "!!!RUN THIS FROM THE ROOT eyearesee DIRECTORY!!!"
echo "(Don't cd src/, run it as ./src/compile.sh)"
echo

cd ./src

echo "Compiling source files..."
pypy -m compileall ./

echo "Adding to eyearebin.zip..."
zip -0 -r ../eyearebin.zip *

echo "Removing .pyc/.pyo files..."
find -name "*.py[c|o]" | xargs rm

cd ..

echo "Done."
