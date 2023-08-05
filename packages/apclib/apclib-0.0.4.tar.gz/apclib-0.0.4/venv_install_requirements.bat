call venv_activate.bat
pip install --upgrade pip
pip install -r venv_requirements.txt
pip freeze > venv_installed_packages.txt
call venv_deactivate.bat