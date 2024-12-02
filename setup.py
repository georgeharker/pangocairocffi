import os
import sys

from setuptools import setup


if sys.version_info.major < 3:
    raise RuntimeError(
        'pangocairocffi does not support Python 2.x. Please use Python 3.'
    )

if ('PANGOCAIROCFFI_API_MODE' in os.environ and
        int(os.environ['PANGOCAIROCFFI_API_MODE']) == 1):
    setup(
        name='pangocairocffi',
        # when cairocffi, pangocffi are updated, bump to include API mode
        install_requires=['cffi >= 1.1.0', 'cairocffi >= 1.7.1', 'pangocffi >= 0.13.0'],
        setup_requires=['cffi >= 1.1.0', 'cairocffi >= 1.7.1', 'pangocffi >= 0.13.0'],
        cffi_modules=['pangocairocffi/ffi_build.py:ffi'],
        packages=['pangocairocffi']
    )
else:
    setup()
