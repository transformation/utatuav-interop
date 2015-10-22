# AUVSI SUAS Puppet Setup Script
# This file launches the module install after configuring the path
# ==============================================================================

# Configure system so it can begin setup
Exec {
    # Configure the path for execution
    path => ["/bin",
             "/sbin",
             "/usr/bin",
             "/usr/sbin",
             "/usr/local/bin"],
    # Log output for setup
    logoutput => true,
}

# Execute puppet setup for AUVSI SUAS
include auvsi_suas
