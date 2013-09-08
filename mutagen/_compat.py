# Copyright 2013 Christoph Reiter
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of version 2 of the GNU General Public License as
# published by the Free Software Foundation.

import sys


PY2 = sys.version_info[0] == 2
PY3 = not PY2

if PY2:
    from StringIO import StringIO
    BytesIO = StringIO
    from cStringIO import StringIO as cBytesIO

    long_ = long
    integer_types = (int, long)

    iteritems = lambda d: d.iteritems()

    exec("def reraise(tp, value, tb):\n raise tp, value, tb")
elif PY3:
    from io import StringIO
    StringIO = StringIO
    from io import BytesIO
    cBytesIO = BytesIO

    long_ = int
    integer_types = (int,)

    iteritems = lambda d: iter(d.items())

    def reraise(tp, value, tb):
        raise value.with_traceback(tb)
