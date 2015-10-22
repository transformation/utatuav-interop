# AUVSI SUAS Puppet Module: server_install
# Installs suas server, plus dependencies
# ==============================================================================

class auvsi_suas::server_install {
    require auvsi_suas::base

    # Install packages from apt.
    $package_deps = [
        'python-numpy',
        'python-scipy',
        'python-matplotlib',
        'python-psycopg2',
        'npm',
    ]
    package { $package_deps:
        ensure => 'latest',
    }

    # Create server virtualenv
    python::virtualenv { '/interop/server/venv' :
        ensure => 'present',
        version => 'system',
        requirements => '/interop/server/requirements.txt',
        # We install some packages from apt since that is much faster.
        systempkgs => true,
        require => [ Package['python-numpy'], Package['python-scipy'],
                     Package['python-matplotlib'], Package['python-psycopg2'] ]
    }

    # Link NodeJS (installed as nodejs) so that Karma can use it as node.
    file { '/usr/local/bin/node':
        ensure => 'link',
        target => '/usr/bin/nodejs',
        require => Package['npm'],
    }
    # Install packages from NPM.
    exec { 'karma and jasmine':
        environment => ['HOME=/interop'],
        command => 'npm install --force -g karma karma-jasmine karma-chrome-launcher phantomjs karma-phantomjs-launcher karma-cli',
        cwd => '/interop/server',
        require => [Package['npm'], File['/usr/local/bin/node']],
    }
}
