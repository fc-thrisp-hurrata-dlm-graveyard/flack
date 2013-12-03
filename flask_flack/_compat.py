import sys

PY2 = sys.version_info[0] == 2

if PY2:
    import urlparse as url_parse_lib
else:
    import urllib.parse as url_parse_lib
