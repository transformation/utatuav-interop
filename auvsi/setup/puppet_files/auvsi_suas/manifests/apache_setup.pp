# AUVSI SUAS Puppet Module: apache_setup
# Configures Apache server to use WSGI and point at auvsi_suas server.
# ==============================================================================

class auvsi_suas::apache_setup {
    require auvsi_suas::base

    # Install additional utils and modules
    $package_deps = [
        "apache2-utils",
        "libapache2-mod-auth-pgsql",
        "libapache2-mod-auth-plain",
        "libapache2-mod-python",
        "libapache2-mod-wsgi",
    ]
    package { $package_deps:
        ensure => "latest",
    }

    # Configure apache defaults
    class { 'apache':
        default_vhost => false,
        service_ensure => running,
    }

    # Configure the python path
    class { 'apache::mod::wsgi':
        wsgi_python_home   => '/interop/server/venv/',
        wsgi_python_path   => '/interop/server/:/interop/server/venv/lib/python2.7/site-packages/',
    }

    # xsendfile will be used to serve uploaded files
    apache::mod { 'xsendfile': }

    # xsendfile configuration
    file { '/etc/apache2/conf.d/xsendfile.conf' :
        content => "XSendFile On\nXSendFilePath /var/www/media",
    }

    # Limit uploads to 1MB
    file { '/etc/apache2/conf.d/limit_upload.conf' :
        content => "LimitRequestBody 1048576",
    }

    # Configure production via WSGI
    apache::vhost { 'interop_server':
        port => '80',
        docroot => '/var/www/',
        wsgi_application_group => '%{GLOBAL}',
        wsgi_daemon_process => 'wsgi',
        wsgi_daemon_process_options => {
            processes => '4',
            threads => '6',
            display-name => '%{GROUP}',
        },
        wsgi_import_script => '/interop/server/server/wsgi.py',
        wsgi_import_script_options  =>
            { process-group => 'wsgi', application-group => '%{GLOBAL}' },
        wsgi_process_group => 'wsgi',
        wsgi_script_aliases => {
            '/' => '/interop/server/server/wsgi.py'
        },
        aliases => [
            { alias => '/static',
              path => '/interop/server/auvsi_suas/static',
            },
        ],
        additional_includes => [
            '/etc/apache2/conf.d/xsendfile.conf',
            '/etc/apache2/conf.d/limit_upload.conf',
        ],
        require => [
            File['/etc/apache2/conf.d/xsendfile.conf'],
            File['/etc/apache2/conf.d/limit_upload.conf'],
        ],
    }

    # Ensure media directory exists
    file { '/var/www/media' :
        ensure => 'directory',
        owner => 'www-data',
        mode => '0644',
    }
}
