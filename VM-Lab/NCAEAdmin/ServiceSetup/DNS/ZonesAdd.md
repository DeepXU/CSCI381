# Forward zones
sudo cp /etc/bind/db.empty /etc/bind/zones/forward.team2.net
sudo cp /etc/bind/db.empty /etc/bind/zones/forward.team2.cnyhackathon.org

# Reverse zones
sudo cp /etc/bind/db.empty /etc/bind/zones/reverse.team2.net
sudo cp /etc/bind/db.empty /etc/bind/zones/reverse.cnyhackathon.org
sudo cp /etc/bind/db.empty /etc/bind/zones/reverse2.cnyhackathon.org







//
// ===============================
// FORWARD ZONES
// ===============================
//

zone "team2.net" IN {
    type master;
    file "/etc/bind/zones/forward.team2.net";
    allow-update { none; };
};

zone "team2.cnyhackathon.org" IN {
    type master;
    file "/etc/bind/zones/forward.team2.cnyhackathon.org";
    allow-update { none; };
};


//
// ===============================
// REVERSE (PTR) ZONES
// ===============================
//

// INTERNAL NETWORK (192.168.2.0/24)
zone "2.168.192.in-addr.arpa" IN {
    type master;
    file "/etc/bind/zones/reverse.team2.net";
    allow-update { none; };
};

// EXTERNAL NETWORK (172.18.13.0/24)
zone "13.18.172.in-addr.arpa" IN {
    type master;
    file "/etc/bind/zones/reverse.cnyhackathon.org";
    allow-update { none; };
};

// EXTERNAL NETWORK (172.18.14.0/24)
zone "14.18.172.in-addr.arpa" IN {
    type master;
    file "/etc/bind/zones/reverse2.cnyhackathon.org";
    allow-update { none; };
};
