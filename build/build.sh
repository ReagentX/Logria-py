echo 'Building standalone Logria...'
python -m nuitka --plugin-enable=pylint-warnings --follow-imports --standalone --python-flag=no_site,no_docstrings --output-dir=build/src/standalone logria/__main__.py
zip build/logria-standalone.zip build/src/standalone/__main__.dist/
zip build/src/standalone.zip build/src/standalone/
echo 'Building dependant Logria...'
python -m nuitka --plugin-enable=pylint-warnings --follow-imports --output-dir=build/src/dependant logria/__main__.py
cp build/src/dependant/__main__.bin build/logria-dependant
zip build/src/dependant.zip build/src/dependant/
echo 'Done!'
