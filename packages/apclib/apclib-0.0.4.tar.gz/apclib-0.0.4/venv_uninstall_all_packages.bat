call venv_activate.bat
pip freeze > venv_installed_packages.txt
pip uninstall -r venv_installed_packages.txt -y
pip freeze > venv_installed_packages.txt
call venv_deactivate.bat