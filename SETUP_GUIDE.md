# Python Server Manager Setup Guide
## Complete Cross-Platform Installation & Usage Guide

### Table of Contents
1. [Prerequisites](#section-1-prerequisites)
2. [Setup Server Manager](#section-2-setup-server-manager)
3. [Gitignore Creation](#section-3-gitignore-creation)
4. [Usage Guide](#section-4-usage-guide)
5. [Maintenance](#section-5-maintenance)
6. [Troubleshooting](#section-6-troubleshooting)

---

## Section 1: Prerequisites

### 1.1 Install Python

#### **macOS**
```bash
# Method 1: Using Homebrew (Recommended)
brew install python

# Method 2: Download from python.org
# Visit https://www.python.org/downloads/macos/

# Verify installation
python3 --version
```

#### **Windows**
```powershell
# Method 1: Microsoft Store
# Search "Python" in Microsoft Store and install

# Method 2: Download from python.org
# Visit https://www.python.org/downloads/windows/
# Check "Add Python to PATH" during installation

# Method 3: Using Chocolatey
choco install python

# Verify installation
python --version
# or
python3 --version
```

#### **Linux (Ubuntu/Debian)**
```bash
# Update package list
sudo apt update

# Install Python 3 and pip
sudo apt install python3 python3-pip

# Verify installation
python3 --version
```

#### **Linux (CentOS/RHEL/Fedora)**
```bash
# For Fedora
sudo dnf install python3 python3-pip

# For CentOS/RHEL
sudo yum install python3 python3-pip
# or for newer versions:
sudo dnf install python3 python3-pip

# Verify installation
python3 --version
```

### 1.2 Install psutil Dependency

#### **macOS**
```bash
# Method 1: Standard installation
pip3 install psutil

# Method 2: For externally managed environments
pip3 install --user psutil

# Method 3: With system packages flag (if needed)
pip3 install --break-system-packages psutil

# Method 4: Using Homebrew
brew install python-psutil
```

#### **Windows**
```powershell
# Standard installation
pip install psutil

# If using Python 3 specifically
pip3 install psutil

# For user installation (if admin rights unavailable)
pip install --user psutil
```

#### **Linux (Ubuntu/Debian)**
```bash
# Using pip (recommended)
pip3 install --user psutil

# Using system package manager
sudo apt install python3-psutil

# Global installation (if needed)
sudo pip3 install psutil
```

#### **Linux (CentOS/RHEL/Fedora)**
```bash
# Using pip (recommended)
pip3 install --user psutil

# Using system package manager (Fedora)
sudo dnf install python3-psutil

# Using system package manager (CentOS/RHEL)
sudo yum install python3-psutil
```

### 1.3 Verify Dependencies
```bash
# Test psutil installation (cross-platform)
python3 -c "import psutil; print('psutil version:', psutil.__version__)"
```

---

## Section 2: Setup Server Manager

### 2.1 Download the Script

#### **Method 1: Manual Download**
1. Download `python_server_manager.py` from the repository
2. Save it to a central location:
   - **macOS/Linux**: `~/scripts/python_server_manager.py`
   - **Windows**: `C:\Scripts\python_server_manager.py`

#### **Method 2: Using curl (macOS/Linux)**
```bash
# Create scripts directory
mkdir -p ~/scripts

# Download the script
curl -o ~/scripts/python_server_manager.py https://raw.githubusercontent.com/your-repo/python_server_manager.py

# Make executable
chmod +x ~/scripts/python_server_manager.py
```

#### **Method 3: Using PowerShell (Windows)**
```powershell
# Create scripts directory
New-Item -ItemType Directory -Force -Path "C:\Scripts"

# Download the script
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/your-repo/python_server_manager.py" -OutFile "C:\Scripts\python_server_manager.py"
```

### 2.2 Manual Project Setup

#### **macOS/Linux**
```bash
# Navigate to your project directory
cd /path/to/your/project

# Method 1: Copy the script
cp ~/scripts/python_server_manager.py ./server_manager.py

# Method 2: Create symlink (recommended)
ln -s ~/scripts/python_server_manager.py server_manager.py

# Verify setup
ls -la server_manager.py
```

#### **Windows (Command Prompt)**
```cmd
# Navigate to your project directory
cd C:\path\to\your\project

# Copy the script
copy "C:\Scripts\python_server_manager.py" "server_manager.py"

# Verify setup
dir server_manager.py
```

#### **Windows (PowerShell)**
```powershell
# Navigate to your project directory
cd C:\path\to\your\project

# Copy the script
Copy-Item "C:\Scripts\python_server_manager.py" -Destination "server_manager.py"

# Create symbolic link (requires admin privileges)
New-Item -ItemType SymbolicLink -Path "server_manager.py" -Target "C:\Scripts\python_server_manager.py"
```

### 2.3 Automated Setup Script

Create this setup script for easy project integration:

#### **macOS/Linux Setup Script**
```bash
#!/bin/bash
# save as: setup_server_manager.sh

PROJECT_DIR="$1"
SCRIPT_PATH="$HOME/scripts/python_server_manager.py"

if [ -z "$PROJECT_DIR" ]; then
    echo "Usage: $0 /path/to/your/project"
    exit 1
fi

cd "$PROJECT_DIR"

# Create/update .gitignore
echo "# Python Server Manager" >> .gitignore
echo "server_manager.py" >> .gitignore
echo "python_server_manager.py" >> .gitignore

# Create symlink
ln -sf "$SCRIPT_PATH" server_manager.py

echo "✅ Server manager setup complete!"
echo "Usage: python3 server_manager.py quick"
```

#### **Windows Setup Script (PowerShell)**
```powershell
# save as: setup_server_manager.ps1
param([string]$ProjectDir)

$ScriptPath = "C:\Scripts\python_server_manager.py"

if (-not $ProjectDir) {
    Write-Host "Usage: .\setup_server_manager.ps1 C:\path\to\your\project"
    exit 1
}

Set-Location $ProjectDir

# Create/update .gitignore
Add-Content -Path ".gitignore" -Value "# Python Server Manager"
Add-Content -Path ".gitignore" -Value "server_manager.py"
Add-Content -Path ".gitignore" -Value "python_server_manager.py"

# Copy script
Copy-Item $ScriptPath -Destination "server_manager.py"

Write-Host "✅ Server manager setup complete!"
Write-Host "Usage: python server_manager.py quick"
```

---

## Section 3: Gitignore Creation

### 3.1 Automatic Method (Using Setup Scripts)
Run the setup scripts from Section 2.3 above.

### 3.2 Manual Method

#### **macOS/Linux**
```bash
# Navigate to project directory
cd /path/to/your/project

# Create .gitignore if it doesn't exist
touch .gitignore

# Add server manager entries
cat >> .gitignore << 'EOF'

# Python Server Manager (local development tool)
server_manager.py
python_server_manager.py

# Python
__pycache__/
*.py[cod]
*.pyc
*.pyo

# Virtual Environments
venv/
env/
.env
.venv/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS Files
.DS_Store
Thumbs.db

# Logs
*.log
logs/
EOF
```

#### **Windows (Command Prompt)**
```cmd
cd C:\path\to\your\project

# Create .gitignore
echo. > .gitignore

# Add entries
echo # Python Server Manager (local development tool) >> .gitignore
echo server_manager.py >> .gitignore
echo python_server_manager.py >> .gitignore
echo. >> .gitignore
echo # Python >> .gitignore
echo __pycache__/ >> .gitignore
echo *.pyc >> .gitignore
echo. >> .gitignore
echo # IDEs >> .gitignore
echo .vscode/ >> .gitignore
echo. >> .gitignore
echo # OS Files >> .gitignore
echo .DS_Store >> .gitignore
echo Thumbs.db >> .gitignore
```

#### **Windows (PowerShell)**
```powershell
cd C:\path\to\your\project

# Create .gitignore with content
@"
# Python Server Manager (local development tool)
server_manager.py
python_server_manager.py

# Python
__pycache__/
*.py[cod]
*.pyc
*.pyo

# Virtual Environments
venv/
env/
.env
.venv/

# IDEs
.vscode/
.idea/

# OS Files
.DS_Store
Thumbs.db

# Logs
*.log
logs/
"@ | Out-File -FilePath ".gitignore" -Encoding utf8 -Append
```

### 3.3 VSCode Method (All Platforms)
1. **Open VSCode in your project directory**
2. **Create .gitignore:**
   - Right-click in Explorer panel → "New File"
   - Name it `.gitignore`
3. **Add the content from the manual method above**

---

## Section 4: Usage Guide

### 4.1 Basic Commands

#### **All Platforms**
```bash
# Interactive mode (full menu)
python3 server_manager.py

# Quick start server in current directory
python3 server_manager.py quick

# Show running servers
python3 server_manager.py status

# Stop all servers
python3 server_manager.py stop

# Show help
python3 server_manager.py help
```

#### **Windows-Specific Commands**
```cmd
# If python3 is not available, use python
python server_manager.py quick
python server_manager.py status
```

### 4.2 Interactive Menu Options

When you run `python3 server_manager.py`, you'll see:

```
╔══════════════════════════════════════════════╗
║        Python HTTP Server Manager            ║
╠══════════════════════════════════════════════╣
║  1) Start new server                         ║
║  2) Show running servers                     ║
║  3) Stop servers                             ║
║  4) Restart servers                          ║
║  5) View server logs                         ║
║  6) Open server in browser                   ║
║  7) Show statistics                          ║
║  8) Cleanup logs and PIDs                    ║
║  9) Quick start (current dir, port 8000)     ║
║  0) Exit                                     ║
╚══════════════════════════════════════════════╝
```

### 4.3 Server Configuration Options

#### **Directory Selection:**
1. Current directory
2. Custom directory path
3. Home directory
4. Desktop folder

#### **Port Configuration:**
1. Default port (8000)
2. Auto-find next available port
3. Custom port number
4. Random available port (8000-9000)

#### **Server Options:**
1. Normal foreground mode
2. Auto-open in browser
3. Background with logging
4. Custom bind address

### 4.4 Common Workflows

#### **Quick Development Server**
```bash
# Navigate to your project
cd /path/to/your/project

# Start server with browser auto-open
python3 server_manager.py quick
```

#### **Background Production Server**
1. Run `python3 server_manager.py`
2. Choose option 1 (Start new server)
3. Select your directory
4. Choose option 2 (Auto-find port)
5. Choose option 3 (Background with logging)

#### **Multiple Server Management**
```bash
# Check what's running
python3 server_manager.py status

# Stop specific server by port
python3 server_manager.py
# Choose option 3 → option 2 → enter port number
```

### 4.5 Platform-Specific Usage Notes

#### **macOS**
- Uses `open` command for browser integration
- Process management via Unix signals
- Terminal colors fully supported

#### **Windows**
- Uses default browser for opening URLs
- Process management via Windows APIs
- Color support via colorama (auto-installed)
- Use `python` instead of `python3` if needed

#### **Linux**
- Uses `xdg-open` for browser integration
- Efficient process management
- Full terminal color support
- May require `python3` explicitly

---

## Section 5: Maintenance

### 5.1 File Locations

#### **All Platforms**
- **Logs**: `~/.python_server_logs/` (Unix) or `%USERPROFILE%\.python_server_logs\` (Windows)
- **PIDs**: `~/.python_server_pids/` (Unix) or `%USERPROFILE%\.python_server_pids\` (Windows)
- **Config**: `~/.python_server_config.json` (Unix) or `%USERPROFILE%\.python_server_config.json` (Windows)

### 5.2 Regular Maintenance

#### **Log Cleanup (Automated)**
```bash
# Using the script's built-in cleanup
python3 server_manager.py
# Choose option 8 → option 1 (Remove old logs)
```

#### **Manual Cleanup**
```bash
# macOS/Linux
rm ~/.python_server_logs/*.log
rm ~/.python_server_pids/*.pid

# Windows (PowerShell)
Remove-Item "$env:USERPROFILE\.python_server_logs\*.log"
Remove-Item "$env:USERPROFILE\.python_server_pids\*.pid"
```

### 5.3 Updating the Script

#### **All Platforms**
1. Download the latest version
2. Replace the existing script
3. Restart any running servers if needed

---

## Section 6: Troubleshooting

### 6.1 Common Issues

#### **"ModuleNotFoundError: No module named 'psutil'"**
```bash
# macOS/Linux
pip3 install --user psutil

# Windows
pip install psutil
```

#### **"Permission denied" errors**
- **Windows**: Run terminal as Administrator
- **macOS/Linux**: Check file permissions, use `sudo` if needed
- **Alternative**: Use user directories instead of system directories

#### **Colors not showing**
```bash
# Windows only
pip install colorama

# Script will automatically fall back to no colors if unavailable
```

#### **Port already in use**
- Use option 2 "Find next available port" when starting servers
- Check running servers with `python3 server_manager.py status`
- Kill conflicting processes if needed

#### **Python command not found**
- **Windows**: Use `python` instead of `python3`
- **macOS/Linux**: Ensure Python 3 is installed and in PATH
- **All platforms**: Try `python3.x` where x is your version number

### 6.2 Platform-Specific Issues

#### **macOS**
- **"externally managed environment"**: Use `--user` or `--break-system-packages` flags
- **Permission issues**: Use `sudo` only for system-wide installations

#### **Windows**
- **Execution policy errors**: Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- **Path issues**: Ensure Python is added to system PATH
- **ANSI color issues**: Install Windows Terminal for better color support

#### **Linux**
- **Package manager conflicts**: Prefer `pip3 install --user`
- **Missing pip**: Install `python3-pip` package
- **Display issues**: Ensure `DISPLAY` environment variable is set for browser opening

### 6.3 Getting Help

#### **Built-in Help**
```bash
python3 server_manager.py help
```

#### **Debug Mode**
Add `-v` or `--verbose` flag if implemented, or check the script source for debug options.

#### **Log Analysis**
Check the log files in `~/.python_server_logs/` for detailed error information.

---

## Quick Reference Card

### Essential Commands
```bash
# Setup (one-time)
pip3 install psutil
ln -s /path/to/python_server_manager.py server_manager.py
echo "server_manager.py" >> .gitignore

# Daily usage
python3 server_manager.py quick    # Quick start
python3 server_manager.py status   # Check servers  
python3 server_manager.py          # Full menu
```

### File Structure
```
your-project/
├── server_manager.py      # Symlink (ignored by git)
├── .gitignore            # Contains server manager exclusions
├── your-files...
└── ~/.python_server_logs/ # Logs (in home directory)
```

This guide provides complete cross-platform setup and usage instructions for the Python Server Manager across macOS, Windows, and Linux systems.
