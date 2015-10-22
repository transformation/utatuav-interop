# AUVSI SUAS Puppet Module: server_run
# Run the server
# ==============================================================================

class auvsi_suas::server_run {
    # Setup the server
    require auvsi_suas::server_setup
    # ... and run it with Apache
    require auvsi_suas::apache_setup
}
