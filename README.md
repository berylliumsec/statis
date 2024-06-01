# statis
![Statis](img/statis.png)

## Acknowledgement

First i would like to thank the All-Mighty God who is the source of all knowledge, without Him, this would not be possible.

## Overview

Statis is a tool available in both Python and C# that modifies a specific function in the memory of running processes. Like other implementations out there in the wild, it is  designed to find and patch the AmsiScanBuffer function in the amsi.dll module within PowerShell processes using python. The primary use case for this script is to disable the AMSI (Antimalware Scan Interface) by patching the AmsiScanBuffer function to bypass malware scanning

## Features

- Find PowerShell Processes: Identifies all running PowerShell processes on the system.
- Read Process Memory: Reads memory of the targeted process to locate the AmsiScanBuffer function.
- Patch Process Memory: Patches the AmsiScanBuffer function to disable its functionality.
- Logging: Detailed logging of all operations for debugging.



## Prerequisites

- Windows operating system.
- Python 3.x installed.
- Cython
- Pyinstaller


## How It Works

- Initialization: The script initializes by setting up logging and loading the kernel32.dll for Windows API functions.
- Get PowerShell PIDs: The script uses the tasklist command to fetch the PIDs of all running PowerShell processes.
- Open Process: For each PowerShell process, the script opens the process with necessary permissions.
- Find amsi.dll Base Address: The script locates the base address of the amsi.dll module in the process memory.
- Read AmsiScanBuffer Address: It searches for the AmsiScanBuffer function within the amsi.dll module.
- Patch AmsiScanBuffer: The function is patched with a payload to disable its scanning capabilities.
- Close Process Handle: Finally, the script closes the handle to the process.


## Build - Python

From the src folder run:

```bash
python cythonize_disable_amsi.py
pyinstaller  --log-level=DEBUG statis.spec
```

You will find statis.exe in a folder named `dist`. Execute `.\statis.exe` from a powershell session and it will disable AMSI.


## Build - C# via Visual Studio

- Open Visual Studio:
- Launch Visual Studio from your Start menu or desktop.

## Create a New Project:

- Go to File > New > Project....
- In the "Create a new project" window, select Console App (.NET Core or .NET Framework) as the project type.
- Click Next.
- Configure Your Project: Give your project a name, e.g., DisableAmsi.
- Choose a location to save your project.
- Click Create.
- Once the project is created, you will see Program.cs in the Solution Explorer.
- Replace the contents of Program.cs with the content of disable_amsi.cs:


**Build the Project:**

- Go to Build > Build Solution or press Ctrl+Shift+B to build the project.
- Ensure there are no build errors.

**Run the Executable:**

Once the build is successful, you can find the executable file in the bin\Debug\yourapp directory within your project folder.
Run the executable from a powershell session.
