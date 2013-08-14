# -*- mode: ruby -*-
# vi: set ft=ruby :

#FIXME It creates a .quantrade in this directory
#FIXME Wait forever the machine to boot
#BOX_NAME = ENV["BOX_NAME"] || "raring64"
#BOX_URI = ENV["BOX_URI"] || "https://cloud-images.ubuntu.com/vagrant/raring/current/raring-server-cloudimg-amd64-vagrant-disk1.box"
BOX_NAME = ENV["BOX_NAME"] || "quantal64"
BOX_URI = ENV["BOX_URI"] || "http://dl.dropbox.com/u/13510779/lxc-quantal-amd64-2013-07-12.box"

Vagrant.configure("2") do |config|
  config.vm.box = BOX_NAME
  config.vm.box_url = BOX_URI

  config.vm.synced_folder File.dirname(__FILE__), "/home/vagrant/ppQuanTrade"

  config.vm.provider :lxc do |lxc|
    lxc.customize 'cgroup.memory.limit_in_bytes', '1024M'
  end

  config.vm.provision :shell, :inline => "export PROJECT_URL=Gusabi/ppQuanTrade && wget -qO- https://raw.github.com/Gusabi/Dotfiles/master/utils/apt-git | bash"
  #config.vm.provision :shell, :inline => "cd /home/vagrant/ppQuanTrade && apt-get install make && make all"
end
