#!/bin/bash

# SANTOSO-GRID Postfix Configuration
# Configure Postfix for direct SMTP sending (null client mode)

echo "📧 Configuring Postfix for SANTOSO-GRID..."

# Get server IP
SERVER_IP=$(curl -s ifconfig.me || hostname -I | awk '{print $1}')
HOSTNAME=$(hostname)

# Backup original main.cf
if [ -f /etc/postfix/main.cf ]; then
    cp /etc/postfix/main.cf /etc/postfix/main.cf.backup
fi

# Create new main.cf configuration
cat > /etc/postfix/main.cf << EOF
# SANTOSO-GRID Postfix Configuration
# Null Client Mode - Direct SMTP sending

# Network settings
myhostname = $HOSTNAME
mydomain = localdomain
myorigin = $mydomain
mydestination = 
relayhost = 
mynetworks = 127.0.0.0/8
inet_interfaces = all
inet_protocols = all

# Mail settings
home_mailbox = 
mailbox_command = 

# Remove all restrictions for mass mailing
smtpd_client_connection_count_limit = 1000
smtpd_client_message_rate_limit = 1000
smtpd_client_recipient_rate_limit = 1000

# Increase limits
message_size_limit = 102400000
mailbox_size_limit = 102400000

# Bypass restrictions
smtpd_relay_restrictions = permit_mynetworks, defer
smtpd_sender_restrictions = permit_mynetworks
smtpd_recipient_restrictions = permit_mynetworks

# Bind to server IP
smtp_bind_address = $SERVER_IP
smtp_address_override_source = no

# Performance settings
default_process_limit = 500
qmgr_message_active_limit = 40000
qmgr_message_recipient_limit = 40000
clone_template_write_time = 2

# Connection settings
smtp_conn_cache_on = yes
smtp_conn_cache_time = 3600s
smtp_conn_limit = 100

# Debug settings
debug_peer_list = 
debug_peer_level = 2
EOF

# Create master.cf configuration
if [ -f /etc/postfix/master.cf ]; then
    cp /etc/postfix/master.cf /etc/postfix/master.cf.backup
fi

cat > /etc/postfix/master.cf << EOF
# Postfix master process configuration
smtp      inet  n       -       y       -       500       smtpd
pickup    unix  n       -       y       60      pickup
cleanup   unix  n       -       y       0       cleanup
qmgr      unix  n       -       n       300     qmgr
tlsmgr    unix  -       -       1000?   60      tlsmgr
rewrite   unix  -       -       -       -       trivial-rewrite
bounce    unix  -       -       y       0       bounce
defer     unix  -       -       y       0       bounce
trace     unix  -       -       y       0       bounce
verify    unix  -       -       y       1       verify
flush     unix  n       -       y       1000?   flush
smtp      unix  -       -       y       -       500       smtp
relay     unix  -       -       y       -       smtp
showq     unix  n       -       y       -       showq
error     unix  -       -       y       -       error
retry     unix  -       -       y       -       error
discard   unix  -       -       y       -       discard
lmtp      unix  -       -       y       -       lmtp
anvil     unix  -       -       y       1       anvil
scache    unix  -       -       y       1       scache
postlog   unix-dgram n  -       n       1       postlogd
EOF

# Restart Postfix
echo "🔄 Restarting Postfix..."
systemctl restart postfix
systemctl enable postfix

# Check Postfix status
if systemctl is-active --quiet postfix; then
    echo "✅ Postfix is running!"
else
    echo "❌ Postfix failed to start. Check logs with: journalctl -xe"
fi

echo "✅ Postfix configuration complete!"