@RD /S /Q "dist"
python version_number_increase.py
python -m build
python -m twine upload dist/*
pause
