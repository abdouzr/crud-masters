# Load environment variables from .env so Vagrant passes them to each VM provisioner
env_vars = {}
env_file = File.expand_path(".env", __dir__)
if File.exist?(env_file)
  File.readlines(env_file).each do |line|
    stripped = line.strip
    next if stripped.empty? || stripped.start_with?("#")
    key, value = stripped.split("=", 2)
    env_vars[key.strip] = value.strip if key && value
  end
end

Vagrant.configure("2") do |config|
  config.vm.define "gateway-vm" do |gateway|
    gateway.vm.box = "ubuntu/jammy64"
    gateway.vm.hostname = "gateway-vm"
    gateway.vm.network "private_network", ip: "192.168.56.10"
    gateway.vm.network "forwarded_port", guest: 3000, host: 3000
    gateway.vm.synced_folder ".", "/vagrant"
    gateway.vm.provision "shell", path: "scripts/gateway.sh", env: env_vars
  end

  config.vm.define "inventory-vm" do |inventory|
    inventory.vm.box = "ubuntu/jammy64"
    inventory.vm.hostname = "inventory-vm"
    inventory.vm.network "private_network", ip: "192.168.56.11"
    inventory.vm.network "forwarded_port", guest: 8080, host: 8080
    inventory.vm.synced_folder ".", "/vagrant"
    inventory.vm.provision "shell", path: "scripts/inventory.sh", env: env_vars
  end

  config.vm.define "billing-vm" do |billing|
    billing.vm.box = "ubuntu/jammy64"
    billing.vm.hostname = "billing-vm"
    billing.vm.network "private_network", ip: "192.168.56.12"
    billing.vm.synced_folder ".", "/vagrant"
    billing.vm.provision "shell", path: "scripts/billing.sh", env: env_vars
  end
end
