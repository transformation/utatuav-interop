#!/bin/bash

# This script launches the Puppet automated dependency installer.
# ==============================================================================

# Quit immediately on any error
set -e

SETUP=$(readlink -f $(dirname ${BASH_SOURCE[0]}))
REPO=$(readlink -f ${SETUP}/..)

# $1 = log message
function log() {
    local C='\033[0;32m'
    local NC='\033[0m'
    printf "${C}$1${NC}\n"
}

# $1 = module name
function ensure_puppet_module() {
    local module="$1"
    local installed=0

    if sudo puppet module list | grep -q ${module}; then
        installed=1
    fi

    if [[ ${installed} == 0 ]]; then
        sudo puppet module install ${version_arg} ${module}
    else
        log "Puppet module \"${module}\" already installed"
    fi

    sudo puppet module upgrade ${module}
}

# Create soft link from repo to standardize scripts
log "Creating softlinks..."
sudo ln -snf ${REPO} /interop

# Update the package list
log "Updating package list and upgrading packages..."
sudo apt-get -y update
# Upgrade old packages
sudo apt-get -y upgrade

# Install Puppet
log "Installing Puppet and modules..."
sudo apt-get -y install puppet
# Install puppet modules
sudo mkdir -p /etc/puppet/modules/
ensure_puppet_module puppetlabs-concat
ensure_puppet_module puppetlabs-postgresql
ensure_puppet_module puppetlabs-apache
# We explicitly use the apt module, so it is listed here.  However, the
# postgresql module currently also depends on it, so it will be automatically
# installed along with the postgresql module.  The postgresql module is not
# compatible with the latest version of the apt module, so if we install the
# apt module manually first, the postgresql module will fail to install.
ensure_puppet_module puppetlabs-apt
ensure_puppet_module stankevich-python

# Launch the Puppet process. Prepares machine.
log "Executing Puppet setup..."
sudo puppet apply --modulepath=${SETUP}/puppet_files:/etc/puppet/modules/ \
    ${SETUP}/puppet_files/auvsi_suas.pp
