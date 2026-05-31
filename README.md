# SANTOSO-GRID

Professional Mass Mailing Tool with Web Dashboard - 5000 emails/hour

![Version](https://img.shields.io/badge/version-1.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![Ubuntu](https://img.shields.io/badge/Ubuntu-24.04-orange)

---

## 📋 Features

### Core Features
- **Mass Email Sending** - Send up to 5000 emails/hour
- **Web Dashboard** - Modern web interface for campaign management
- **Live Monitoring** - Real-time tracking of sent/failed emails
- **Multi-Threading** - Fast parallel sending with threading
- **Background Processing** - Campaigns survive browser close

### Advanced Features
- **Proxy Support** - HTTP, SOCKS4, SOCKS5 proxy rotation
- **Proxy Checker** - Built-in proxy validation tool
- **Maillist Filter** - Filter emails by domain
- **Template Manager** - Save and reuse email templates
- **Telegram Notifications** - Get reports via Telegram bot

### Anti-Detection
- **Header Randomization** - Random Message-ID, X-Mailer headers
- **Content Obfuscation** - Invisible characters to avoid spam filters
- **Random Delays** - Variable delays between sends
- **Proxy Rotation** - Change IP every 500 emails

---

## 🚀 Installation

### Prerequisites
- Ubuntu 24/22/20/18 VPS
- Root access
- Python 3.11+

### Quick Install

```bash
# 1. Upload the project to your VPS
cd /opt
git clone https://github.com/hamzaswork00/SANTOSO-GRID.git
cd SANTOSO-GRID

# 2. Run the installer
chmod +x installer/install.sh
sudo bash installer/install.sh

# 3. Configure Telegram (optional)
nano config/.env

# 4. Start the service
sudo systemctl start santosogrid
sudo systemctl enable santosogrid