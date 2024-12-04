###Installing
---
Assuming Python is already installed on your system, create a directory to hold your application and set it as your working directory.

__Nexios__ require Python 3.6 or higher.

```bash
mkdir your_project_name
cd  your_project_name
```

Use Python's venv module to create a virtual environment. This isolates your project's dependencies, ensuring they don't interfere with system-wide packages or other projects. Run the following command to initialize the virtual environment:

```bash
python -m venv venv

```

- The name venv is conventional, but you can choose any name for your virtual environment folder.

- This virtual environment will store all the libraries and dependencies your project requires.

Activate the Virtual Environment

Depending on your operating system, activate the virtual environment using one of the following commands:

- Windows

```bash
    venv\Scripts\activate
```

- Linux/Mac

```bash
    source venv/bin/activate
```

After activation, your terminal will display the virtual environment's name as a prefix (e.g., (venv)), indicating that it is active.

Once activated, you can install project-specific dependencies, and they will be stored within the virtual environment. When you're done working on the project, deactivate the environment with the deactivate command

Run the follow command to install nexios

```bash
pip install nexios
```

Confirm the installation by running :

```bash
python -m nexios
```

You should see an output like this :

```text
      _   _                 _               
 | \ | |               (_)              
 |  \| |   ___  __  __  _    ___    ___ 
 | . ` |  / _ \ \ \/ / | |  / _ \  / __|
 | |\  | |  __/  >  <  | | | (_) | \__ \
 |_| \_|  \___| /_/\_\ |_|  \___/  |___/
                                               
    🚀 Welcome to Nexios 🚀
      The sleek ASGI Backend Framework
      Version: X.X.X
```

__Congrat you have installed nexios__