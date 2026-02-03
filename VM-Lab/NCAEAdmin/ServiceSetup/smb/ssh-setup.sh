#!/bin/bash
set -e

SCORING_KEY='ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCcM4aDj8Y4COv+f8bd2WsrIynlbRGgDj2+q9aBeW1Umj5euxnO1vWsjfkpKnyE/ORsI6gkkME9ojAzNAPquWMh2YG+n11FB1iZl2S6yuZB7dkVQZSKpVYwRvZv2RnYDQdcVnX9oWMiGrBWEAi4jxcYykz8nunaO2SxjEwzuKdW8lnnh2BvOO9RkzmSXIIdPYgSf8bFFC7XFMfRrlMXlsxbG3u/NaFjirfvcXKexz06L6qYUzob8IBPsKGaRjO+vEdg6B4lH1lMk1JQ4GtGOJH6zePfB6Gf7rp31261VRfkpbpaDAznTzh7bgpq78E7SenatNbezLDaGq3Zra3j53u7XaSVipkW0S3YcXczhte2J9kvo6u6s094vrcQfB9YigH4KhXpCErFk08NkYAEJDdqFqXIjvzsro+2/EW1KKB9aNPSSM9EZzhYc+cBAl4+ohmEPej1m15vcpw3k+kpo1NC2rwEXIFxmvTme1A2oIZZBpgzUqfmvSPwLXF0EyfN9Lk= SCORING KEY DO NOT REMOVE'

USERS=(
camille_jenatzy
gaston_chasseloup
leon_serpollet
william_vanderbilt
henri_fournier
maurice_augieres
arthur_duray
henry_ford
louis_rigolly
pierre_caters
paul_baras
victor_hemery
fred_marriott
lydston_hornsted
kenelm_guinness
rene_thomas
ernest_eldridge
malcolm_campbell
ray_keech
john_cobb
dorothy_levitt
paula_murphy
betty_skelton
rachel_kushner
kitty_oneil
jessi_combs
andy_green
)

for u in "${USERS[@]}"; do
    if ! id "$u" &>/dev/null; then
        useradd -m -s /bin/bash "$u"
    fi

    mkdir -p /home/$u/.ssh
    echo "$SCORING_KEY" > /home/$u/.ssh/authorized_keys

    chown -R $u:$u /home/$u/.ssh
    chmod 700 /home/$u/.ssh
    chmod 600 /home/$u/.ssh/authorized_keys
done

echo "[+] SSH scoring users installed successfully"
