# pylint: disable=no-self-use
from typing import Any

from winregistry import RegEntry, RegKey, WinRegistry, WinregType


class Keywords:
    def read_registry_key(
        self,
        key: str,
        key_wow64_32key: bool = False,
    ) -> RegKey:
        """Reading registry key"""
        with WinRegistry() as client:
            resp = client.read_key(key, key_wow64_32key)
        return resp

    def create_registry_key(
        self,
        key: str,
        key_wow64_32key: bool = False,
    ) -> None:
        """Creating registry key"""
        with WinRegistry() as client:
            client.create_key(key, key_wow64_32key)

    def delete_registry_key(
        self,
        key: str,
        key_wow64_32key: bool = False,
    ) -> None:
        """Deleting registry key"""
        with WinRegistry() as client:
            client.delete_key(key, key_wow64_32key)

    def read_registry_entry(
        self,
        key: str,
        value: Any,
        key_wow64_32key: bool = False,
    ) -> RegEntry:
        """Reading value from registry"""
        with WinRegistry() as client:
            resp = client.read_entry(key, value, key_wow64_32key)
        return resp

    def write_registry_entry(
        self,
        key: str,
        value: str,
        data: Any = None,
        reg_type: str = "REG_SZ",
        key_wow64_32key: bool = False,
    ) -> None:
        """Writing (or creating) data in value"""
        with WinRegistry() as client:
            client.write_entry(key, value, data, WinregType[reg_type], key_wow64_32key)

    def delete_registry_entry(
        self,
        key: str,
        value: str,
        key_wow64_32key: bool = False,
    ) -> None:
        """Deleting value from registry"""
        with WinRegistry() as client:
            client.delete_entry(key, value, key_wow64_32key)
