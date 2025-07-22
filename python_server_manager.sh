#!/bin/bash

# Interactive Python HTTP Server Manager
# Author: Created for streamlined Python server management
# Description: Manages python3 -m http.server instances with interactive prompts

set -e  # Exit on any error

# Colors for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Default settings
DEFAULT_PORT=8000
SERVER_LOG_DIR="$HOME/.python_server_logs"
PID_FILE_DIR="$HOME/.python_server_pids"

# Create necessary directories
mkdir -p "$SERVER_LOG_DIR"
mkdir -p "$PID_FILE_DIR"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_question() {
    echo -e "${BLUE}[QUESTION]${NC} $1"
}

print_server() {
    echo -e "${CYAN}[SERVER]${NC} $1"
}

print_success() {
    echo -e "${PURPLE}[SUCCESS]${NC} $1"
}

# Function to check if Python 3 is available
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed or not in PATH."
        exit 1
    fi
    
    python_version=$(python3 --version)
    print_status "Using $python_version"
}

# Function to find available port
find_available_port() {
    local start_port=$1
    local port=$start_port
    
    while netstat -an | grep -q ":$port "; do
        ((port++))
    done
    
    echo $port
}

# Function to check if port is in use
is_port_in_use() {
    local port=$1
    netstat -an | grep -q ":$port "
}

# Function to get running Python servers
get_running_servers() {
    ps aux | grep "http.server" | grep -v grep
}

# Function to get server info by PID
get_server_info() {
    local pid=$1
    if kill -0 "$pid" 2>/dev/null; then
        ps -p "$pid" -o pid,ppid,command --no-headers 2>/dev/null
    fi
}

# Function to show running servers
show_running_servers() {
    print_status "Checking for running Python HTTP servers..."
    echo
    
    local servers=$(get_running_servers)
    if [[ -z "$servers" ]]; then
        print_warning "No running Python HTTP servers found."
        return 1
    fi
    
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    Running Python Servers                   ║"
    echo "╠══════════════════════════════════════════════════════════════╣"
    echo "$servers" | while read -r line; do
        local pid=$(echo "$line" | awk '{print $2}')
        local port=$(echo "$line" | grep -o "[0-9]\{4,5\}" | tail -1)
        
        # Get the working directory using lsof (more reliable)
        local dir=$(lsof -p "$pid" 2>/dev/null | grep cwd | awk '{print $9}' || echo "Unknown")
        
        # If lsof fails, try to extract from the command line (fallback)
        if [[ "$dir" == "Unknown" ]]; then
            dir=$(echo "$line" | awk '{for(i=11;i<=NF;i++) printf "%s ", $i; print ""}' | sed 's/.*http.server [0-9]* *//' | sed 's/^ *//' || echo "Unknown")
        fi
        
        # Truncate directory path if too long, show basename if needed
        if [[ ${#dir} -gt 25 ]]; then
            dir="...$(basename "$dir")"
        fi
        
        printf "║ PID: %-6s Port: %-6s Directory: %-25s ║\n" "$pid" "$port" "${dir:0:25}"
    done
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo
    return 0
}

# Function to start a new server
start_server() {
    echo
    print_status "=== START NEW PYTHON HTTP SERVER ==="
    
    # Get directory
    local current_dir=$(pwd)
    print_status "Current directory: $current_dir"
    echo
    print_question "Where would you like to serve files from?"
    echo "1) Current directory ($current_dir)"
    echo "2) Specify different directory"
    echo "3) Home directory ($HOME)"
    echo "4) Desktop ($HOME/Desktop)"
    echo
    read -p "Enter your choice (1-4): " dir_choice
    
    local serve_dir="$current_dir"
    case $dir_choice in
        2)
            read -p "Enter directory path: " custom_dir
            if [[ -d "$custom_dir" ]]; then
                serve_dir="$custom_dir"
            else
                print_error "Directory does not exist: $custom_dir"
                return 1
            fi
            ;;
        3)
            serve_dir="$HOME"
            ;;
        4)
            serve_dir="$HOME/Desktop"
            ;;
    esac
    
    # Get port
    echo
    print_question "What port would you like to use?"
    echo "1) Default port (8000)"
    echo "2) Find next available port starting from 8000"
    echo "3) Specify custom port"
    echo "4) Random available port (8000-9000)"
    echo
    read -p "Enter your choice (1-4): " port_choice
    
    local port=$DEFAULT_PORT
    case $port_choice in
        2)
            port=$(find_available_port $DEFAULT_PORT)
            print_status "Found available port: $port"
            ;;
        3)
            read -p "Enter port number: " custom_port
            if [[ "$custom_port" =~ ^[0-9]+$ ]] && [ "$custom_port" -ge 1024 ] && [ "$custom_port" -le 65535 ]; then
                if is_port_in_use "$custom_port"; then
                    print_error "Port $custom_port is already in use."
                    return 1
                fi
                port="$custom_port"
            else
                print_error "Invalid port number. Must be between 1024 and 65535."
                return 1
            fi
            ;;
        4)
            local random_start=$((RANDOM % 1000 + 8000))
            port=$(find_available_port $random_start)
            print_status "Selected random available port: $port"
            ;;
    esac
    
    # Check if port is already in use
    if is_port_in_use "$port"; then
        print_error "Port $port is already in use."
        return 1
    fi
    
    # Additional options
    echo
    print_question "Additional server options:"
    echo "1) Start server normally"
    echo "2) Start server and open in default browser"
    echo "3) Start server in background with logging"
    echo "4) Start server with custom bind address"
    echo
    read -p "Enter your choice (1-4): " option_choice
    
    local bind_address=""
    local open_browser=false
    local background=false
    local log_file=""
    
    case $option_choice in
        2)
            open_browser=true
            ;;
        3)
            background=true
            log_file="$SERVER_LOG_DIR/server_${port}_$(date +%Y%m%d_%H%M%S).log"
            ;;
        4)
            read -p "Enter bind address (default: localhost): " custom_bind
            if [[ -n "$custom_bind" ]]; then
                bind_address="--bind $custom_bind"
            fi
            ;;
    esac
    
    # Start the server
    print_status "Starting Python HTTP server..."
    print_server "Directory: $serve_dir"
    print_server "Port: $port"
    print_server "URL: http://localhost:$port"
    
    cd "$serve_dir"
    
    if $background; then
        print_status "Starting server in background with logging..."
        nohup python3 -m http.server $port $bind_address > "$log_file" 2>&1 &
        local pid=$!
        echo "$pid" > "$PID_FILE_DIR/server_${port}.pid"
        print_success "Server started in background with PID: $pid"
        print_status "Log file: $log_file"
    else
        if $open_browser; then
            print_status "Starting server and opening browser..."
            # Open browser after a short delay
            (sleep 2 && open "http://localhost:$port") &
        fi
        
        print_success "Server starting... Press Ctrl+C to stop"
        echo "─────────────────────────────────────────────"
        python3 -m http.server $port $bind_address
    fi
}

# Function to stop servers
stop_servers() {
    echo
    print_status "=== STOP PYTHON HTTP SERVERS ==="
    
    if ! show_running_servers; then
        return 1
    fi
    
    echo
    print_question "How would you like to stop servers?"
    echo "1) Stop specific server by PID"
    echo "2) Stop specific server by port"
    echo "3) Stop all Python HTTP servers"
    echo "4) Back to main menu"
    echo
    read -p "Enter your choice (1-4): " stop_choice
    
    case $stop_choice in
        1)
            read -p "Enter PID to stop: " pid
            if [[ "$pid" =~ ^[0-9]+$ ]]; then
                if kill -0 "$pid" 2>/dev/null; then
                    kill "$pid"
                    print_success "Server with PID $pid stopped."
                    # Clean up PID file
                    find "$PID_FILE_DIR" -name "server_*.pid" -exec grep -l "$pid" {} \; -delete 2>/dev/null
                else
                    print_error "No process found with PID $pid."
                fi
            else
                print_error "Invalid PID format."
            fi
            ;;
        2)
            read -p "Enter port number: " port
            local pid=$(lsof -ti:$port 2>/dev/null | head -1)
            if [[ -n "$pid" ]]; then
                kill "$pid"
                print_success "Server on port $port (PID: $pid) stopped."
                rm -f "$PID_FILE_DIR/server_${port}.pid"
            else
                print_error "No server found on port $port."
            fi
            ;;
        3)
            print_warning "This will stop ALL Python HTTP servers!"
            read -p "Are you sure? (y/N): " confirm
            if [[ "$confirm" =~ ^[Yy]$ ]]; then
                pkill -f "http.server" && print_success "All Python HTTP servers stopped." || print_warning "No servers were running."
                rm -f "$PID_FILE_DIR"/server_*.pid
            else
                print_status "Operation cancelled."
            fi
            ;;
        4)
            return 0
            ;;
        *)
            print_error "Invalid choice."
            ;;
    esac
}

# Function to restart servers
restart_servers() {
    echo
    print_status "=== RESTART PYTHON HTTP SERVERS ==="
    
    if ! show_running_servers; then
        print_status "No servers to restart. Would you like to start a new server?"
        read -p "(y/N): " start_new
        if [[ "$start_new" =~ ^[Yy]$ ]]; then
            start_server
        fi
        return 0
    fi
    
    echo
    print_question "How would you like to restart?"
    echo "1) Restart specific server by PID"
    echo "2) Restart specific server by port"
    echo "3) Restart all servers"
    echo "4) Back to main menu"
    echo
    read -p "Enter your choice (1-4): " restart_choice
    
    case $restart_choice in
        1)
            read -p "Enter PID to restart: " pid
            if [[ "$pid" =~ ^[0-9]+$ ]] && kill -0 "$pid" 2>/dev/null; then
                local server_info=$(ps -p "$pid" -o command --no-headers)
                local port=$(echo "$server_info" | grep -o "[0-9]\{4,5\}")
                local dir=$(lsof -p "$pid" 2>/dev/null | grep cwd | awk '{print $9}')
                
                kill "$pid"
                sleep 1
                
                if [[ -n "$port" && -n "$dir" ]]; then
                    cd "$dir"
                    nohup python3 -m http.server "$port" > "$SERVER_LOG_DIR/server_${port}_$(date +%Y%m%d_%H%M%S).log" 2>&1 &
                    local new_pid=$!
                    echo "$new_pid" > "$PID_FILE_DIR/server_${port}.pid"
                    print_success "Server restarted with new PID: $new_pid"
                else
                    print_error "Could not determine server configuration for restart."
                fi
            else
                print_error "Invalid or non-existent PID."
            fi
            ;;
        2)
            read -p "Enter port number: " port
            local pid=$(lsof -ti:$port 2>/dev/null | head -1)
            if [[ -n "$pid" ]]; then
                local dir=$(lsof -p "$pid" 2>/dev/null | grep cwd | awk '{print $9}')
                kill "$pid"
                sleep 1
                
                cd "$dir"
                nohup python3 -m http.server "$port" > "$SERVER_LOG_DIR/server_${port}_$(date +%Y%m%d_%H%M%S).log" 2>&1 &
                local new_pid=$!
                echo "$new_pid" > "$PID_FILE_DIR/server_${port}.pid"
                print_success "Server on port $port restarted with new PID: $new_pid"
            else
                print_error "No server found on port $port."
            fi
            ;;
        3)
            print_warning "This will restart ALL Python HTTP servers!"
            read -p "Are you sure? (y/N): " confirm
            if [[ "$confirm" =~ ^[Yy]$ ]]; then
                print_status "Stopping all servers..."
                pkill -f "http.server"
                sleep 2
                print_status "This feature requires manual reconfiguration of each server."
                print_status "Please use the start server option to create new servers."
            else
                print_status "Operation cancelled."
            fi
            ;;
        4)
            return 0
            ;;
        *)
            print_error "Invalid choice."
            ;;
    esac
}

# Function to view server logs
view_logs() {
    echo
    print_status "=== VIEW SERVER LOGS ==="
    
    local logs=($(ls -t "$SERVER_LOG_DIR"/*.log 2>/dev/null || true))
    
    if [[ ${#logs[@]} -eq 0 ]]; then
        print_warning "No log files found in $SERVER_LOG_DIR"
        return 1
    fi
    
    echo "Available log files:"
    for i in "${!logs[@]}"; do
        local log_file=$(basename "${logs[$i]}")
        local log_date=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M" "${logs[$i]}" 2>/dev/null || echo "Unknown")
        printf "%d) %s (Created: %s)\n" $((i+1)) "$log_file" "$log_date"
    done
    
    echo
    read -p "Enter log number to view (or 'q' to quit): " log_choice
    
    if [[ "$log_choice" == "q" ]]; then
        return 0
    fi
    
    if [[ "$log_choice" =~ ^[0-9]+$ ]] && [[ $log_choice -ge 1 ]] && [[ $log_choice -le ${#logs[@]} ]]; then
        local selected_log="${logs[$((log_choice-1))]}"
        print_status "Viewing log: $(basename "$selected_log")"
        echo "─────────────────────────────────────────────"
        tail -n 50 "$selected_log"
        echo "─────────────────────────────────────────────"
        echo
        read -p "Press Enter to continue or 'f' to follow log: " follow_choice
        if [[ "$follow_choice" == "f" ]]; then
            tail -f "$selected_log"
        fi
    else
        print_error "Invalid selection."
    fi
}

# Function to open server in browser
open_in_browser() {
    echo
    print_status "=== OPEN SERVER IN BROWSER ==="
    
    if ! show_running_servers; then
        return 1
    fi
    
    read -p "Enter port number to open in browser: " port
    if [[ "$port" =~ ^[0-9]+$ ]]; then
        if is_port_in_use "$port"; then
            print_status "Opening http://localhost:$port in browser..."
            open "http://localhost:$port"
            print_success "Browser opened!"
        else
            print_error "No server running on port $port."
        fi
    else
        print_error "Invalid port number."
    fi
}

# Function to show server statistics
show_statistics() {
    echo
    print_status "=== SERVER STATISTICS ==="
    echo
    
    local running_count=$(ps aux | grep "http.server" | grep -v grep | wc -l)
    local log_count=$(ls "$SERVER_LOG_DIR"/*.log 2>/dev/null | wc -l)
    local pid_count=$(ls "$PID_FILE_DIR"/*.pid 2>/dev/null | wc -l)
    
    echo "╔══════════════════════════════════════╗"
    echo "║           Server Statistics          ║"
    echo "╠══════════════════════════════════════╣"
    printf "║ Running Servers:    %-15s  ║\n" "$running_count"
    printf "║ Log Files:          %-15s  ║\n" "$log_count"
    printf "║ PID Files:          %-15s  ║\n" "$pid_count"
    printf "║ Log Directory:      %-15s  ║\n" "$(basename "$SERVER_LOG_DIR")"
    printf "║ PID Directory:      %-15s  ║\n" "$(basename "$PID_FILE_DIR")"
    echo "╚══════════════════════════════════════╝"
    echo
}

# Function to cleanup old logs and PIDs
cleanup() {
    echo
    print_status "=== CLEANUP ==="
    
    print_question "What would you like to clean up?"
    echo "1) Remove old log files (older than 7 days)"
    echo "2) Remove orphaned PID files"
    echo "3) Clean up everything"
    echo "4) Back to main menu"
    echo
    read -p "Enter your choice (1-4): " cleanup_choice
    
    case $cleanup_choice in
        1)
            print_status "Removing log files older than 7 days..."
            find "$SERVER_LOG_DIR" -name "*.log" -mtime +7 -delete 2>/dev/null
            print_success "Old log files removed."
            ;;
        2)
            print_status "Removing orphaned PID files..."
            for pid_file in "$PID_FILE_DIR"/*.pid; do
                if [[ -f "$pid_file" ]]; then
                    local pid=$(cat "$pid_file")
                    if ! kill -0 "$pid" 2>/dev/null; then
                        rm "$pid_file"
                        print_status "Removed orphaned PID file: $(basename "$pid_file")"
                    fi
                fi
            done
            print_success "Orphaned PID files removed."
            ;;
        3)
            print_warning "This will remove all logs and PID files!"
            read -p "Are you sure? (y/N): " confirm
            if [[ "$confirm" =~ ^[Yy]$ ]]; then
                rm -f "$SERVER_LOG_DIR"/*.log 2>/dev/null
                rm -f "$PID_FILE_DIR"/*.pid 2>/dev/null
                print_success "All cleanup completed."
            else
                print_status "Cleanup cancelled."
            fi
            ;;
        4)
            return 0
            ;;
        *)
            print_error "Invalid choice."
            ;;
    esac
}

# Main menu function
show_menu() {
    echo
    echo "╔══════════════════════════════════════════════╗"
    echo "║        Python HTTP Server Manager            ║"
    echo "╠══════════════════════════════════════════════╣"
    echo "║  1) Start new server                         ║"
    echo "║  2) Show running servers                     ║"
    echo "║  3) Stop servers                             ║"
    echo "║  4) Restart servers                          ║"
    echo "║  5) View server logs                         ║"
    echo "║  6) Open server in browser                   ║"
    echo "║  7) Show statistics                          ║"
    echo "║  8) Cleanup logs and PIDs                    ║"
    echo "║  9) Quick start (current dir, port 8000)     ║"
    echo "║  0) Exit                                     ║"
    echo "╚══════════════════════════════════════════════╝"
    echo
}

# Quick start function
quick_start() {
    local port=$(find_available_port $DEFAULT_PORT)
    print_status "Quick starting server in $(pwd) on port $port..."
    
    (sleep 2 && open "http://localhost:$port") &
    print_success "Server starting on http://localhost:$port (opening browser)..."
    print_status "Press Ctrl+C to stop"
    echo "─────────────────────────────────────────────"
    python3 -m http.server $port
}

# Main function
main() {
    echo
    echo "╔══════════════════════════════════════════════╗"
    echo "║        Python HTTP Server Manager            ║"
    echo "║              Welcome!                        ║"
    echo "╚══════════════════════════════════════════════╝"
    
    # Check Python availability
    check_python
    
    # Check for command line arguments
    if [[ $# -gt 0 ]]; then
        case $1 in
            "quick"|"q")
                quick_start
                return 0
                ;;
            "start"|"s")
                start_server
                return 0
                ;;
            "stop")
                stop_servers
                return 0
                ;;
            "status"|"list"|"ls")
                show_running_servers
                return 0
                ;;
            "help"|"h"|"--help")
                echo "Usage: $0 [command]"
                echo "Commands:"
                echo "  quick, q    - Quick start server in current directory"
                echo "  start, s    - Interactive server start"
                echo "  stop        - Stop servers"
                echo "  status, ls  - Show running servers"
                echo "  help, h     - Show this help"
                echo
                return 0
                ;;
        esac
    fi
    
    # Interactive menu loop
    while true; do
        show_menu
        read -p "Enter your choice (0-9): " choice
        
        case $choice in
            1) start_server ;;
            2) show_running_servers ;;
            3) stop_servers ;;
            4) restart_servers ;;
            5) view_logs ;;
            6) open_in_browser ;;
            7) show_statistics ;;
            8) cleanup ;;
            9) quick_start ;;
            0) 
                print_success "Thank you for using Python HTTP Server Manager!"
                exit 0
                ;;
            *)
                print_error "Invalid choice. Please try again."
                ;;
        esac
        
        echo
        read -p "Press Enter to continue..."
    done
}

# Run main function
main "$@"
