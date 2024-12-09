"""
    pangocairocffi.ffi_build
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Build the cffi bindings
"""

import sys
from setuptools.errors import CCompilerError, ExecError, PlatformError
from pathlib import Path
from warnings import warn


from cffi import FFI
from cffi.error import VerificationError


sys.path.append(str(Path(__file__).parent))


def ffi_for_mode(mode):
    # Read the CFFI definitions
    c_definitions_cairo_file = open(
        str(Path(__file__).parent / 'c_definitions_cairo.txt'),
        'r'
    )
    c_definitions_cairo = c_definitions_cairo_file.read()
    c_definitions_pangocairo_file = open(
        str(Path(__file__).parent / 'c_definitions_pangocairo.txt'),
        'r'
    )
    c_definitions_pangocairo = c_definitions_pangocairo_file.read()

    # cffi definitions, in the order outlined in:
    ffi = FFI()

    from pangocffi.ffi_build import ffi_for_mode as pango_ffi_for_mode
    pango_ffi = pango_ffi_for_mode(mode)
    ffi.include(pango_ffi)

    from cairocffi.ffi_build import ffi_for_mode as cairo_ffi_for_mode
    from cairocffi.ffi_build import c_source_cairo, c_source_cairo_compat
    cairo_ffi = cairo_ffi_for_mode(mode)
    ffi.include(cairo_ffi)

    ffi.cdef(c_definitions_pangocairo)

    if mode == "api":
        ffi.set_source_pkgconfig(
            '_pangocairocffi',
            ['pangocairo', 'pango', 'glib-2.0'],
            c_source_cairo +
            r"""
            #include "glib.h"
            #include "glib-object.h"
            #include "pango/pango.h"
            #include "pango/pangocairo.h"
            """ + c_source_cairo_compat,
            sources=[]
        )

    else:
        ffi.set_source('_pangocairocffi', None)
    return ffi


def build_ffi():
    """
    This will be called from setup() to return an FFI
    which it will compile - work out here which type is
    possible and return it.
    """
    try:
        ffi_api = ffi_for_mode("api")
        ffi_api.compile(verbose=True)
        return ffi_api
    except (CCompilerError, ExecError, PlatformError,
            VerificationError) as e:
        warn("Falling back to precompiled python mode: {}".format(str(e)))

        ffi_abi = ffi_for_mode("abi")
        ffi_abi.compile(verbose=True)
        return ffi_abi


if __name__ == '__main__':
    build_ffi()
