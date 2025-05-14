Налаштування опен впн(Для чайників)

# first docker compose run --rm openvpn ovpn_genconfig -u udp://VPN.SERVER.IP
# second docker compose run --rm openvpn ovpn_initpki
# third docker-compose up -d
# Fourth docker compose run --rm openvpn ovpn_initpki

# Для створення різних клієнтів docker compose run --rm openvpn ovpn_getclient client1 > client1.ovpn
# Для перевірки docker compose exec openvpn ls /etc/openvpn/pki/issued

