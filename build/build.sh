echo 'Building standalone Logria...'
python -m nuitka --plugin-enable=pylint-warnings --follow-imports --standalone --python-flag=no_site,no_docstrings --output-dir=build/src/standalone logria/__main__.py
echo 'Compressing standalone Logria build...'
zip -r build/logria-standalone.zip build/src/standalone/__main__.dist > /dev/null
echo 'Compressing standalone Logria source...'
zip -r build/src/standalone.zip build/src/standalone > /dev/null

echo 'Building dependant Logria...'
python -m nuitka --plugin-enable=pylint-warnings --follow-imports --output-dir=build/src/dependant logria/__main__.py
echo 'Copying dependant Logria binary...'
cp build/src/dependant/__main__.bin build/logria-dependant
echo 'Compressing dependant Logria...'
zip -r build/src/dependant.zip build/src/dependant > /dev/null
echo 'Done!'
