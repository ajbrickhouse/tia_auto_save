# TIA Portal Auto Save Utility

This script is designed to automate the saving of projects within the TIA Portal, using the Siemens Engineering API. It provides a graphical user interface using `tkinter` that allows users to select an active TIA Portal process and schedule automatic saves at a specified interval.

## Features

- Auto-detects running TIA Portal processes.
- Auto-saves projects based on a user-defined interval.
- Provides a progress bar and countdown timer for the next save.
- Offers a refresh option to update the list of detected TIA Portal processes.

## Prerequisites

- TIA Portal installed on the same machine running the script.
- Siemens Engineering API DLL registered on the system.
- Python 3 environment with `tkinter` library available.

## Installation

Ensure that the TIA Portal API DLL is correctly referenced within the script by changing the `clr.AddReference` path to the installed location of the API on your system.

```python
clr.AddReference('C:\\Program Files\\Siemens\\Automation\\Portal V16\\PublicAPI\\V16\\Siemens.Engineering.dll')
```

## How to Use

1. Start your TIA Portal and open the project(s) you want to auto-save.
2. Run this script in your Python environment.
3. The GUI will display all active TIA Portal processes. Select the process corresponding to your project.
4. Set the auto-save interval using the provided spinbox.
5. Start the auto-save function by clicking the "Start Saving" button.
6. The script will begin counting down, displaying the time left until the next auto-save. Progress is shown in the application window and progress bar.

## Dependencies

```python
from tkinter import messagebox
import clr  # Python for .NET library to use .NET assemblies
import schedule  # Used for scheduling the auto-save function
import tkinter as tk  # GUI library for Python
from datetime import datetime
```

## Disclaimer

This script comes with a potential risk of losing unsaved changes if the TIA Portal is closed or goes offline unexpectedly. Always ensure your work is saved before leaving the TIA Portal unattended.

_readme.md genenerated with GPT_
