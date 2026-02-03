#!/bin/bash
set -e

SMB_USERS=(
benjamin_franklin
alexander_hamilton
theodore_roosevelt
winston_churchill
florence_nightingale
eleanor_roosevelt
mother_teresa
mahatma_gandhi
socrates
plato
aristotle
hippocrates
archimedes
rene_descartes
voltaire
jean_jacques_rousseau
immanuel_kant
friedrich_nietzsche
sigmund_freud
charles_darwin
marie_antoinette
louis_xiv
peter_the_great
)

SMB_PASS="cnyrocks"
SHARE_DIR="/mnt/files"

FILES=(
amsterdam.data
berlin.data
brussels.data
data_dump_1.bin
data_dump_2.bin
data_dump_3.bin
datadump.bin
dublin.data
lisbon.data
ljubljana.data
nicosia.data
oslo.data
paris.data
prague.data
reykjavik.data
rome.data
stockholm.data
valletta.data
vilnius.data
warsaw.data
)

echo "[+] Installing Samba"
apt update
apt install -y samba smbclient

echo "[+] Creating share directory"
mkdir -p $SHARE_DIR
chmod 2777 $SHARE_DIR
chown root:sambashare $SHARE_DIR

echo "[+] Creating users"
for u in "${SMB_USERS[@]}"; do
    if ! id "$u" &>/dev/null; then
        useradd -M -s /usr/sbin/nologin "$u"
    fi

    echo -e "$SMB_PASS\n$SMB_PASS" | smbpasswd -a "$u"
    smbpasswd -e "$u"
done

echo "[+] Creating files"
for f in "${FILES[@]}"; do
    echo "NCAE SMB FILE: $f" > "$SHARE_DIR/$f"
done

chmod 666 $SHARE_DIR/*
chown root:sambashare $SHARE_DIR/*

echo "[+] Configuring Samba"

cat >/etc/samba/smb.conf <<'EOF'
[global]
   workgroup = WORKGROUP
   server string = NCAE SMB Server
   security = user
   map to guest = never
   smb ports = 445
   unix extensions = no
   disable netbios = yes

[files]
   path = /mnt/files
   browsable = yes
   writable = yes
   read only = no
   guest ok = no
   create mask = 0666
   directory mask = 2777
   force group = sambashare
EOF

echo "[+] Restarting Samba"
systemctl restart smbd
systemctl enable smbd

echo "[✓] SMB setup complete"
