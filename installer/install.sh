#!/bin/bash

# SANTOSO-GRID Auto-Installer
# Version: 1.0
# Compatible: Ubuntu 24/22/20/18

set -e

echo "🚀 Starting SANTOSO-GRID Installation..."
echo "========================================"

# Detect Ubuntu version
VERSION=$(lsb_release -rs 2>/dev/null || cat /etc/os-release | grep VERSION_ID | cut -d'"' -f2)
echo "📌 Detected Ubuntu: $VERSION"

# Update system
echo "📦 Updating system packages..."
apt update && apt upgrade -y

# Install required packages
echo "📦 Installing required packages..."
apt install -y python3 python3-pip python3-venv postfix curl wget git net-tools ufw

# Create SANTOSO-GRID directory
echo "📁 Creating SANTOSO-GRID directory..."
mkdir -p /opt/SANTOSO-GRID
cd /opt/SANTOSO-GRID

# Create Python virtual environment
echo "🐍 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install fastapi uvicorn python-multipart aiosqlite requests beautifulsoup4 python-telegram-bot

# Get server IP
SERVER_IP=$(curl -s ifconfig.me || hostname -I | awk '{print $1}')
echo "📌 Server IP: $SERVER_IP"

# Copy project files
echo "📂 Copying project files..."
cp -r backend /opt/SANTOSO-GRID/
cp -r frontend /opt/SANTOSO-GRID/
cp -r config /opt/SANTOSO-GRID/

# Configure Postfix
echo "📧 Configuring Postfix..."
bash config_postfix.sh

# Create systemd service
echo "⚙️ Creating systemd service..."
cat > /etc/systemd/system/santosogrid.service << EOF
[Unit]
Description=SANTOSO-GRID Mass Mailing Tool
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/SANTOSO-GRID
ExecStart=/opt/SANTOSO-GRID/venv/bin/python /opt/SANTOSO-GRID/backend/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
systemctl daemon-reload

# Open firewall ports
echo "🔥 Configuring firewall..."
ufw allow 25/tcp
ufw allow 5000/tcp
ufw --force enable

# Create .env file
echo "⚙️ Creating environment file..."
cp config/.env.example config/.env
sed -i "s/your_server_ip/$SERVER_IP/" config/.env

# Make scripts executable
chmod +x installer/*.sh

echo "========================================"
echo "✅ SANTOSO-GRID Installation Complete!"
echo "📌 Dashboard will be available at: http://$SERVER_IP:5000"
echo ""
echo "📝 NEXT STEPS:"
echo "1. Edit config/.env with your Telegram Bot info"
echo "2. Run: systemctl start santosogrid"
echo "3. Run: systemctl enable santosogrid"
echo ""
echo "🎯 To start the service, run:"
echo "   sudo systemctl start santosogrid"
echo "========================================"