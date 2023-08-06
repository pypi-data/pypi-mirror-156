#!/bin/bash
echo Have you updated version?
read
#./setup.py sdist --formats=gztar upload
#echo "Generating docs"
#./setup.py build_sphinx
#echo "Uploading docs to pypi"
#./setup.py upload_docs --upload-dir doc/_build/html/


echo "Building..."
python -m build

echo "Uploading..."
twine upload dist/*


echo "Done"
