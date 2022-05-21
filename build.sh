#!/bin/bash
pip38 uninstall MCF -y
python38 setup.py bdist_wheel
# shellcheck disable=SC2164
cd dist/
pip38 install MCF-1.0.0-py3-none-any.whl
# shellcheck disable=SC2103
cd ..
rm -r dist/
rm -r MCF.egg-info
rm -r build