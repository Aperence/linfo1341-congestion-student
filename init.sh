# Install docker
sudo dnf -y install dnf-plugins-core
sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo

sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

sudo systemctl start docker

sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker

# Install kathara
curl -OL https://github.com/KatharaFramework/Kathara/releases/download/3.7.5/kathara-3.7.5-1.fc38.x86_64.rpm
sudo rpm -U kathara-3.7.5-1.fc38.x86_64.rpm
rm kathara-3.7.5-1.fc38.x86_64.rpm
