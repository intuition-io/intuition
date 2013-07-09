# -*- mode: ruby -*-
# vi: set ft=ruby :

#FIXME Wait forever the machine to boot
#BOX_NAME = ENV["BOX_NAME"] || "raring64"
#BOX_URI = ENV["BOX_URI"] || "https://cloud-images.ubuntu.com/vagrant/raring/current/raring-server-cloudimg-amd64-vagrant-disk1.box"
BOX_NAME = ENV["BOX_NAME"] || "precise64"
BOX_URI = ENV["BOX_URI"] || "http://files.vagrantup.com/precise64.box"

Vagrant.configure("2") do |config|
  config.vm.box = BOX_NAME
  config.vm.box_url = BOX_URI
  config.vm.provider :virtualbox do |vb|
    vb.customize ["modifyvm", :id, "--memory", 2048, "--cpus", 2]
  end
  config.vm.provision "shell", path: "vagrant_init.sh"
end
