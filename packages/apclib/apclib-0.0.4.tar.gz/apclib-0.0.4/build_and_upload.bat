rmdir /s "dist" /Q
call venv_activate.bat
py -m pip install --upgrade pip
py -m pip install --upgrade build
py -m pip install --upgrade twine
py -m build
py -m twine upload dist/*

rem python setup.py sdist
rem pip install --upgrade twine
rem twine upload dist/*