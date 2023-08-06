#!/usr/bin/python3
import struct
from sys import platform as _sys_info
try:
    size = struct.calcsize('P')
except struct.error:# Older installations can only query longs
    size = struct.calcsize('l')
if _sys_info.__contains__("win32") or _sys_info.__contains__("Win32"):
    from sys import winver as _version_info
    print(_sys_info)
    print("python version :"+_version_info)
    if size == 8: # 64bits system
        if _version_info.__contains__("3.6"):
            from ..libs.python36.x64 import mdc_gateway_client as mdc_gateway_client
        elif _version_info.__contains__("3.7"):
            from ..libs.python37.x64 import mdc_gateway_client as mdc_gateway_client
        elif _version_info.__contains__("3.8"):
            from ..libs.python38.x64 import mdc_gateway_client as mdc_gateway_client
        elif _version_info.__contains__("3.9"):
            from ..libs.python39.x64 import mdc_gateway_client as mdc_gateway_client
        elif _version_info.__contains__("3.10"):
            from ..libs.python310.x64 import mdc_gateway_client as mdc_gateway_client
        elif _version_info.__contains__("3.4"):
            from ..libs.python34.x64 import mdc_gateway_client as mdc_gateway_client
        else:
            raise RuntimeError('Python 3.7 or Python 3.6 required')
    elif size == 4: # 32bits system
        if _version_info.__contains__("3.6"):
            from ..libs.python36.x86 import mdc_gateway_client as mdc_gateway_client
        elif _version_info.__contains__("3.7"):
            from ..libs.python37.x86 import mdc_gateway_client as mdc_gateway_client
        elif _version_info.__contains__("3.9"):
            from ..libs.python39.x86 import mdc_gateway_client as mdc_gateway_client
        elif _version_info.__contains__("3.10"):
            from ..libs.python310.x86 import mdc_gateway_client as mdc_gateway_client
        elif _version_info.__contains__("3.4"):
            from ..libs.python34.x86 import mdc_gateway_client as mdc_gateway_client
        else:
            raise RuntimeError('Python 3.7 or Python 3.6 required')
    else:
        raise RuntimeError('Python 3.7 or Python 3.6 required')
else:
    from com.libs.linux import mdc_gateway_client as mdc_gateway_client