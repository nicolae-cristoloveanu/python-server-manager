#!/usr/bin/env python3
"""
Cross-Platform Python HTTP Server Manager
Author: Created for streamlined Python server management
Description: Manages python -m http.server instances across Windows, macOS, and Linux
"""

import os
import sys
import time
import json
import signal
import socket
import psutil
import platform
import subprocess
import webbrowser
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple

# Colors for better output (cross-platform)
class Colors:
    if platform.system() == 'Windows':
        # Windows ANSI color support (Windows 10+)
        try:
            import colorama
            colorama.init()
            RED = '\033[0;31m'
            GREEN = '\033[0;32m'
            YELLOW = '\033[1;33m'
            BLUE = '\033[0;34m'
            CYAN = '\033[0;36m'
            PURPLE = '\033[0;35m'
            NC = '\033[0m'
        except ImportError:
            # Fallback to no colors if colorama not available
            RED = GREEN = YELLOW = BLUE = CYAN = PURPLE = NC = ''
    else:
        RED = '\033[0;31m'
        GREEN = '\033[0;32m'
        YELLOW = '\033[1;33m'
        BLUE = '\033[0;34m'
        CYAN = '\033[0;36m'
        PURPLE = '\033[0;35m'
        NC = '\033[0m'

class ServerManager:
    def __init__(self):
        self.default_port = 8000
        self.home_dir = Path.home()
        self.log_dir = self.home_dir / '.python_server_logs'
        self.pid_dir = self.home_dir / '.python_server_pids'
        self.config_file = self.home_dir / '.python_server_config.json'
        
        # Create necessary directories
        self.log_dir.mkdir(exist_ok=True)
        self.pid_dir.mkdir(exist_ok=True)
        
        # Load or create config
        self.config = self.load_config()
    
    def load_config(self) -> Dict:
        """Load configuration from file or create default"""
        default_config = {
            'servers': {},
            'default_port': 8000,
            'auto_open_browser': False
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return {**default_config, **json.load(f)}
            except (json.JSONDecodeError, IOError):
                return default_config
        return default_config
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except IOError:
            self.print_error("Failed to save configuration")
    
    def print_status(self, message: str):
        print(f"{Colors.GREEN}[INFO]{Colors.NC} {message}")
    
    def print_warning(self, message: str):
        print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")
    
    def print_error(self, message: str):
        print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")
    
    def print_question(self, message: str):
        print(f"{Colors.BLUE}[QUESTION]{Colors.NC} {message}")
    
    def print_server(self, message: str):
        print(f"{Colors.CYAN}[SERVER]{Colors.NC} {message}")
    
    def print_success(self, message: str):
        print(f"{Colors.PURPLE}[SUCCESS]{Colors.NC} {message}")
    
    def check_python(self) -> bool:
        """Check if Python is available"""
        try:
            result = subprocess.run([sys.executable, '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.print_status(f"Using {result.stdout.strip()}")
                return True
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
        
        self.print_error("Python is not available")
        return False
    
    def is_port_available(self, port: int) -> bool:
        """Check if port is available"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.bind(('localhost', port))
                return True
        except OSError:
            return False
    
    def find_available_port(self, start_port: int = None) -> int:
        """Find next available port starting from start_port"""
        if start_port is None:
            start_port = self.default_port
        
        port = start_port
        while not self.is_port_available(port) and port < 65535:
            port += 1
        
        if port >= 65535:
            raise RuntimeError("No available ports found")
        
        return port
    
    def get_running_servers(self) -> List[Dict]:
        """Get list of running Python HTTP servers"""
        servers = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cwd']):
            try:
                cmdline = proc.info['cmdline']
                if (cmdline and len(cmdline) >= 3 and 
                    'python' in cmdline[0].lower() and 
                    '-m' in cmdline and 
                    'http.server' in cmdline):
                    
                    # Extract port from command line
                    port = self.default_port
                    for i, arg in enumerate(cmdline):
                        if arg.isdigit() and 1024 <= int(arg) <= 65535:
                            port = int(arg)
                            break
                    
                    # Get working directory
                    try:
                        cwd = proc.info['cwd'] or 'Unknown'
                    except (psutil.AccessDenied, psutil.NoSuchProcess):
                        cwd = 'Unknown'
                    
                    servers.append({
                        'pid': proc.info['pid'],
                        'port': port,
                        'directory': cwd,
                        'cmdline': ' '.join(cmdline)
                    })
            
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        return servers
    
    def show_running_servers(self) -> bool:
        """Display running Python HTTP servers"""
        self.print_status("Checking for running Python HTTP servers...")
        print()
        
        servers = self.get_running_servers()
        if not servers:
            self.print_warning("No running Python HTTP servers found.")
            return False
        
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║                    Running Python Servers                   ║")
        print("╠══════════════════════════════════════════════════════════════╣")
        
        for server in servers:
            pid = server['pid']
            port = server['port']
            directory = server['directory']
            
            # Truncate directory path if too long
            if len(directory) > 25:
                directory = f"...{Path(directory).name}"
            
            print(f"║ PID: {pid:<6} Port: {port:<6} Directory: {directory[:25]:<25} ║")
        
        print("╚══════════════════════════════════════════════════════════════╝")
        print()
        return True
    
    def start_server(self):
        """Start a new Python HTTP server"""
        print()
        self.print_status("=== START NEW PYTHON HTTP SERVER ===")
        
        # Get directory
        current_dir = Path.cwd()
        self.print_status(f"Current directory: {current_dir}")
        print()
        self.print_question("Where would you like to serve files from?")
        print(f"1) Current directory ({current_dir})")
        print("2) Specify different directory")
        print(f"3) Home directory ({self.home_dir})")
        print(f"4) Desktop ({self.home_dir / 'Desktop'})")
        print()
        
        try:
            dir_choice = input("Enter your choice (1-4): ").strip()
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            return
        
        serve_dir = current_dir
        if dir_choice == '2':
            try:
                custom_dir = input("Enter directory path: ").strip()
                custom_path = Path(custom_dir).expanduser().resolve()
                if custom_path.exists() and custom_path.is_dir():
                    serve_dir = custom_path
                else:
                    self.print_error(f"Directory does not exist: {custom_dir}")
                    return
            except KeyboardInterrupt:
                print("\nOperation cancelled.")
                return
        elif dir_choice == '3':
            serve_dir = self.home_dir
        elif dir_choice == '4':
            serve_dir = self.home_dir / 'Desktop'
            if not serve_dir.exists():
                self.print_error("Desktop directory does not exist")
                return
        
        # Get port
        print()
        self.print_question("What port would you like to use?")
        print("1) Default port (8000)")
        print("2) Find next available port starting from 8000")
        print("3) Specify custom port")
        print("4) Random available port (8000-9000)")
        print()
        
        try:
            port_choice = input("Enter your choice (1-4): ").strip()
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            return
        
        port = self.default_port
        try:
            if port_choice == '2':
                port = self.find_available_port(self.default_port)
                self.print_status(f"Found available port: {port}")
            elif port_choice == '3':
                custom_port = input("Enter port number: ").strip()
                if custom_port.isdigit():
                    port = int(custom_port)
                    if not (1024 <= port <= 65535):
                        self.print_error("Port must be between 1024 and 65535")
                        return
                    if not self.is_port_available(port):
                        self.print_error(f"Port {port} is already in use")
                        return
                else:
                    self.print_error("Invalid port number")
                    return
            elif port_choice == '4':
                import random
                port = self.find_available_port(random.randint(8000, 9000))
                self.print_status(f"Selected random available port: {port}")
        except RuntimeError as e:
            self.print_error(str(e))
            return
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            return
        
        # Additional options
        print()
        self.print_question("Additional server options:")
        print("1) Start server normally")
        print("2) Start server and open in browser")
        print("3) Start server in background with logging")
        print("4) Start server with custom bind address")
        print()
        
        try:
            option_choice = input("Enter your choice (1-4): ").strip()
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            return
        
        bind_address = ""
        open_browser = False
        background = False
        
        if option_choice == '2':
            open_browser = True
        elif option_choice == '3':
            background = True
        elif option_choice == '4':
            try:
                custom_bind = input("Enter bind address (default: localhost): ").strip()
                if custom_bind:
                    bind_address = custom_bind
            except KeyboardInterrupt:
                print("\nOperation cancelled.")
                return
        
        # Start the server
        self.print_status("Starting Python HTTP server...")
        self.print_server(f"Directory: {serve_dir}")
        self.print_server(f"Port: {port}")
        self.print_server(f"URL: http://localhost:{port}")
        
        # Build command
        cmd = [sys.executable, '-m', 'http.server', str(port)]
        if bind_address:
            cmd.extend(['--bind', bind_address])
        
        try:
            if background:
                # Start in background
                log_file = self.log_dir / f"server_{port}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
                self.print_status(f"Starting server in background with logging...")
                
                with open(log_file, 'w') as f:
                    proc = subprocess.Popen(cmd, cwd=serve_dir, stdout=f, stderr=subprocess.STDOUT)
                
                # Save PID
                pid_file = self.pid_dir / f"server_{port}.pid"
                with open(pid_file, 'w') as f:
                    f.write(str(proc.pid))
                
                # Update config
                self.config['servers'][str(port)] = {
                    'pid': proc.pid,
                    'directory': str(serve_dir),
                    'log_file': str(log_file),
                    'started': datetime.now().isoformat()
                }
                self.save_config()
                
                self.print_success(f"Server started in background with PID: {proc.pid}")
                self.print_status(f"Log file: {log_file}")
                
            else:
                # Start in foreground
                if open_browser:
                    self.print_status("Starting server and opening browser...")
                    # Open browser after a short delay
                    import threading
                    def open_browser_delayed():
                        time.sleep(2)
                        try:
                            webbrowser.open(f"http://localhost:{port}")
                        except Exception as e:
                            self.print_error(f"Could not open browser: {e}")
                    
                    threading.Thread(target=open_browser_delayed, daemon=True).start()
                
                self.print_success("Server starting... Press Ctrl+C to stop")
                print("─" * 45)
                
                # Change to serve directory and start server
                original_cwd = Path.cwd()
                try:
                    os.chdir(serve_dir)
                    subprocess.run(cmd)
                except KeyboardInterrupt:
                    print("\nServer stopped by user")
                finally:
                    os.chdir(original_cwd)
        
        except Exception as e:
            self.print_error(f"Failed to start server: {e}")
    
    def stop_servers(self):
        """Stop running servers"""
        print()
        self.print_status("=== STOP PYTHON HTTP SERVERS ===")
        
        if not self.show_running_servers():
            return
        
        print()
        self.print_question("How would you like to stop servers?")
        print("1) Stop specific server by PID")
        print("2) Stop specific server by port")
        print("3) Stop all Python HTTP servers")
        print("4) Back to main menu")
        print()
        
        try:
            stop_choice = input("Enter your choice (1-4): ").strip()
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            return
        
        try:
            if stop_choice == '1':
                pid_str = input("Enter PID to stop: ").strip()
                if pid_str.isdigit():
                    pid = int(pid_str)
                    if psutil.pid_exists(pid):
                        try:
                            proc = psutil.Process(pid)
                            proc.terminate()
                            proc.wait(timeout=5)
                            self.print_success(f"Server with PID {pid} stopped.")
                            self._cleanup_pid_files(pid)
                        except psutil.TimeoutExpired:
                            proc.kill()
                            self.print_success(f"Server with PID {pid} force stopped.")
                        except psutil.AccessDenied:
                            self.print_error(f"Access denied stopping PID {pid}")
                    else:
                        self.print_error(f"No process found with PID {pid}")
                else:
                    self.print_error("Invalid PID format")
            
            elif stop_choice == '2':
                port_str = input("Enter port number: ").strip()
                if port_str.isdigit():
                    port = int(port_str)
                    stopped = False
                    
                    for server in self.get_running_servers():
                        if server['port'] == port:
                            try:
                                proc = psutil.Process(server['pid'])
                                proc.terminate()
                                proc.wait(timeout=5)
                                self.print_success(f"Server on port {port} (PID: {server['pid']}) stopped.")
                                stopped = True
                                break
                            except psutil.TimeoutExpired:
                                proc.kill()
                                self.print_success(f"Server on port {port} force stopped.")
                                stopped = True
                                break
                            except psutil.AccessDenied:
                                self.print_error(f"Access denied stopping server on port {port}")
                    
                    if not stopped:
                        self.print_error(f"No server found on port {port}")
                    
                    # Clean up PID file
                    pid_file = self.pid_dir / f"server_{port}.pid"
                    if pid_file.exists():
                        pid_file.unlink()
                else:
                    self.print_error("Invalid port number")
            
            elif stop_choice == '3':
                self.print_warning("This will stop ALL Python HTTP servers!")
                confirm = input("Are you sure? (y/N): ").strip().lower()
                if confirm == 'y' or confirm == 'yes':
                    servers = self.get_running_servers()
                    stopped_count = 0
                    
                    for server in servers:
                        try:
                            proc = psutil.Process(server['pid'])
                            proc.terminate()
                            proc.wait(timeout=3)
                            stopped_count += 1
                        except psutil.TimeoutExpired:
                            try:
                                proc.kill()
                                stopped_count += 1
                            except:
                                pass
                        except:
                            pass
                    
                    if stopped_count > 0:
                        self.print_success(f"Stopped {stopped_count} Python HTTP servers.")
                    else:
                        self.print_warning("No servers were running.")
                    
                    # Clean up all PID files
                    for pid_file in self.pid_dir.glob("server_*.pid"):
                        pid_file.unlink()
                else:
                    self.print_status("Operation cancelled.")
            
            elif stop_choice == '4':
                return
            else:
                self.print_error("Invalid choice.")
        
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
    
    def _cleanup_pid_files(self, pid: int):
        """Clean up PID files for a stopped process"""
        for pid_file in self.pid_dir.glob("server_*.pid"):
            try:
                with open(pid_file, 'r') as f:
                    if int(f.read().strip()) == pid:
                        pid_file.unlink()
                        break
            except (ValueError, IOError):
                pass
    
    def view_logs(self):
        """View server logs"""
        print()
        self.print_status("=== VIEW SERVER LOGS ===")
        
        log_files = list(self.log_dir.glob("*.log"))
        log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        if not log_files:
            self.print_warning(f"No log files found in {self.log_dir}")
            return
        
        print("Available log files:")
        for i, log_file in enumerate(log_files, 1):
            try:
                mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                print(f"{i}) {log_file.name} (Created: {mtime.strftime('%Y-%m-%d %H:%M')})")
            except OSError:
                print(f"{i}) {log_file.name} (Created: Unknown)")
        
        print()
        try:
            log_choice = input("Enter log number to view (or 'q' to quit): ").strip()
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            return
        
        if log_choice.lower() == 'q':
            return
        
        try:
            if log_choice.isdigit():
                log_index = int(log_choice) - 1
                if 0 <= log_index < len(log_files):
                    selected_log = log_files[log_index]
                    self.print_status(f"Viewing log: {selected_log.name}")
                    print("─" * 45)
                    
                    try:
                        with open(selected_log, 'r') as f:
                            lines = f.readlines()
                            # Show last 50 lines
                            for line in lines[-50:]:
                                print(line.rstrip())
                    except IOError as e:
                        self.print_error(f"Could not read log file: {e}")
                    
                    print("─" * 45)
                else:
                    self.print_error("Invalid selection.")
            else:
                self.print_error("Invalid selection.")
        except ValueError:
            self.print_error("Invalid selection.")
    
    def open_in_browser(self):
        """Open server in browser"""
        print()
        self.print_status("=== OPEN SERVER IN BROWSER ===")
        
        if not self.show_running_servers():
            return
        
        try:
            port_str = input("Enter port number to open in browser: ").strip()
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            return
        
        if port_str.isdigit():
            port = int(port_str)
            if not self.is_port_available(port):  # Port is in use
                self.print_status(f"Opening http://localhost:{port} in browser...")
                try:
                    webbrowser.open(f"http://localhost:{port}")
                    self.print_success("Browser opened!")
                except Exception as e:
                    self.print_error(f"Could not open browser: {e}")
            else:
                self.print_error(f"No server running on port {port}")
        else:
            self.print_error("Invalid port number")
    
    def show_statistics(self):
        """Show server statistics"""
        print()
        self.print_status("=== SERVER STATISTICS ===")
        print()
        
        running_count = len(self.get_running_servers())
        log_count = len(list(self.log_dir.glob("*.log")))
        pid_count = len(list(self.pid_dir.glob("*.pid")))
        
        print("╔══════════════════════════════════════╗")
        print("║           Server Statistics          ║")
        print("╠══════════════════════════════════════╣")
        print(f"║ Running Servers:    {running_count:<15}  ║")
        print(f"║ Log Files:          {log_count:<15}  ║")
        print(f"║ PID Files:          {pid_count:<15}  ║")
        print(f"║ Platform:           {platform.system():<15}  ║")
        print(f"║ Python Version:     {platform.python_version():<15}  ║")
        print("╚══════════════════════════════════════╝")
        print()
    
    def cleanup(self):
        """Cleanup old logs and PIDs"""
        print()
        self.print_status("=== CLEANUP ===")
        
        self.print_question("What would you like to clean up?")
        print("1) Remove old log files (older than 7 days)")
        print("2) Remove orphaned PID files")
        print("3) Clean up everything")
        print("4) Back to main menu")
        print()
        
        try:
            cleanup_choice = input("Enter your choice (1-4): ").strip()
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            return
        
        try:
            if cleanup_choice == '1':
                self.print_status("Removing log files older than 7 days...")
                count = 0
                week_ago = time.time() - (7 * 24 * 60 * 60)
                
                for log_file in self.log_dir.glob("*.log"):
                    try:
                        if log_file.stat().st_mtime < week_ago:
                            log_file.unlink()
                            count += 1
                    except OSError:
                        pass
                
                self.print_success(f"Removed {count} old log files.")
            
            elif cleanup_choice == '2':
                self.print_status("Removing orphaned PID files...")
                count = 0
                
                for pid_file in self.pid_dir.glob("*.pid"):
                    try:
                        with open(pid_file, 'r') as f:
                            pid = int(f.read().strip())
                        
                        if not psutil.pid_exists(pid):
                            pid_file.unlink()
                            count += 1
                    except (ValueError, IOError):
                        pid_file.unlink()  # Remove invalid PID files
                        count += 1
                
                self.print_success(f"Removed {count} orphaned PID files.")
            
            elif cleanup_choice == '3':
                self.print_warning("This will remove all logs and PID files!")
                confirm = input("Are you sure? (y/N): ").strip().lower()
                if confirm == 'y' or confirm == 'yes':
                    log_count = len(list(self.log_dir.glob("*.log")))
                    pid_count = len(list(self.pid_dir.glob("*.pid")))
                    
                    for log_file in self.log_dir.glob("*.log"):
                        try:
                            log_file.unlink()
                        except OSError:
                            pass
                    
                    for pid_file in self.pid_dir.glob("*.pid"):
                        try:
                            pid_file.unlink()
                        except OSError:
                            pass
                    
                    self.print_success(f"Removed {log_count} log files and {pid_count} PID files.")
                else:
                    self.print_status("Cleanup cancelled.")
            
            elif cleanup_choice == '4':
                return
            else:
                self.print_error("Invalid choice.")
        
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
    
    def quick_start(self):
        """Quick start server in current directory"""
        try:
            port = self.find_available_port(self.default_port)
            current_dir = Path.cwd()
            
            self.print_status(f"Quick starting server in {current_dir} on port {port}...")
            
            # Open browser after a short delay
            import threading
            def open_browser_delayed():
                time.sleep(2)
                try:
                    webbrowser.open(f"http://localhost:{port}")
                except Exception as e:
                    self.print_error(f"Could not open browser: {e}")
            
            threading.Thread(target=open_browser_delayed, daemon=True).start()
            
            self.print_success(f"Server starting on http://localhost:{port} (opening browser)...")
            self.print_status("Press Ctrl+C to stop")
            print("─" * 45)
            
            cmd = [sys.executable, '-m', 'http.server', str(port)]
            try:
                subprocess.run(cmd)
            except KeyboardInterrupt:
                print("\nServer stopped by user")
        
        except Exception as e:
            self.print_error(f"Failed to start server: {e}")
    
    def show_menu(self):
        """Display main menu"""
        print()
        print("╔══════════════════════════════════════════════╗")
        print("║        Python HTTP Server Manager            ║")
        print("╠══════════════════════════════════════════════╣")
        print("║  1) Start new server                         ║")
        print("║  2) Show running servers                     ║")
        print("║  3) Stop servers                             ║")
        print("║  4) Restart servers                          ║")
        print("║  5) View server logs                         ║")
        print("║  6) Open server in browser                   ║")
        print("║  7) Show statistics                          ║")
        print("║  8) Cleanup logs and PIDs                    ║")
        print("║  9) Quick start (current dir, port 8000)     ║")
        print("║  0) Exit                                     ║")
        print("╚══════════════════════════════════════════════╝")
        print()
    
    def restart_servers(self):
        """Restart servers (simplified implementation)"""
        print()
        self.print_status("=== RESTART PYTHON HTTP SERVERS ===")
        print()
        self.print_status("Restart functionality: Stop the desired server and start a new one.")
        self.print_status("This ensures clean restart with your preferred settings.")
        print()
        
        if self.show_running_servers():
            print()
            self.print_question("Would you like to stop servers first? (y/N): ")
            try:
                choice = input().strip().lower()
                if choice == 'y' or choice == 'yes':
                    self.stop_servers()
            except KeyboardInterrupt:
                print("\nOperation cancelled.")
    
    def run(self):
        """Main application loop"""
        print()
        print("╔══════════════════════════════════════════════╗")
        print("║        Python HTTP Server Manager            ║")
        print("║              Welcome!                        ║")
        print(f"║            Platform: {platform.system():<18}        ║")
        print("╚══════════════════════════════════════════════╝")
        
        # Check Python availability
        if not self.check_python():
            return 1
        
        # Check for command line arguments
        if len(sys.argv) > 1:
            arg = sys.argv[1].lower()
            if arg in ['quick', 'q']:
                self.quick_start()
                return 0
            elif arg in ['start', 's']:
                self.start_server()
                return 0
            elif arg == 'stop':
                self.stop_servers()
                return 0
            elif arg in ['status', 'list', 'ls']:
                self.show_running_servers()
                return 0
            elif arg in ['help', 'h', '--help']:
                print("Usage: python server_manager.py [command]")
                print("Commands:")
                print("  quick, q    - Quick start server in current directory")
                print("  start, s    - Interactive server start")
                print("  stop        - Stop servers")
                print("  status, ls  - Show running servers")
                print("  help, h     - Show this help")
                return 0
        
        # Interactive menu loop
        try:
            while True:
                self.show_menu()
                try:
                    choice = input("Enter your choice (0-9): ").strip()
                except KeyboardInterrupt:
                    print("\nExiting...")
                    break
                
                if choice == '1':
                    self.start_server()
                elif choice == '2':
                    self.show_running_servers()
                elif choice == '3':
                    self.stop_servers()
                elif choice == '4':
                    self.restart_servers()
                elif choice == '5':
                    self.view_logs()
                elif choice == '6':
                    self.open_in_browser()
                elif choice == '7':
                    self.show_statistics()
                elif choice == '8':
                    self.cleanup()
                elif choice == '9':
                    self.quick_start()
                elif choice == '0':
                    self.print_success("Thank you for using Python HTTP Server Manager!")
                    break
                else:
                    self.print_error("Invalid choice. Please try again.")
                
                if choice != '0':
                    print()
                    try:
                        input("Press Enter to continue...")
                    except KeyboardInterrupt:
                        print("\nExiting...")
                        break
        
        except KeyboardInterrupt:
            print("\nExiting...")
        
        return 0

def main():
    """Main entry point"""
    try:
        manager = ServerManager()
        return manager.run()
    except KeyboardInterrupt:
        print("\nExiting...")
        return 0
    except Exception as e:
        print(f"Fatal error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
