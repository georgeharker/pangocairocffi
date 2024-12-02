"""
    pangocairocffi.ffi_build
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Build the cffi bindings
"""

import os
import sys
from pathlib import Path
from warnings import warn


from cffi import FFI

sys.path.append(str(Path(__file__).parent))


api_mode = False
if ('PANGOCAIROCFFI_API_MODE' in os.environ and
        int(os.environ['PANGOCAIROCFFI_API_MODE']) == 1):
    # Allow explicit disable of api_mode
    api_mode = True

# Create an empty _generated folder if needed
if not api_mode:
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

xcffib_available = False
try:
    from xcffib.ffi_build import ffi as xcb_ffi
except ImportError:
    warn("xcfiib not available")
else:
    xcffib_available = True

pangocffi_api_mode = False
try:
    from pangocffi import ffi_build as ffi_pango
    ffi.include(ffi_pango.ffi)
    pangocffi_api_mode = True
except ImportError:
    from pangocffi import ffi as ffi_pango
    ffi.include(ffi_pango)
    if api_mode:
        warn("pangocffi is not available in API mode, disabling API mode")
        api_mode = False

cairocffi_api_mode = False
try:
    from cairocffi.ffi_build import ffi as ffi_cairo
    ffi.include(ffi_cairo)
    cairocffi_api_mode = True
except ImportError:
    ffi.cdef(c_definitions_cairo)
    if api_mode:
        warn("cairocffi is not available in API mode, disabling API mode")
        api_mode = False


ffi.cdef(c_definitions_pangocairo)

if api_mode:
    ffi.set_source_pkgconfig(
        '_pangocairocffi',
        ['pangocairo', 'pango', 'glib-2.0'],
        r"""
        #include "glib.h"
        #include "glib-object.h"
        #include "pango/pango.h"
        #include "pango/pangocairo.h"
        #include "cairo-pdf.h"
        #include "cairo-svg.h"
        #include "cairo-ps.h"
        #if defined(_WIN64) || defined(_WIN32)
        #include "cairo-win32.h"
        #endif
        """ +
        (r"""
        #include "xcb/xcb.h"
        #include "xcb/xproto.h"
        #include "xcb/xcbext.h"
        #include "xcb/render.h"
        #include "cairo-xcb.h"
        """ if xcffib_available else "") +
        r"""
        /* Deal with some newer definitions for compatibility */
        #if CAIRO_VERSION < 11702
        #define CAIRO_FORMAT_RGBA128F 7
        #define CAIRO_FORMAT_RGB96F 6
        #endif
        #if CAIRO_VERSION < 11800
        #include <stdio.h>
        #include <stdbool.h>
        void cairo_set_hairline(cairo_t*, cairo_bool_t);
        cairo_bool_t cairo_get_hairline(cairo_t*);
        void cairo_set_hairline(cairo_t*, cairo_bool_t) {
            fprintf(stderr, "Unimplemented!!\n");
        }
        cairo_bool_t cairo_get_hairline(cairo_t*) {
            fprintf(stderr, "Unimplemented!!\n");
            return false;
        }
        #endif
        """,
        sources=[]
    )

else:
    ffi.set_source('pangocairocffi._generated.ffi', None)

if __name__ == '__main__':
    ffi.compile()
