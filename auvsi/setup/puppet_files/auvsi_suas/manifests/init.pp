# AUVSI SUAS Setup Script
# This file launches the install for the various required components
# =============================================================================

# Create the main AUVSI SUAS definition. Including this definition will
# setup all system dependencies.
class auvsi_suas {
    include auvsi_suas::server_run
    include auvsi_suas::client_install
    include auvsi_suas::docs_setup
}
