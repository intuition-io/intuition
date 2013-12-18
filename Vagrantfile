# -*- mode: ruby -*-
# vi: set ft=ruby :

BOX_URL="http://cloud-images.ubuntu.com/vagrant/saucy/current/saucy-server-cloudimg-amd64-vagrant-disk1.box"
#BOX_URL="http://cloud-images.ubuntu.com/vagrant/raring/current/raring-server-cloudimg-amd64-vagrant-disk1.box"
BOX_NAME="saucy-server64"

Vagrant.configure("2") do |config|
  ## Choose your base box
  config.vm.box_url = BOX_URL
  config.vm.box = BOX_NAME

  ## For masterless, mount your file roots file root
  #config.vm.synced_folder "salt/roots/", "/srv/"
  config.vm.synced_folder File.dirname(__FILE__), "/home/vagrant/intuition"

  ### Set your salt configs here
  #config.vm.provision :salt do |salt|
    ### Minion config is set to ``file_client: local`` for masterless
    #salt.minion_config = "salt/minion"
    ### Installs our example formula in "salt/roots/salt"
    #salt.run_highstate = true
    #salt.verbose = true
  #end

  config.vm.provision :shell, :inline => "cd /home/vagrant/intuition && apt-get install make && make all"
end
