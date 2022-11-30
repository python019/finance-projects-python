# -*- coding: utf-8 -*-
#
# Copyright (C) 2009 Akoha. Written by Simon Law <sfllaw@sfllaw.ca>
# 
# This software is licensed under the same terms and conditions as
# Python itself. See the file LICENSE.txt for more details.
#
# It is based on Python's PC/_winreg.c.
#
# cygwinreg/w32api.py
#
# This module provides hooks into the Windows libraries for manipulating
# the registry.

import exceptions
from locale import getpreferredencoding
import re
from struct import pack, unpack_from

from cygwinreg.constants import *

from ctypes import (addressof, byref, cast, pointer, POINTER, sizeof, Structure,
                    create_string_buffer,
                    c_char_p, c_long, c_ulong, c_ushort, c_void_p, c_wchar_p)

PCVOID = c_void_p
WORD = c_ushort
DWORD = c_ulong
PDWORD = POINTER(DWORD)
LPDWORD = PDWORD
LONG = c_long
PLONG = POINTER(LONG)
PBYTE = c_char_p
LPBYTE = PBYTE
LPSTR = c_char_p
LPWSTR = c_wchar_p
LPCWSTR = LPWSTR
HANDLE = c_ulong # in the header files: void *
HKEY = HANDLE
PHKEY = POINTER(HKEY)
HLOCAL = c_void_p
REGSAM = c_ulong

class FILETIME(Structure):
    _fields_ = [("low", DWORD),
                ("high", DWORD)]
PFILETIME = POINTER(FILETIME)

from ctypes import cdll

# WINBASEAPI DWORD WINAPI FormatMessageW(DWORD,PCVOID,DWORD,DWORD,LPWSTR,DWORD,
#                                        va_list*)
FormatMessageW = cdll.kernel32.FormatMessageW
FormatMessageW.restype = DWORD
FormatMessageW.argtypes = [DWORD, PCVOID, DWORD, DWORD, PCVOID, DWORD,
                           c_void_p]

# WINBASEAPI DWORD WINAPI GetLastError(void);
GetLastError = cdll.kernel32.GetLastError
GetLastError.restype = DWORD
GetLastError.argtypes = []

# WINBASEAPI HLOCAL WINAPI LocalFree(HLOCAL);
LocalFree = cdll.kernel32.LocalFree
LocalFree.restype = HLOCAL
LocalFree.argtypes = [HLOCAL]

# WINADVAPI LONG WINAPI RegCloseKey(HKEY);
RegCloseKey = cdll.advapi32.RegCloseKey
RegCloseKey.restype = LONG
RegCloseKey.argtypes = [HKEY]

# WINADVAPI LONG WINAPI RegConnectRegistryW(LPCWSTR,HKEY,PHKEY);
RegConnectRegistryW = cdll.advapi32.RegConnectRegistryW
RegConnectRegistryW.restype = LONG
RegConnectRegistryW.argtypes = [LPCWSTR, HKEY, PHKEY]

# WINADVAPI LONG WINAPI RegCreateKeyW(HKEY,LPCWSTR,PHKEY);
RegCreateKeyW = cdll.advapi32.RegCreateKeyW
RegCreateKeyW.restype = LONG
RegCreateKeyW.argtypes = [HKEY, LPCWSTR, PHKEY]

# WINADVAPI LONG WINAPI RegDeleteKeyW(HKEY,LPCWSTR);
RegDeleteKeyW = cdll.advapi32.RegDeleteKeyW
RegDeleteKeyW.restype = LONG
RegDeleteKeyW.argtypes = [HKEY, LPCWSTR]

# WINADVAPI LONG WINAPI RegDeleteValueW(HKEY,LPCWSTR);
RegDeleteValueW = cdll.advapi32.RegDeleteValueW
RegDeleteValueW.restype = LONG
RegDeleteValueW.argtypes = [HKEY, LPCWSTR]

# WINADVAPI LONG WINAPI RegEnumKeyExW(HKEY,DWORD,LPWSTR,PDWORD,PDWORD,
#                                     LPWSTR,PDWORD,PFILETIME);
RegEnumKeyExW = cdll.advapi32.RegEnumKeyExW
RegEnumKeyExW.restype = LONG
RegEnumKeyExW.argtypes = [HKEY, DWORD, LPWSTR, PDWORD, PDWORD, LPWSTR,
                          PDWORD, c_void_p]

# WINADVAPI LONG WINAPI RegQueryInfoKeyW(HKEY,LPWSTR,PDWORD,PDWORD,PDWORD,
#                                        PDWORD,PDWORD,PDWORD,PDWORD,PDWORD,
#                                        PDWORD,PFILETIME);
RegQueryInfoKeyW = cdll.advapi32.RegQueryInfoKeyW
RegQueryInfoKeyW.restype = LONG
RegQueryInfoKeyW.argtypes = [HKEY, LPWSTR, PDWORD, PDWORD, PDWORD, PDWORD,
                             PDWORD, PDWORD, PDWORD, PDWORD, PDWORD, PFILETIME]

# WINADVAPI LONG WINAPI RegEnumValueW(HKEY,DWORD,LPWSTR,PDWORD,PDWORD,PDWORD,
#                                     LPBYTE,PDWORD);
RegEnumValueW = cdll.advapi32.RegEnumValueW
RegEnumValueW.restype = LONG
RegEnumValueW.argtypes = [HKEY, DWORD, LPWSTR, PDWORD, PDWORD, PDWORD,
                          LPBYTE, PDWORD]

# WINADVAPI LONG WINAPI RegFlushKey(HKEY);
RegFlushKey = cdll.advapi32.RegFlushKey
RegFlushKey.restype = LONG
RegFlushKey.argtypes = [HKEY]

# WINADVAPI LONG WINAPI RegLoadKeyW(HKEY,LPCWSTR,LPCWSTR)
RegLoadKeyW = cdll.advapi32.RegLoadKeyW
RegLoadKeyW.restype = LONG
RegLoadKeyW.argtypes = [HKEY, LPCWSTR, LPCWSTR]

# WINADVAPI LONG WINAPI RegOpenKeyExW(HKEY,LPCWSTR,DWORD,REGSAM,PHKEY)
RegOpenKeyExW = cdll.advapi32.RegOpenKeyExW
RegOpenKeyExW.restype = LONG
RegOpenKeyExW.argtypes = [HKEY, LPCWSTR, DWORD, REGSAM, PHKEY]

# WINADVAPI LONG WINAPI RegQueryValueW(HKEY,LPCWSTR,LPWSTR,PLONG);
RegQueryValueW = cdll.advapi32.RegQueryValueW
RegQueryValueW.restype = LONG
RegQueryValueW.argtypes = [HKEY, LPCWSTR, LPWSTR, PLONG]

# WINADVAPI LONG WINAPI RegQueryValueExW(HKEY,LPCWSTR,LPDWORD,LPDWORD,LPBYTE,
#                                        LPDWORD);
RegQueryValueExW = cdll.advapi32.RegQueryValueExW
RegQueryValueExW.restype = LONG
RegQueryValueExW.argtypes = [HKEY, LPCWSTR, LPDWORD, LPDWORD, LPBYTE, LPDWORD]

# WINADVAPI LONG WINAPI RegSaveKeyW(HKEY,LPCWSTR,LPSECURITY_ATTRIBUTES);
RegSaveKeyW = cdll.advapi32.RegSaveKeyW
RegSaveKeyW.restype = LONG
RegSaveKeyW.argtypes = [HKEY, LPCWSTR, c_void_p]

# WINADVAPI LONG WINAPI RegSetValueW(HKEY,LPCWSTR,DWORD,LPCWSTR,DWORD);
RegSetValueW = cdll.advapi32.RegSetValueW
RegSetValueW.restype = LONG
RegSetValueW.argtypes = [HKEY, LPCWSTR, DWORD, LPCWSTR, DWORD]

# WINADVAPI LONG WINAPI RegSetValueExW(HKEY,LPCWSTR,DWORD,DWORD,const BYTE*,
#                                      DWORD);
RegSetValueExW = cdll.advapi32.RegSetValueExW
RegSetValueExW.restype = LONG
RegSetValueExW.argtypes = [HKEY, LPCWSTR, DWORD, DWORD, PBYTE, DWORD]

_winerror_to_errno = {2: 2,
                      3: 2,
                      4: 24,
                      5: 13,
                      6: 9,
                      7: 12,
                      8: 12,
                      9: 12,
                      10: 7,
                      11: 8,
                      15: 2,
                      16: 13,
                      17: 18,
                      18: 2,
                      19: 13,
                      20: 13,
                      21: 13,
                      22: 13,
                      23: 13,
                      24: 13,
                      25: 13,
                      26: 13,
                      27: 13,
                      28: 13,
                      29: 13,
                      30: 13,
                      31: 13,
                      32: 13,
                      33: 13,
                      34: 13,
                      35: 13,
                      36: 13,
                      53: 2,
                      65: 13,
                      67: 2,
                      80: 17,
                      82: 13,
                      83: 13,
                      89: 11,
                      108: 13,
                      109: 32,
                      112: 28,
                      114: 9,
                      128: 10,
                      129: 10,
                      130: 9,
                      132: 13,
                      145: 41,
                      158: 13,
                      161: 2,
                      164: 11,
                      167: 13,
                      183: 17,
                      188: 8,
                      189: 8,
                      190: 8,
                      191: 8,
                      192: 8,
                      193: 8,
                      194: 8,
                      195: 8,
                      196: 8,
                      197: 8,
                      198: 8,
                      199: 8,
                      200: 8,
                      201: 8,
                      202: 8,
                      206: 2,
                      215: 11,
                      1816: 12}
def winerror_to_errno(winerror):
    from errno import EINVAL
    return _winerror_to_errno.get(winerror, EINVAL)

def winerror_to_strerror(winerror):
    # buf is actually a string, but is initially set to NULL
    buf = c_void_p(None)
    len = FormatMessageW(
        # Error API error
        (FORMAT_MESSAGE_ALLOCATE_BUFFER |
         FORMAT_MESSAGE_FROM_SYSTEM |
         FORMAT_MESSAGE_IGNORE_INSERTS),
        None,                   # no message source 
        c_ulong(winerror),
        LANG_NEUTRAL,           # Default language
        byref(buf),
        0,                      # size not used
        None)                   # no args
    if len == 0:
        # Only seen this in out of mem situations
        return "Windows Error 0x%X" % winerror
    else:
        result = cast(buf, LPWSTR).value
        LocalFree(buf)
    # remove trailing cr/lf and dots
    return re.sub(r'[\s.]*$', '', result)

def wincall(return_code):
    from cygwinreg.constants import ERROR_SUCCESS
    if not isinstance(return_code, (int, long)):
        return_code = return_code.value
    if return_code != ERROR_SUCCESS:
        raise WindowsError(return_code)
    return return_code

# We need to provide our own copy of exceptions.Windowsrror, since
# Python under Cygwin doesn't have a WindowsError.
class WindowsError(OSError):
    def __init__(self, winerror, strerror=None, filename=None):
        if winerror == 0:
            winerror = GetLastError()
        self.winerror = winerror
        self.errno = winerror_to_errno(winerror)
        if strerror is None:
            self.strerror = winerror_to_strerror(winerror)
        else:
            self.strerror = strerror
        self.filename = filename

    def __str__(self):
        if self.filename is not None:
            return "[Error %s] %s: %s" % (self.winerror, self.strerror,
                                          repr(self.filename))
        else:
            return "[Error %s] %s" % (self.winerror, self.strerror)
exceptions.WindowsError = WindowsError

def py_to_reg(value, typ):
    """Convert a Python object to Registry data.

    Returns a ctypes.c_char array.
    """
    def utf16(basestring):
        if isinstance(basestring, str):
            basestring = basestring.decode(getpreferredencoding())
        return basestring.encode('utf-16-le')

    exception = ValueError("Could not convert the data to the specified type.")
    if typ == REG_DWORD:
        if value is None:
            buf = create_string_buffer(pack('L', 0), sizeof(DWORD))
        else:
            buf = create_string_buffer(pack('L', value), sizeof(DWORD))
    elif typ in (REG_SZ, REG_EXPAND_SZ):
        if not isinstance(value, basestring):
            raise ValueError("Value must be a string or a unicode object.")
        if value is None:
            value = u''
        buf = create_string_buffer(utf16(value))
    elif typ == REG_MULTI_SZ:
        if not hasattr(value, '__iter__'):
            raise ValueError("Value must be a sequence or iterable.")
        if value is None:
            value = []
        result = []
        count = 0
        for elem in value:
            if not isinstance(elem, basestring):
                raise ValueError("Element %d must be a string or a unicode "
                                 "object." % count)
            if elem is None:
                elem = u''
            result.append(utf16(elem))
            count += 1
        result.append(utf16(u'')) # Terminate the list with an empty string
        result = '\x00\x00'.join(result)
        buf = create_string_buffer(result, len(result))
    else:
        # Handle REG_BINARY and ALSO handle ALL unknown data types
        # here.  Even if we can't support it natively, we should
        # handle the bits.
        if value is None:
            buf = create_string_buffer(0)
        try:
            buf = buffer(value)
            buf = create_string_buffer(str(buf), len(buf))
        except TypeError:
            raise TypeError("Objects of type '%s' can not be used as "
                            "binary registry values" % type(value))
    return buf

UTF16LE_NULL = re.compile(r'(?<![\x01-\x7f])\x00\x00')

def reg_to_py(data_buf, data_size, typ):
    """Convert Registry data to a Python object."""
    if hasattr(data_size, 'value'):
        data_size = data_size.value
    if hasattr(typ, 'value'):
        typ = typ.value
    if typ == REG_DWORD:
        if data_size == 0:
            return 0L
        return unpack_from('L', data_buf)[0]
    elif typ in (REG_SZ, REG_EXPAND_SZ):
        # data_buf may or may not have a trailing NULL in the buffer.
        if data_size % 2:
            data_size -= 1
        buf = data_buf.raw
        if len(buf) > data_size:
            buf = buf[:data_size]
        return UTF16LE_NULL.split(buf, 1)[0].decode('utf-16-le')
    elif typ == REG_MULTI_SZ:
        # data_buf may or may not have a trailing NULL in the buffer.
        if data_size % 2:
            data_size -= 1
        # The registry specification calls for strings to be
        # terminated with 2 null bytes.  It seems some commercial
        # packages install strings which dont conform, causing this
        # code to fail - however, "regedit" etc still work with these
        # strings (ie only we dont!).
        buf = data_buf.raw 
        if len(buf) > data_size:
            buf = buf[:data_size]
        result = []
        for s in UTF16LE_NULL.split(buf):
            if s == "":
                break
            result.append(s.decode('utf-16-le'))
        return result
    else:
        # Handle REG_BINARY and ALSO handle ALL unknown data types
        # here.  Even if we can't support it natively, we should
        # handle the bits.
        if not data_size:
            return None
        return str(data_buf[:data_size])

