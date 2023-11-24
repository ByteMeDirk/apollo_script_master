# Testing Postgresql
apollo_script_master --conn_params "{\"drivername\": \"postgresql\", \"dialect\": \"psycopg2\", \"host\": \"localhost\", \"port\": 5432, \"database\": \"postgres\", \"username\": \"postgres\", \"password\": \"YourPassword123!\"}" --directory "./tests/sql/postgres/*.sql" --author "ByteMeDirk"

# Testing MySQL
apollo_script_master --conn_params "{\"drivername\": \"mysql\", \"dialect\": \"pymysql\", \"host\": \"localhost\", \"port\": 3306, \"database\": \"mysql\", \"username\": \"root\", \"password\": \"YourPassword123!\"}" --directory "./tests/sql/mysql/*.sql" --author "ByteMeDirk"