import pkg_resources

from .binubuo import binubuo
from .BinubuoTemplate import BinubuoTemplate

pkgs_installed = {pkg.key for pkg in pkg_resources.working_set}

oracle_required = {'cx-oracle'}
oracle_missing = oracle_required - pkgs_installed

if oracle_missing:
    print("Oracle client not installed. Please install cx_Oracle for Oracle support.")
else:
    from .binubuoOracle import binubuoOracle

postgres_required = {'psycopg2'}
postgres_missing = postgres_required - pkgs_installed

if postgres_missing:
    # Check for binary also
    postgres_bin_required = {'psycopg2-binary'}
    postgres_bin_missing = postgres_bin_required - pkgs_installed
    if postgres_bin_missing:
        print("Postgres client not installed. Please install Psycopg2 for Postgres support.")
    else:
        from .binubuoPostgres import binubuoPostgres
else:
    from .binubuoPostgres import binubuoPostgres
