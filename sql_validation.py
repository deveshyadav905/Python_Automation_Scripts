import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import mysql.connector
from crawlers.settings import TEST_DB_SETTINGS,SQL_FILE_PATH
from connections import newsdatafeeds_logger,MySQLConnection,PooledMySQLConnection,Tuple,Union


def get_testdb_conn() -> Tuple[Union[PooledMySQLConnection, MySQLConnection], mysql.connector.cursor.MySQLCursor]:
    try:
        db = mysql.connector.connect(
            host=TEST_DB_SETTINGS['test_mysql_host'],
            port=TEST_DB_SETTINGS['test_mysql_port'],
            user=TEST_DB_SETTINGS['test_mysql_user'],
            password=TEST_DB_SETTINGS['test_mysql_password'],
            database=TEST_DB_SETTINGS['test_mysql_db'],
            autocommit=True
        )
        return db, db.cursor()
    except mysql.connector.Error as e:
        newsdatafeeds_logger.error(f"MySQL connection error: {e}", exc_info=True)
        return None, None
    except Exception as e:
        newsdatafeeds_logger.error(f"Unexpected error during DB connection: {e}", exc_info=True)
        return None, None

def execute_sql_file(file_path):
    db, cursor = None, None
    try:
        db, cursor = get_testdb_conn()
        if not db or not cursor:
            raise ConnectionError("Failed to establish a database connection.")

        # Read the SQL file
        with open(file_path, 'r', encoding='utf-8') as sql_file:
            sql_script = sql_file.read()

        # Execute the entire script with multi=True
        for result in cursor.execute(sql_script, multi=True):
            try:
                # Log the statement that was executed
                newsdatafeeds_logger.info(f"Executed: {result.statement.strip()[:50]}...")
            except mysql.connector.Error as e:
                newsdatafeeds_logger.error(
                    f"Error executing statement: {result.statement}\nError: {e}", exc_info=True
                )
                # Rollback on error
                db.rollback()
                newsdatafeeds_logger.er(f"Rolled back changes due to error in: {result.statement}")

        # Commit all changes
        db.commit()
    except FileNotFoundError as e:
        newsdatafeeds_logger.error(f"SQL file not found: {e}", exc_info=True)
    except mysql.connector.Error as e:
        newsdatafeeds_logger.error(f"MySQL error during execution: {e}", exc_info=True)
    except Exception as e:
        newsdatafeeds_logger.error(f"Unexpected error: {e}", exc_info=True)
    finally:
        # Close the database connection
        if cursor:
            cursor.close()
        if db:
            db.close()
if __name__ == "__main__":
    
    sql_file_path = "/home/charanjeet/Downloads/devesh1.sql"  # Path to your SQL file
    execute_sql_file(sql_file_path)
