import ctypes
from ctypes import wintypes
import sys
import os

class STARTUPINFO(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("lpReserved", wintypes.LPWSTR),
        ("lpDesktop", wintypes.LPWSTR),
        ("lpTitle", wintypes.LPWSTR),
        ("dwX", wintypes.DWORD),
        ("dwY", wintypes.DWORD),
        ("dwXSize", wintypes.DWORD),
        ("dwYSize", wintypes.DWORD),
        ("dwXCountChars", wintypes.DWORD),
        ("dwYCountChars", wintypes.DWORD),
        ("dwFillAttribute", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("wShowWindow", wintypes.WORD),
        ("cbReserved2", wintypes.WORD),
        ("lpReserved2", wintypes.LPBYTE),
        ("hStdInput", wintypes.HANDLE),
        ("hStdOutput", wintypes.HANDLE),
        ("hStdError", wintypes.HANDLE),
    ]

def was_launched_from_shortcut():
    si = STARTUPINFO()
    si.cb = ctypes.sizeof(STARTUPINFO)
    ctypes.windll.kernel32.GetStartupInfoW(ctypes.byref(si))
    with open("shortcut_test_log.txt", "w") as f:
        f.write(f"dwFlags: {si.dwFlags}\n")
        f.write(f"lpTitle: {si.lpTitle}\n")
        f.write(f"IsShortcut: {(si.dwFlags & 0x0800) != 0}\n")
        f.write(f"args: {sys.argv}\n")
        # To identify if it has STARTF_TITLEISLINKNAME
    return (si.dwFlags & 0x0800) != 0

if __name__ == '__main__':
    was_launched_from_shortcut()
