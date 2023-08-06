import collections
import json
import os
import subprocess
import sys
import types


def collect():
    collectors = {
        "sys": _collect_sys,
        "os": _collect_os,
        "platform": _collect_platform,
        "psutil": _collect_psutil,
        "sysctl": _collect_sysctl,
        "system_profiler": _collect_system_profiler,
    }
    values = {}
    for name, collector in collectors.items():
        try:
            values[name] = collector()
        except Exception as e:
            values[name] = f"Exception: {e}"

    values_serializable = to_json_serializable(values)

    return json.dumps(values_serializable)


def to_json_serializable(value):
    if value is None:
        return None
    elif isinstance(value, (int, float)):
        return value
    elif isinstance(value, (list, tuple)):
        return [to_json_serializable(x) for x in value]
    elif callable(value):
        try:
            return to_json_serializable(value())
        except Exception as e:
            return f"Exception: {e}"
    elif isinstance(value, dict):
        values_serializable = {}
        for key, value in value.items():
            values_serializable[key] = to_json_serializable(value)
        return values_serializable
    elif isinstance(value, str):
        return value
    elif isinstance(
        value,
        (
            type(sys.flags),
            type(sys.float_info),
            type(sys.hash_info),
            type(sys.int_info),
            type(sys.thread_info),
            type(sys.version_info),
            os.terminal_size,
            type(os.uname()),
            types.SimpleNamespace,
        ),
    ):
        return {
            n: to_json_serializable(getattr(sys.flags, n))
            for n in sys.flags.__dir__()
            if not n.startswith("__")
        }
    else:
        return None


def _collect_sys():
    names = [
        "abiflags",
        "byteorder",
        "executable",
        "flags",
        "float_info",
        "float_repr_style",
        "getswitchinterval",
        "getwindowsversion",
        "hash_info",
        "hexversion",
        "implementation",
        "int_info",
        "maxsize",
        "maxunicode",
        "platform",
        "thread_info",
        "tracebacklimit",
        "version",
        "api_version",
        "version_info",
        "warnoptions",
        "winver",
        "_xoptions",
    ]
    values = {}

    for name in names:
        try:
            value = getattr(sys, name)
            if callable(value):
                value = value()
            values[name] = value
        except Exception as e:
            values[name] = f"Exception: {e}"

    return values


def _collect_os():
    names = [
        "name",
        "supports_bytes_environ",
        "uname",
        "get_terminal_size",
        "confstr_names",
        "cpu_count",
        "getloadavg",
        ("sysconf", lambda: {x: os.sysconf(x) for x in os.sysconf_names}),
        "sep",
        "altsep",
        "extsep",
        "pathsep",
        "defpath",
        "linesep",
        "devnull",
    ]
    values = {}

    for name in names:
        try:
            if isinstance(name, tuple):
                name, value = name
                values[name] = value()
                continue
            value = getattr(os, name)
            if callable(value):
                value = value()
            values[name] = value
        except Exception as e:
            values[name] = f"Exception: {e}"

    return values


def _collect_platform():
    import platform

    names = [
        "architecture",
        "machine",
        "node",
        "platform",
        "processor",
        "python_build",
        "python_compiler",
        "python_branch",
        "python_implementation",
        "python_revision",
        "python_version",
        "python_version_tuple",
        "release",
        "system",
        "version",
        "uname",
        "java_version",
        "win32_verion",
        "win32_edition",
        "win32_is_iot",
        "mac_ver",
        "libc_ver",
        "freedesktop_os_release",
    ]
    values = {}

    for name in names:
        try:
            if isinstance(name, tuple):
                name, value = name
                values[name] = value()
                continue
            value = getattr(platform, name)
            if callable(value):
                value = value()
            values[name] = value
        except Exception as e:
            values[name] = f"Exception: {e}"

    return values


def _collect_sys():
    names = [
        "abiflags",
        "byteorder",
        "executable",
        "flags",
        "float_info",
        "float_repr_style",
        "getswitchinterval",
        "getwindowsversion",
        "hash_info",
        "hexversion",
        "implementation",
        "int_info",
        "maxsize",
        "maxunicode",
        "platform",
        "thread_info",
        "tracebacklimit",
        "version",
        "api_version",
        "version_info",
        "warnoptions",
        "winver",
        "_xoptions",
    ]
    values = {}

    import sys

    for name in names:
        try:
            value = getattr(sys, name)
            if callable(value):
                value = value()
            values[name] = value
        except Exception as e:
            values[name] = f"Exception: {e}"

    return values


def _collect_os():
    names = [
        "name",
        "supports_bytes_environ",
        "uname",
        "get_terminal_size",
        "confstr_names",
        "cpu_count",
        "getloadavg",
        ("sysconf", lambda: {x: os.sysconf(x) for x in os.sysconf_names}),
        "sep",
        "altsep",
        "extsep",
        "pathsep",
        "defpath",
        "linesep",
        "devnull",
    ]
    values = {}

    for name in names:
        try:
            if isinstance(name, tuple):
                name, value = name
                values[name] = value()
                continue
            value = getattr(os, name)
            if callable(value):
                value = value()
            values[name] = value
        except Exception as e:
            values[name] = f"Exception: {e}"

    return values


def _collect_psutil():
    import psutil

    names = [
        "cpu_times",
        ("cpu_count_logical", lambda: psutil.cpu_count()),
        ("cpu_count", lambda: psutil.cpu_count(logical=False)),
        "cpu_stats",
        "cpu_freq",
        "getloadavg",
        "virtual_memory",
        "swap_memory",
        "sensors_temperatures",
        "sensors_fans",
        "sensors_battery",
        "boot_time",
    ]
    values = {}

    for name in names:
        try:
            if isinstance(name, tuple):
                name, value = name
                values[name] = value()
                continue
            value = getattr(psutil, name)
            if callable(value):
                value = value()
            values[name] = value
        except Exception as e:
            values[name] = f"Exception: {e}"

    return values


def _collect_sysctl():
    process = subprocess.run(["sysctl", "-a"], stdout=subprocess.PIPE, check=True)
    output = process.stdout.decode("utf-8")
    values = {}

    for line in output.splitlines():
        if not line.strip():
            continue
        name, value = line.split(": ", 1)
        values[name] = value
    return values


def _collect_system_profiler():
    data_types = [
        "SPUniversalAccessDataType",
        "SPSecureElementDataType",
        "SPiBridgeDataType",
        "SPDisplaysDataType",
        "SPHardwareDataType",
        "SPInternationalDataType",
        "SPMemoryDataType",
        "SPNVMeDataType",
        "SPPowerDataType",
        "SPSPIDataType",
        "SPSmartCardsDataType",
        "SPSoftwareDataType",
        "SPStartupItemDataType",
        "SPStorageDataType",
        "SPThunderboltDataType",
        "SPUSBDataType",
    ]

    process = subprocess.run(
        ["system_profiler", "-json", "-detailLevel", "mini", *data_types],
        stdout=subprocess.PIPE,
        check=True,
    )
    output = process.stdout.decode("utf-8")
    return json.loads(output)
