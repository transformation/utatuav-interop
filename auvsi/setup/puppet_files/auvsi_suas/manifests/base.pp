# AUVSI SUAS Puppet Module: base
# Base, core system setup
# ==============================================================================

# Should be required by anything that needs to install or use packages
class auvsi_suas::base {
    require auvsi_suas::apt_sources

    # Install python and pip
    class { 'python' :
        version => 'system',
        pip => true,
        virtualenv => true,
    }

    # Some core programs
    $package_deps = [
        "ntp",
        "openssh-client",
        "openssh-server",
        "rsync",
        "vim",
        "git",
        # The Puppet Python class can't actually handle installing multiple
        # versions of Python, so we handle Python 3 ourselves.
        "python3",
        "python3-pip",
    ]
    package { $package_deps:
        ensure => "latest",
    }

    # Ubuntu 14.04 comes with a broken virtualenv, so it must be installed
    # from pip. Better yet, python::pip can't use a non-system (i.e., Python 2)
    # version of pip outside of a virtualenv, so we must install with a manual
    # command.
    exec { 'install virtualenv-3.4' :
        command => 'pip3 install --upgrade virtualenv',
        user => root,
        require => Package['python3-pip'],
    }
}
