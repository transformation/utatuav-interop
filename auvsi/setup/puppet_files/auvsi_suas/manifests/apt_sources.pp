# AUVSI SUAS Puppet Module: apt_sources
# Enable all standard Ubuntu repos: main restricted universe multiverse
# ==============================================================================

# apt_sources module definition
class auvsi_suas::apt_sources {
    include apt

    apt::source { "ubuntu_trusty":
        location        => "http://archive.ubuntu.com/ubuntu/",
        release         => "trusty",
        repos           => "main restricted universe multiverse",
    }

    apt::source { "ubuntu_trusty-updates":
        location        => "http://archive.ubuntu.com/ubuntu/",
        release         => "trusty-updates",
        repos           => "main restricted universe multiverse",
    }

    apt::source { "ubuntu_trusty-security":
        location        => "http://archive.ubuntu.com/ubuntu/",
        release         => "trusty-security",
        repos           => "main restricted universe multiverse",
    }
}
