#!/bin/bash
echo "**** Begin installing Docker CE"

#Uninstall old versions
echo -e "\e[96mUninstalling any old versions"
echo -e "\e[0m"
sudo apt-get remove docker docker-engine docker.io containerd runc

#Set up the repository
##Update the apt package index
echo -e "\e[96mUpdating apt package index"
echo -e "\e[0m"
sudo apt-get update
echo -e "\e[96mPrepping apt to use repos over HTTPS"
echo -e "\e[0m"
##Install packages to allow apt to use a repository over HTTPS
sudo apt-get install -y apt-transport-https
sudo apt-get install -y ca-certificates wget
sudo apt-get install -y curl
sudo apt-get install -y gnupg-agent
sudo apt-get install -y software-properties-common
##Add Docker's official GPG key
echo -e "\e[96mAdding Docker's official GPG key"
echo -e "\e[0m"
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
##Set up the stable repository
echo -e "\e[96mSetting  up stable repo"
echo -e "\e[0m"
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"

#Install Docker CE
##Update the apt package index
echo -e "\e[96mUpdating apt package index after pre-setup"
echo -e "\e[0m"
sudo apt-get update
#Install a specific version of Docker CE 
sudo apt-get install -y docker-ce
#=18.06.1~ce~3-0~ubuntu
#Verify that Docker CE is installed correctly by running the hello-world image
echo -e "\e[96mVerifying docker install via hello-world"
echo -e "\e[0m"
sudo docker run hello-world
#use Docker as a non-root user
echo -e "\e[96mAdding docker group to vagrant user"
echo -e "\e[0m"
usermod -aG docker vagrant

echo "**** End installing Docker CE"
