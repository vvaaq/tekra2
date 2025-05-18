#!/bin/sh

set -e

echo "[OpenVPN INIT] Старт инициализации конфигурации..."

if [ ! -f /etc/openvpn/openvpn.conf ]; then
  echo "[OpenVPN INIT] Генерация базовой конфигурации..."
  ovpn_genconfig -u ${VPN_PROTOCOL}://${OVPN_SERVER}

  echo "[OpenVPN INIT] Инициализация PKI..."
  echo "${VPN_PKI_PASSWORD}" | ovpn_initpki nopass
else
  echo "[OpenVPN INIT] Конфигурация уже существует, пропускаем инициализацию."
fi

echo "[OpenVPN INIT] Запуск OpenVPN-сервера..."
exec ovpn_run