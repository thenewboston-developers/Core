Local development environment setup (for Windows)
=================================================

This section describes how to setup development environment for Windows (tested on Windows 10 specifically).

This guide will use Widows Subsystem for Linux (WSL) to get the development environment running on Windows.

IMPORTANT: After the setup is complete, refer to https://code.visualstudio.com/docs/remote/wsl on how to use VS Code
with WSL.

Initial setup
+++++++++++++
Once initial setup is done only corresponding `Update`_ section (of `INSTALL.linux.rst`_) should be performed
to get the latest version for development.

#. Install Windows Subsystem for Linux (WSL)

   As described on https://docs.microsoft.com/en-us/windows/wsl/install
   run Windows Powershell as administrator and run::

        wsl --install

   Restart system after this

   Then enable WSL by running Powershell as Administrator and run the command::

    dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

   Just to be safe, restart system again

#. Install Ubuntu environment on Windows: search Microsoft store for Ubuntu and install it (login not required).
#. Search for Ubuntu in taskbar or open up a command prompt and type `ubuntu`. This should open up an Ubuntu terminal.
#. Use `INSTALL.linux.rst`_ for the rest of the setup
