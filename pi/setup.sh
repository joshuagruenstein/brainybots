# pls run this as root

sudo apt-get update
sudo apt-get upgrade
sudo apt-get -y install wget python3 python3-pip python3-smbus

# Wifi setup
wget https://raw.githubusercontent.com/idev1/rpihotspot/master/setup-network.sh
chmod +x setup-network.sh
sudo ./setup-network --clean
sudo ./setup-network.sh --install --ap-ssid="$0" --ap-password="$1" --ap-password-encrypt --ap-country-code="US" --ap-ip-address="192.168.0.1"

# Python setup
sudo pip3 install --no-cache --upgrade jupyter numpy matplotlib

# Run jupyterlab on start?