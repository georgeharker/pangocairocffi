"""
    pangocairocffi.ffi_build
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Build the cffi bindings
"""

import os
import sys
from pathlib import Path

from cffi import FFI


sys.path.append(str(Path(__file__).parent))

# Create an empty _generated folder if needed
(Path(__file__).parent / '_generated').mkdir(exist_ok=True)

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

if ('PANGOCFFI_API_MODE' in os.environ and
        int(os.environ['PANGOCFFI_API_MODE']) == 1):
    from pangocffi.ffi_build import ffi as ffi_pango
    ffi.include(ffi_pango)
else:
    from pangocffi import ffi as ffi_pango
    ffi.include(ffi_pango)

if ('CAIROCFFI_API_MODE' in os.environ and
        int(os.environ['CAIROCFFI_API_MODE']) == 1):
    from cairocffi.ffi import ffi as ffi_cairo
    ffi.include(ffi_cairo)
else:
    ffi.cdef(c_definitions_cairo)

ffi.cdef(c_definitions_pangocairo)

if ('PANGOCAIROCFFI_API_MODE' in os.environ and
        int(os.environ['PANGOCAIROCFFI_API_MODE']) == 1):
    ffi.set_source_pkgconfig(
        '_pangocairocffi',
        ['pangocairo', 'pango', 'glib-2.0'],
        """
        #include "glib.h"
        #include "glib-object.h"
        #include "pango/pango.h"
        #include "pango/pangocairo.h"
        #include "cairo-pdf.h"
        #include "cairo-svg.h"
        #include "cairo-ps.h"
        #include "cairo-quartz.h"

        #include "xcb/xproto.h"
        #include "xcb/xcb.h"
        #include "xcb/xcbext.h"
        #include "xcb/render.h"
        #include "cairo-xcb.h"
        """,
        sources=[]
    )

else:
    ffi.set_source('pangocairocffi._generated.ffi', None)

if __name__ == '__main__':
    ffi.compile()
