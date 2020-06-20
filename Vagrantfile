Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/bionic64"


  config.ssh.forward_agent = true
  config.ssh.forward_x11 = true

  config.vm.provider "virtualbox" do |vb|
	  vb.cpus = 4
  end

  config.vm.provision :shell, path: "bootstrap.sh"
end
