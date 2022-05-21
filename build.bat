@echo off
pip uninstall cpir -y
python setup.py bdist_wheel
cd dist/
pip install MCF-1.0.0-py3-none-any.whl
cd ..
del /S /Q build
del /S /Q MCF.egg-info