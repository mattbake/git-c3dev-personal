#!/bin/bash

# ensure running as root
if [ "$(id -u)" != "0" ]; then
  exec sudo "$0" "$@"
fi

source /usr/local/osmosix/etc/userenv

if [ -z $CliqrTier_Apache_PUBLIC_IP ]; then
  exit 4
elif [ -z $CliqrTier_Database_IP ]; then
  exit 5
fi

ip route add 10.20.0.0/24 via 10.16.0.10

until ping -c1 $CliqrTier_Database_IP &>/dev/null; do :; done

cd /var/www/install
php cli_install.php install --db_driver mysqli --db_host $CliqrTier_Database_IP --db_user opencart --db_password opencart --db_name opencart --username admin --password admin --email youremail@example.com --agree_tnc yes --http_server http://$CliqrTier_Apache_PUBLIC_IP/
