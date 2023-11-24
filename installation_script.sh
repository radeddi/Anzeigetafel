sudo apt-get -y install nodm

# Edit nodm config file
sudo sed -i -e "s/NODM_ENABLED=false/NODM_ENABLED=true/" -e "s/NODM_USER=root/NODM_USER=$USER/" \
  /etc/default/nodm

# Create custom Xsession file
printf "%s\n" \
  "#!/usr/bin/env bash" \
  "exec openbox-session &" \
  "while true; do" \
  "  python3 $PWD/main.py" \
  "done" \
  > /home/$USER/.xsession
