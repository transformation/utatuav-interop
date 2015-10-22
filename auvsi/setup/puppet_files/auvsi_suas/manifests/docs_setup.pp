# AUVSI SUAS Puppet Module: docs_setup
# Setup a virtualenv with tools for building docs.
# ==============================================================================

class auvsi_suas::docs_setup {
    require auvsi_suas::base

    python::virtualenv { '/interop/docs/venv' :
        ensure => 'present',
        version => 'system',
        requirements => '/interop/docs/requirements.txt',
    }
}
