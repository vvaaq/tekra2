# 🚀 OpenVPN + API — Установка и Настройка

## 📋 Обязательные условия

- 🖥️ Сервер: x86_64 Ubuntu 24.04  
- 🔑 Доступ: root  
- 🌍 Публичный IP: 100.100.100.100  
- 👤 Работайте из-под root или добавьте пользователя в группу docker.

```bash
# Перейти в root
sudo -i
```

---

## 🗺 Схема инфраструктуры

```
           🌐 Интернет
                │
        ┌───────┴────────┐
        │ Публичный IP    │
        │ 100.100.100.100 │
        └───────┬────────┘
                │
      ┌─────────▼───────────┐
      │    🖥 VPS / Ubuntu   │
      │  (🐳 Docker + Compose) │
      └─────────┬───────────┘
                │
        ┌───────▼───────┐
        │  🔐 OpenVPN    │
        │ (1194/udp)     │
        └───────┬────────┘
                │ VPN-туннель (10.8.0.0/24)
        ┌───────▼────────┐
        │  ⚙️ API (8000) │
        │  FastAPI/Uvicorn │
        └─────────────────┘
```

---

## 1️⃣ Установка Docker + Compose 🐳

```bash
apt update && apt upgrade -y
apt install -y ca-certificates curl gnupg apt-transport-https

install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg
. /etc/os-release
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $VERSION_CODENAME stable" > /etc/apt/sources.list.d/docker.list
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

---

## 2️⃣ Настройка маршрутизации и UFW+NAT 🔥

### IPv4/IPv6 форвардинг 🌐
```bash
cat >/etc/sysctl.d/99-openvpn.conf <<'EOF'
net.ipv4.ip_forward=1
net.ipv6.conf.all.forwarding=1
EOF
sysctl --system
```

### Файрвол 🛡
```bash
ufw allow OpenSSH
ufw allow 1194/udp
```

### Определение внешнего интерфейса 📡
```bash
IFACE=$(ip route get 1.1.1.1 | awk '/dev/ {print $5}'); echo "$IFACE"
```

### NAT 🔄
(Добавить блок `*nat` перед первой строкой `*filter`)
```bash
cp /etc/ufw/before.rules /etc/ufw/before.rules.bak.$(date +%s)
awk -v iface="$IFACE" 'BEGIN{p=0}
{ if(!p && $0 ~ /^\*filter/){
    print "*nat\n:POSTROUTING ACCEPT [0:0]\n-A POSTROUTING -s 10.8.0.0/24 -o " iface " -j MASQUERADE\nCOMMIT";
    p=1
  }
  print
}' /etc/ufw/before.rules > /tmp/before.rules && mv /tmp/before.rules /etc/ufw/before.rules
```

```bash
sed -i 's/^DEFAULT_FORWARD_POLICY=.*/DEFAULT_FORWARD_POLICY="ACCEPT"/' /etc/default/ufw
ufw enable
ufw reload
```

> 💡 Если у провайдера есть внешний firewall (например, Hetzner Cloud Firewall) — открой UDP/1194 на вход.

---

## 3️⃣ Клонирование репозитория и подготовка 📂
```bash
mkdir -p /root/openvpn-data
chmod 700 /root/openvpn-data

cd /root
git clone https://github.com/VladSkopenko/tekra_vpn.git
cd tekra_vpn
```

---

## 4️⃣ Обновление зависимостей 📦

### requirements.txt
❌ Удалить:
```
PyQt6==6.9.0
```
✅ Добавить:
```
uvicorn==0.27.0.post1
```
(и оставить все остальные зависимости из инструкции)

### Dockerfile
```dockerfile
ENV PIP_DEFAULT_TIMEOUT=180
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir --prefer-binary --retries 10 -r requirements.txt
```

---

## 5️⃣ Конфигурация docker-compose.yml ⚙️

### OpenVPN сервис 🔐
- NET_ADMIN  
- /dev/net/tun  
- 10.8.0.0/24  
- IPv6 форвардинг  

### API сервис ⚙️
- По умолчанию доступен только через VPN  
- Для доступа снаружи — раскомментировать публикацию порта 8000

---

## 6️⃣ Генерация конфигов 🛠

```bash
export OVPN_URL="udp://100.100.100.100"

docker run --rm -v /root/openvpn-data:/etc/openvpn kylemanna/openvpn \
  ovpn_genconfig -u "$OVPN_URL" \
  -p "redirect-gateway def1" \
  -p "route 172.17.0.0 255.255.0.0" \
  -n 1.1.1.1 -n 9.9.9.9

docker run --rm -it -v /root/openvpn-data:/etc/openvpn kylemanna/openvpn ovpn_initpki
```

📌 Проверка:
```bash
nl -ba /root/openvpn-data/openvpn.conf | sed -n '20,60p'
```

---

## 7️⃣ Сборка и запуск 🚀
```bash
docker compose build --no-cache
docker compose up -d
docker logs --tail=120 vpn_server
ss -lun | grep 1194
```

---

## 8️⃣ Создание клиента 👤

```bash
docker run --rm -it -v /root/openvpn-data:/etc/openvpn kylemanna/openvpn \
  easyrsa build-client-full client1 nopass

docker run --rm -v /root/openvpn-data:/etc/openvpn kylemanna/openvpn \
  ovpn_getclient client1 | tee /root/client1.ovpn
```

🔌 Подключение:
```bash
sudo openvpn --config /path/to/client1.ovpn
```

---

## 🎯 Готово!
Теперь у вас полностью рабочий OpenVPN-сервер с API, готовый к использованию 💪
