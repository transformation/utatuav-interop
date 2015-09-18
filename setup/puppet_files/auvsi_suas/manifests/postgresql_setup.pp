# AUVSI SUAS Puppet Module: postgresql_setup
# Configures the Postgres server.
# ==============================================================================

class auvsi_suas::postgresql_setup {
    require auvsi_suas::base

    # Setup postgresql server
    class { 'postgresql::server':
        postgres_password => 'postgresql_pass',
    }

    # Create superuser role
    postgresql::server::role { 'postgresql_user':
        password_hash => postgresql_password('postgresql_user', 'postgresql_pass'),
        superuser => true
    }

    # Create database for competition server
    postgresql::server::db { 'auvsi_suas_db':
        user => 'postgresql_user',
        password => postgresql_password('postgresql_user', 'postgresql_pass'),
    }

    # Define settings which impact performance.
    # Give the database server more memory. Should be ~1/4 of total memory.
    postgresql::server::config_entry { 'shared_buffers':
        value => '24MB',
    }
    # The effective size between server and OS. Should be ~1/2 of total memory.
    postgresql::server::config_entry { 'effective_cache_size':
        value => '1024MB',
    }
    # The number of segments (16MB) before an expensive checkpoint.
    # Increasing optimizes for write performance, decreasing for recovery time.
    # 32-256 for write-heavy application. Corresponds to ~512MB.
    postgresql::server::config_entry { 'checkpoint_segments':
        value => '32',
    }
    # The checkpoint targets finish before next one is a target percent done.
    # Larger values give server more flexibility.
    postgresql::server::config_entry { 'checkpoint_completion_target':
        value => '0.9',
    }
    # Fsync guarantees consistency of database. Synchronous commit waits for
    # flush to disk before responding to client. In this application, it is
    # safe to respond success and lose the write if server crashes.
    # Turn off for faster responses to client.
    postgresql::server::config_entry { 'synchronous_commit':
        value => 'off',
    }
}
