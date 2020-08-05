echo 'Building standalone Logria...'
python -m nuitka --plugin-enable=pylint-warnings --follow-imports --standalone --python-flag=no_site,no_docstrings --output-dir=build/standalone logria/__main__.py
zip build/logria-standalone.zip build/standalone/__main__.dist/
echo 'Building dependant Logria...'
python -m nuitka --plugin-enable=pylint-warnings --follow-imports --output-dir=build/dependant logria/__main__.py
cp build/dependant/__main__.bin build/logria-dependant
echo 'Done!'
