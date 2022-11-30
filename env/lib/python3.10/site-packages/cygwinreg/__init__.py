# -*- coding: utf-8 -*-
#
# Copyright (C) 2009 Akoha. Written by Simon Law <sfllaw@sfllaw.ca>
# 
# This software is licensed under the same terms and conditions as
# Python itself. See the file LICENSE.txt for more details.
#
# It is based on Python's PC/_winreg.c.
#
# cygwinreg/__init__.py
#
# Windows Registry access module for Python.
#
# * Simple registry access written by Mark Hammond in win32api
#       module circa 1995.
# * Bill Tutt expanded the support significantly not long after.
# * Numerous other people have submitted patches since then.
# * Ripped from win32api module 03-Feb-2000 by Mark Hammond, and
#   basic Unicode support added.
# * Ported to Cygwin on 05-Apr-2009 by Simon Law, with full Unicode
#   support finished.


"""
This module provides access to the Windows registry API.

Functions:

CloseKey() - Closes a registry key.
ConnectRegistry() - Establishes a connection to a predefined registry handle
                    on another computer.
CreateKey() - Creates the specified key, or opens it if it already exists.
DeleteKey() - Deletes the specified key.
DeleteValue() - Removes a named value from the specified registry key.
EnumKey() - Enumerates subkeys of the specified open registry key.
EnumValue() - Enumerates values of the specified open registry key.
ExpandEnvironmentStrings() - Expand the env strings in a REG_EXPAND_SZ string.
FlushKey() - Writes all the attributes of the specified key to the registry.
LoadKey() - Creates a subkey under HKEY_USER or HKEY_LOCAL_MACHINE and stores
            registration information from a specified file into that subkey.
OpenKey() - Alias for <om win32api.RegOpenKeyEx>
OpenKeyEx() - Opens the specified key.
QueryValue() - Retrieves the value associated with the unnamed value for a
               specified key in the registry.
QueryValueEx() - Retrieves the type and data for a specified value name
                 associated with an open registry key.
QueryInfoKey() - Returns information about the specified key.
SaveKey() - Saves the specified key, and all its subkeys a file.
SetValue() - Associates a value with a specified key.
SetValueEx() - Stores data in the value field of an open registry key.

Special objects:

HKEYType -- type object for HKEY objects
error -- exception raised for Win32 errors

Integer constants:
Many constants are defined - see the documentation for each function
to see what constants are used, and where.
"""

from ctypes import byref, create_string_buffer, create_unicode_buffer, sizeof
import errno
import sys
from types import NoneType

if sys.platform != 'cygwin':
    raise ImportError('Not running under Cygwin')

from cygwinreg.constants import *
from cygwinreg.w32api import (wincall, WindowsError,
                              DWORD, FILETIME, HKEY, LONG)

class PyHKEY(object):
    """PyHKEY Object - A Python object, representing a win32 registry key.

    This object wraps a Windows HKEY object, automatically closing it when
    the object is destroyed.  To guarantee cleanup, you can call either
    the Close() method on the PyHKEY, or the CloseKey() method.

    All functions which accept a handle object also accept an integer - 
    however, use of the handle object is encouraged.

    Functions:
    Close() - Closes the underlying handle.
    Detach() - Returns the integer Win32 handle, detaching it from the object

    Properties:
    handle - The integer Win32 handle.

    Operations:
    __nonzero__ - Handles with an open object return true, otherwise false.
    __int__ - Converting a handle to an integer returns the Win32 handle.
    __cmp__ - Handle objects are compared using the handle value.
    """
    slots = ('Close', 'Detach', '__enter__', '__exit__', 'handle')

    def __init__(self, hkey, null_ok=False):
        if isinstance(hkey, (int, long)):
            self.hkey = hkey
        elif null_ok and isinstance(hkey, NoneType):
            self.hkey = hkey
        else:
            raise TypeError("A handle must be an integer")

    def __del__(self):
        if self.hkey:
            try:
                self.Close()
            except:
                pass

    def Close(self):
        """key.Close() - Closes the underlying Windows handle.

        If the handle is already closed, no error is raised.
        """
        from cygwinreg.w32api import RegCloseKey
        wincall(RegCloseKey(self.hkey))
        self.hkey = 0

    def Detach(self):
        """int = key.Detach() - Detaches the Windows handle from the handle object.

        The result is the value of the handle before it is detached.  If the
        handle is already detached, this will return zero.

        After calling this function, the handle is effectively invalidated,
        but the handle is not closed.  You would call this function when you
        need the underlying win32 handle to exist beyond the lifetime of the
        handle object.
        On 64 bit windows, the result of this function is a long integer
        """
        hkey = self.hkey
        self.hkey = 0
        return hkey

    def _handle(self):
        return self.hkey
    handle = property(_handle)

    def __enter__(self):
        return self

    def __exit__(*exc_info):
        self.Close()
        return False

    def __hash__(self):
        # Just use the address.
        # XXX - should we use the handle value?
        return id(self)

    def __int__(self):
        return self.hkey

    def __nonzero__(self):
        return bool(self.hkey)

    def __repr__(self):
        return "<PyHKEY at %08X (%08X)>" % (id(self), self.hkey)

    def __str__(self):
        return "<PyHKEY:%08X>" % self.hkey

    _as_parameter_ = property(lambda self: self.hkey)

    @staticmethod
    def make(hkey, null_ok=None):
        if isinstance(hkey, PyHKEY):
            return hkey
        elif isinstance(hkey, (int, long)):
            return PyHKEY(hkey)
        elif null_ok and isinstance(hkey, NoneType):
            return PyHKEY(None)
        else:
            raise TypeError("A handle must be a HKEY object or an integer")

def CloseKey(hkey):
    """CloseKey(hkey) - Closes a previously opened registry key.

    The hkey argument specifies a previously opened key.

    Note that if the key is not closed using this method, it will be
    closed when the hkey object is destroyed by Python.
    """
    PyHKEY.make(hkey).Close()

def ConnectRegistry(computer_name, key):
    """key = ConnectRegistry(computer_name, key) - Establishes a connection to a predefined registry handle on another computer.

    computer_name is the name of the remote computer, of the form \\computername.
    If None, the local computer is used.
    key is the predefined handle to connect to.

    The return value is the handle of the opened key.
    If the function fails, an EnvironmentError exception is raised.
    """
    from cygwinreg.w32api import RegConnectRegistryW
    result = HKEY()
    wincall(RegConnectRegistryW(computer_name, PyHKEY.make(key),
                                byref(result)))
    return PyHKEY(result.value)

def CreateKey(key, sub_key):
    """key = CreateKey(key, sub_key) - Creates or opens the specified key.

    key is an already open key, or one of the predefined HKEY_* constants
    sub_key is a string that names the key this method opens or creates.
    If key is one of the predefined keys, sub_key may be None. In that case,
    the handle returned is the same key handle passed in to the function.

    If the key already exists, this function opens the existing key

    The return value is the handle of the opened key.
    If the function fails, an exception is raised.
    """
    from cygwinreg.w32api import RegCreateKeyW
    result = HKEY()
    wincall(RegCreateKeyW(PyHKEY.make(key), sub_key, byref(result)))
    return PyHKEY(result.value)

def DeleteKey(key, sub_key):
    """DeleteKey(key, sub_key) - Deletes the specified key.

    key is an already open key, or any one of the predefined HKEY_* constants.
    sub_key is a string that must be a subkey of the key identified by the key parameter.
    This value must not be None, and the key may not have subkeys.

    This method can not delete keys with subkeys.

    If the method succeeds, the entire key, including all of its values,
    is removed.  If the method fails, an EnvironmentError exception is raised.
    """
    from cygwinreg.w32api import RegDeleteKeyW
    wincall(RegDeleteKeyW(PyHKEY.make(key), sub_key))

def DeleteValue(key, value):
    """DeleteValue(key, value) - Removes a named value from a registry key.

    key is an already open key, or any one of the predefined HKEY_* constants.
    value is a string that identifies the value to remove.
    """
    from cygwinreg.w32api import RegDeleteValueW
    wincall(RegDeleteValueW(PyHKEY.make(key), value))

def EnumKey(key, index):
    """string = EnumKey(key, index) - Enumerates subkeys of an open registry key.

    key is an already open key, or any one of the predefined HKEY_* constants.
    index is an integer that identifies the index of the key to retrieve.

    The function retrieves the name of one subkey each time it is called.
    It is typically called repeatedly until an EnvironmentError exception is
    raised, indicating no more values are available.
    """
    from cygwinreg.w32api import RegEnumKeyExW
    buf = create_unicode_buffer(256) # max key name length is 255
    length = DWORD(sizeof(buf))
    wincall(RegEnumKeyExW(PyHKEY.make(key), index, buf, byref(length),
                          None, None, None, None))
    return buf[:length.value]

def EnumValue(key, index):
    """tuple = EnumValue(key, index) - Enumerates values of an open registry key.
    key is an already open key, or any one of the predefined HKEY_* constants.
    index is an integer that identifies the index of the value to retrieve.

    The function retrieves the name of one subkey each time it is called.
    It is typically called repeatedly, until an EnvironmentError exception
    is raised, indicating no more values.

    The result is a tuple of 3 items:
    value_name is a string that identifies the value.
    value_data is an object that holds the value data, and whose type depends
    on the underlying registry type.
    data_type is an integer that identifies the type of the value data.
    """
    from cygwinreg.w32api import RegQueryInfoKeyW, RegEnumValueW, reg_to_py
    hkey = PyHKEY.make(key)
    name_size = DWORD()
    data_size = DWORD()
    wincall(RegQueryInfoKeyW(hkey, None, None, None, None, None, None, None,
                             byref(name_size), byref(data_size), None, None))
    name_size.value += 1       # Include null terminators
    data_size.value += 1
    name_buf = create_unicode_buffer(name_size.value)
    data_buf = create_string_buffer(data_size.value)
    typ = DWORD()
    wincall(RegEnumValueW(hkey, index, name_buf, byref(name_size), None,
                          byref(typ), data_buf, byref(data_size)))
    return (name_buf[:name_size.value],
            reg_to_py(data_buf, data_size, typ),
            typ.value)

def FlushKey(key):
    """FlushKey(key) - Writes all the attributes of a key to the registry.

    key is an already open key, or any one of the predefined HKEY_* constants.

    It is not necessary to call RegFlushKey to change a key.
    Registry changes are flushed to disk by the registry using its lazy flusher.
    Registry changes are also flushed to disk at system shutdown.
    Unlike CloseKey(), the FlushKey() method returns only when all the data has
    been written to the registry.
    An application should only call FlushKey() if it requires absolute certainty that registry changes are on disk.
    If you don't know whether a FlushKey() call is required, it probably isn't.
    """
    from cygwinreg.w32api import RegFlushKey
    wincall(RegFlushKey(PyHKEY.make(key)))

def LoadKey(key, sub_key, file_name):
    """LoadKey(key, sub_key, file_name) - Creates a subkey under the specified key
    and stores registration information from a specified file into that subkey.

    key is an already open key, or any one of the predefined HKEY_* constants.
    sub_key is a string that identifies the sub_key to load
    file_name is the name of the file to load registry data from.
    This file must have been created with the SaveKey() function.
    Under the file allocation table (FAT) file system, the filename may not
    have an extension.

    A call to LoadKey() fails if the calling process does not have the
    SE_RESTORE_PRIVILEGE privilege.

    If key is a handle returned by ConnectRegistry(), then the path specified
    in fileName is relative to the remote computer.

    The docs imply key must be in the HKEY_USER or HKEY_LOCAL_MACHINE tree
    """
    from cygwinreg.w32api import RegLoadKeyW
    wincall(RegLoadKeyW(PyHKEY.make(key), sub_key, file_name))

def OpenKey(key, sub_key, res=0, sam=KEY_READ):
    """key = OpenKey(key, sub_key, res = 0, sam = KEY_READ) - Opens the specified key.

    key is an already open key, or any one of the predefined HKEY_* constants.
    sub_key is a string that identifies the sub_key to open
    res is a reserved integer, and must be zero.  Default is zero.
    sam is an integer that specifies an access mask that describes the desired
    security access for the key.  Default is KEY_READ

    The result is a new handle to the specified key
    If the function fails, an EnvironmentError exception is raised.
    """
    from cygwinreg.w32api import RegOpenKeyExW
    result = HKEY()
    wincall(RegOpenKeyExW(PyHKEY.make(key), sub_key, res, sam, byref(result)))
    return PyHKEY.make(result.value)

def OpenKeyEx(key, sub_key, res=0, sam=KEY_READ):
    """See OpenKey()"""
    return OpenKey(key, sub_key, res, sam)

def QueryInfoKey(key):
    """tuple = QueryInfoKey(key) - Returns information about a key.

    key is an already open key, or any one of the predefined HKEY_* constants.

    The result is a tuple of 3 items:"
    An integer that identifies the number of sub keys this key has.
    An integer that identifies the number of values this key has.
    A long integer that identifies when the key was last modified (if available)
    as 100's of nanoseconds since Jan 1, 1600.
    """
    from cygwinreg.w32api import RegQueryInfoKeyW
    num_sub_keys = DWORD()
    num_values = DWORD()
    last_write_time = FILETIME()
    wincall(RegQueryInfoKeyW(PyHKEY.make(key), None, None, None,
                             byref(num_sub_keys), None, None,
                             byref(num_values),  None,  None, None,
                             byref(last_write_time)))
    last_write_time = (last_write_time.high << 32 | last_write_time.low)
    return (num_sub_keys.value, num_values.value, last_write_time)

def QueryValue(key, sub_key):
    """string = QueryValue(key, sub_key) - retrieves the unnamed value for a key.

    key is an already open key, or any one of the predefined HKEY_* constants.
    sub_key is a string that holds the name of the subkey with which the value
    is associated.  If this parameter is None or empty, the function retrieves
    the value set by the SetValue() method for the key identified by key."

    Values in the registry have name, type, and data components. This method
    retrieves the data for a key's first value that has a NULL name.
    But the underlying API call doesn't return the type, Lame Lame Lame, DONT USE THIS!!!
    """
    from cygwinreg.w32api import RegQueryValueW
    hkey = PyHKEY.make(key)
    buf_size = LONG()
    wincall(RegQueryValueW(hkey, sub_key, None, byref(buf_size)))
    buf = create_unicode_buffer(buf_size.value)
    wincall(RegQueryValueW(hkey, sub_key, buf, byref(buf_size)))
    return buf.value

def QueryValueEx(key, value_name):
    """value,type_id = QueryValueEx(key, value_name) - Retrieves the type and data for a specified value name associated with an open registry key.

    key is an already open key, or any one of the predefined HKEY_* constants.
    value_name is a string indicating the value to query
    """
    from cygwinreg.w32api import RegQueryValueExW, reg_to_py
    hkey = PyHKEY.make(key)
    buf_size = DWORD()
    wincall(RegQueryValueExW(hkey, value_name, None, None, None,
                             byref(buf_size)))
    # buf is a byte array
    buf = create_string_buffer(buf_size.value)
    typ = DWORD()
    wincall(RegQueryValueExW(hkey, value_name, None, byref(typ), buf,
                             byref(buf_size)))
    return (reg_to_py(buf, buf_size, typ),
            typ.value)

def SaveKey(key, file_name):
    """SaveKey(key, file_name) - Saves the specified key, and all its subkeys to the specified file.

    key is an already open key, or any one of the predefined HKEY_* constants.
    file_name is the name of the file to save registry data to.
    This file cannot already exist. If this filename includes an extension,
    it cannot be used on file allocation table (FAT) file systems by the
    LoadKey(), ReplaceKey() or RestoreKey() methods.

    If key represents a key on a remote computer, the path described by
    file_name is relative to the remote computer.
    The caller of this method must possess the SeBackupPrivilege security privilege.
    This function passes NULL for security_attributes to the API.
    """
    from cygwinreg.w32api import RegSaveKeyW
    wincall(RegSaveKeyW(PyHKEY.make(key), file_name, None))

def SetValue(key, sub_key, value_type, value):
    """SetValue(key, sub_key, value_type, value) - Associates a value with a specified key.

    key is an already open key, or any one of the predefined HKEY_* constants.
    sub_key is a string that names the subkey with which the value is associated.
    value_type is an integer that specifies the type of the data.  Currently this
    must be REG_SZ, meaning only strings are supported.
    value is a string that specifies the new value.

    If the key specified by the sub_key parameter does not exist, the SetValue
    function creates it.

    Value lengths are limited by available memory. Long values (more than
    2048 bytes) should be stored as files with the filenames stored in 
    the configuration registry.  This helps the registry perform efficiently.

    The key identified by the key parameter must have been opened with
    KEY_SET_VALUE access.
    """
    from cygwinreg.w32api import RegSetValueW
    if value_type != REG_SZ:
        raise TypeError("Type must be cygwinreg.REG_SZ")
    value_buf = create_unicode_buffer(value)
    wincall(RegSetValueW(PyHKEY.make(key), sub_key,
                         REG_SZ, value_buf, sizeof(value_buf)))

def SetValueEx(key, value_name, reserved, value_type, value):
    """SetValueEx(key, value_name, reserved, value_type, value) - Stores data in the value field of an open registry key.

    key is an already open key, or any one of the predefined HKEY_* constants.
    value_name is a string containing the name of the value to set, or None
    value_type is an integer that specifies the type of the data.  This should be one of:
      REG_BINARY -- Binary data in any form.
      REG_DWORD -- A 32-bit number.
      REG_DWORD_LITTLE_ENDIAN -- A 32-bit number in little-endian format.
      REG_DWORD_BIG_ENDIAN -- A 32-bit number in big-endian format.
      REG_EXPAND_SZ -- A null-terminated string that contains unexpanded references
                       to environment variables (for example, %PATH%).
      REG_LINK -- A Unicode symbolic link.
      REG_MULTI_SZ -- An sequence of null-terminated strings, terminated by
                      two null characters.  Note that Python handles this
                      termination automatically.
      REG_NONE -- No defined value type.
      REG_RESOURCE_LIST -- A device-driver resource list.
      REG_SZ -- A null-terminated string.
    reserved can be anything - zero is always passed to the API.
    value is a string that specifies the new value.

    This method can also set additional value and type information for the
    specified key.  The key identified by the key parameter must have been
    opened with KEY_SET_VALUE access.

    To open the key, use the CreateKeyEx() or OpenKeyEx() methods.

    Value lengths are limited by available memory. Long values (more than
    2048 bytes) should be stored as files with the filenames stored in 
    the configuration registry.  This helps the registry perform efficiently.
    """
    from cygwinreg.w32api import RegSetValueExW, py_to_reg
    buf = py_to_reg(value, value_type)
    wincall(RegSetValueExW(PyHKEY.make(key), value_name, 0, value_type,
                           buf, len(buffer(buf))))

