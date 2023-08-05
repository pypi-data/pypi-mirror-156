@RD /S /Q "dist"
python version_number_increase.py
python3 -m build
python3 -m twine upload dist/*
pause
