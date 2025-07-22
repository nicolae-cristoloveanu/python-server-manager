#!/bin/bash

# Setup Python Server Manager in Project
# Usage: ./setup_project_server.sh /path/to/your/project

PROJECT_DIR="$1"
SCRIPT_DIR="/Users/krat05/Desktop/Code Institute/python-server-manager"
SERVER_MANAGER="$SCRIPT_DIR/python_server_manager.py"

if [ -z "$PROJECT_DIR" ]; then
    echo "Usage: $0 /path/to/your/project"
    echo "Example: $0 ~/Desktop/my-web-project"
    exit 1
fi

if [ ! -d "$PROJECT_DIR" ]; then
    echo "Error: Directory $PROJECT_DIR does not exist"
    exit 1
fi

if [ ! -f "$SERVER_MANAGER" ]; then
    echo "Error: Server manager script not found at $SERVER_MANAGER"
    exit 1
fi

cd "$PROJECT_DIR"

echo "Setting up Python Server Manager in: $PROJECT_DIR"

# Create or update .gitignore
if [ -f ".gitignore" ]; then
    echo "✓ .gitignore exists, adding server manager entries..."
    if ! grep -q "python_server_manager.py" .gitignore; then
        echo "" >> .gitignore
        echo "# Python Server Manager (local development tool)" >> .gitignore
        echo "python_server_manager.py" >> .gitignore
        echo "server_manager.py" >> .gitignore
        echo "✓ Added server manager to .gitignore"
    else
        echo "✓ Server manager already in .gitignore"
    fi
else
    echo "✓ Creating .gitignore..."
    cat << 'EOF' > .gitignore
# Python Server Manager (local development tool)
python_server_manager.py
server_manager.py

# Python
__pycache__/
*.py[cod]
*.pyc
*.pyo

# Virtual Environments
venv/
env/
.env

# IDEs
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Logs
*.log
EOF
    echo "✓ Created .gitignore"
fi

# Create symlink to server manager
if [ -f "server_manager.py" ]; then
    echo "✓ server_manager.py already exists"
else
    ln -s "$SERVER_MANAGER" server_manager.py
    echo "✓ Created symlink to server_manager.py"
fi

echo ""
echo "🎉 Setup complete! You can now use:"
echo "   python3 server_manager.py quick      # Quick start server"
echo "   python3 server_manager.py status     # Show running servers"
echo "   python3 server_manager.py           # Interactive menu"
echo ""
echo "The server manager is ignored by Git and won't be committed to your repository."
