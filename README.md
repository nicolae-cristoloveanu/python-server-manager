# Cross-Platform Python HTTP Server Manager

A powerful, interactive Python script for managing Python's built-in HTTP server across Windows, macOS, and Linux systems. This cross-platform version replaces Unix-specific commands with Python-native solutions that work everywhere.

## Features

### 🔄 Cross-Platform Compatibility
- **Windows 10/11** - Full support with native Windows process management
- **macOS** - Optimized for macOS with proper process detection
- **Linux** - Works with all major Linux distributions
- **Color support** - Automatic color detection with fallback for older systems

### 🚀 Core Functionality
- **Interactive Menu System** - User-friendly interface with numbered options
- **Multiple Server Management** - Start, stop, and monitor multiple servers simultaneously
- **Smart Port Detection** - Automatic port availability checking and suggestions
- **Background Processing** - Run servers in background with logging
- **Browser Integration** - Automatic browser opening for started servers
- **Process Monitoring** - Real-time server status and resource usage

### 📊 Advanced Features
- **Comprehensive Logging** - Detailed logs with timestamp and rotation
- **Configuration Management** - JSON-based config with persistent settings
- **Cleanup Tools** - Automatic cleanup of orphaned processes and old logs
- **Statistics Dashboard** - Server usage statistics and system info
- **Command Line Interface** - Quick commands for automation

## Installation

### Prerequisites
- **Python 3.6+** (tested with 3.7-3.13)
- **psutil** library for cross-platform process management

### Quick Install

#### Method 1: Clone Repository (Recommended)
```bash
# 1. Clone the repository
git clone https://github.com/your-username/python-server-manager.git
cd python-server-manager

# 2. Install dependencies
pip3 install -r requirements.txt

# Or on systems with externally managed environments:
pip3 install --user -r requirements.txt

# 3. Make executable (Unix systems)
chmod +x python_server_manager.py

# 4. Test the installation
python3 python_server_manager.py --help
```

#### Method 2: Direct Download
```bash
# 1. Download the script
curl -O https://raw.githubusercontent.com/your-username/python-server-manager/main/python_server_manager.py

# 2. Install dependencies
pip3 install psutil

# 3. Make executable (Unix systems)
chmod +x python_server_manager.py
```

### Platform-Specific Installation

#### Windows
```powershell
# Install Python from python.org or Microsoft Store
# Install psutil
pip install psutil

# Optional: Install Windows Terminal for better colors
```

#### macOS (Homebrew)
```bash
# Install Python if needed
brew install python

# Install psutil
pip3 install --break-system-packages psutil

# Or use user install
pip3 install --user psutil
```

#### Ubuntu/Debian
```bash
# Install Python and pip
sudo apt update
sudo apt install python3 python3-pip

# Install psutil
pip3 install --user psutil
```

#### CentOS/RHEL/Fedora
```bash
# Install Python and pip
sudo dnf install python3 python3-pip  # Fedora
# OR
sudo yum install python3 python3-pip  # CentOS/RHEL

# Install psutil
pip3 install --user psutil
```

## Usage

### Interactive Mode
```bash
python3 python_server_manager.py
```

This launches the full interactive menu with all features:

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

### Command Line Mode
```bash
# Quick start server in current directory
python3 python_server_manager.py quick

# Interactive server setup
python3 python_server_manager.py start

# Show running servers
python3 python_server_manager.py status

# Stop all servers
python3 python_server_manager.py stop

# Show help
python3 python_server_manager.py help
```

### Server Options

#### Start Server Options
1. **Directory Selection**:
   - Current directory
   - Custom directory path
   - Home directory
   - Desktop folder

2. **Port Configuration**:
   - Default port (8000)
   - Auto-find next available port
   - Custom port number
   - Random available port

3. **Advanced Options**:
   - Normal foreground mode
   - Auto-open in browser
   - Background with logging
   - Custom bind address

#### Example Workflows

**Quick Development Server**:
```bash
# Navigate to your project
cd /path/to/your/project

# Start server with browser
python3 python_server_manager.py quick
```

**Background Production Server**:
1. Run script interactively
2. Choose "Start new server" (option 1)
3. Select directory
4. Choose "Find next available port" (option 2)
5. Select "Start server in background with logging" (option 3)

**Multi-Server Management**:
```bash
# Check running servers
python3 python_server_manager.py status

# Stop specific server by port
python3 python_server_manager.py
# Choose option 3 (Stop servers)
# Choose option 2 (Stop by port)
```

## Project Structure

```
python-server-manager/
├── python_server_manager.py      # Main cross-platform Python script
├── python_server_manager.sh      # Original bash script (Unix only)
├── setup_project_server.sh       # Setup script for projects
├── requirements.txt              # Python dependencies
├── README.md                     # This file
├── SETUP_GUIDE.md               # Comprehensive setup guide
└── .gitignore                   # Git ignore patterns
```

## File Structure (User Data)

The script creates these directories in your home folder:

```
~/.python_server_logs/        # Server log files
~/.python_server_pids/        # Process ID files  
~/.python_server_config.json  # Configuration file

# Log file naming: server_PORT_YYYYMMDD_HHMMSS.log
# PID file naming: server_PORT.pid
```

## Using in Your Projects

To use the server manager in your development projects without committing it to Git:

### Option 1: Using the Setup Script
```bash
# Run the setup script from the python-server-manager directory
./setup_project_server.sh /path/to/your/project
```

### Option 2: Manual Setup
```bash
# Navigate to your project
cd /path/to/your/project

# Create symlink to server manager
ln -s /path/to/python-server-manager/python_server_manager.py server_manager.py

# Add to .gitignore
echo "server_manager.py" >> .gitignore
echo "python_server_manager.py" >> .gitignore

# Now use in your project
python3 server_manager.py quick
```

## Configuration

The script creates a JSON configuration file at `~/.python_server_config.json`:

```json
{
  "servers": {
    "8000": {
      "pid": 12345,
      "directory": "/path/to/served/directory",
      "log_file": "/path/to/log/file.log",
      "started": "2023-07-22T10:30:00"
    }
  },
  "default_port": 8000,
  "auto_open_browser": false
}
```

## Platform-Specific Features

### Windows
- **ANSI Color Support** - Automatic colorama integration for colored output
- **Process Management** - Native Windows process handling
- **Path Handling** - Windows path separator support
- **Browser Integration** - Default browser detection and opening

### macOS
- **Process Detection** - Optimized for macOS process structure
- **Security** - Handles macOS process access permissions
- **Terminal Colors** - Native terminal color support
- **Browser Opening** - Uses macOS `open` command equivalent

### Linux
- **Distribution Agnostic** - Works across all major distributions
- **Process Management** - Efficient Linux process handling
- **Resource Monitoring** - Detailed process resource usage
- **Service Integration** - Can be integrated with systemd

## Troubleshooting

### Common Issues

#### "ModuleNotFoundError: No module named 'psutil'"
```bash
# Install psutil
pip install psutil

# If that fails, try:
pip install --user psutil

# Or use conda:
conda install psutil
```

#### "Permission denied" errors
- **Windows**: Run as Administrator if needed
- **macOS/Linux**: Use `sudo` only if accessing system directories
- **Alternative**: Use user directories instead of system directories

#### Colors not showing on Windows
```bash
# Install colorama
pip install colorama

# Or the script will fall back to no colors automatically
```

#### Port already in use
- The script automatically detects and suggests available ports
- Use option 2 "Find next available port" when starting servers
- Check running servers with `status` command

### Performance Tips

1. **Background Servers**: Use background mode for long-running servers
2. **Log Rotation**: Regularly clean up old logs (option 8)
3. **Port Management**: Use the built-in port detection to avoid conflicts
4. **Resource Monitoring**: Check statistics (option 7) for resource usage

## Security Considerations

- **Local Only**: Default binding is localhost only
- **Port Range**: Restricted to ports 1024-65535 for security
- **Process Management**: Only manages Python HTTP servers
- **File Access**: Respects file system permissions
- **Clean Shutdown**: Proper process termination with timeout

## Contributing

This script is designed to be easily extensible. Key areas for contribution:

- **Additional Platforms**: Support for additional operating systems
- **Server Types**: Support for other Python server types
- **UI Improvements**: Enhanced terminal interface
- **Logging**: Advanced logging features
- **Configuration**: More configuration options

## License

This script is provided as-is for educational and development purposes. Modify and distribute freely.

## Changelog

### Version 1.0 (Cross-Platform)
- ✅ Full cross-platform compatibility (Windows, macOS, Linux)
- ✅ Python-native process management using psutil
- ✅ Interactive menu system with colored output
- ✅ Command-line interface for automation
- ✅ Background server support with logging
- ✅ Browser integration across platforms
- ✅ Configuration management with JSON
- ✅ Comprehensive error handling
- ✅ Statistics and monitoring dashboard
- ✅ Cleanup tools for maintenance

### Improvements over Bash Version
- **Cross-Platform**: Works on Windows without WSL
- **Error Handling**: Robust exception handling
- **Process Management**: More reliable process detection and control
- **Configuration**: Persistent configuration storage
- **Modularity**: Object-oriented design for easy extension
- **Testing**: Easier to unit test Python code
- **Dependencies**: Minimal external dependencies

## Support

For issues, questions, or contributions, please refer to the project documentation or create an issue in the project repository.
# python-server-manager
