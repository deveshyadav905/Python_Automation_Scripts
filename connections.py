from redis import Redis
from typing import Tuple,Union
from pymongo import MongoClient
from pymongo.database import Database
from elasticsearch import Elasticsearch
import mysql.connector,logging,warnings
from pymongo.collection import Collection
from mysql.connector.cursor import MySQLCursor
from mysql.connector.connection import MySQLConnection
from mysql.connector.pooling import PooledMySQLConnection
from settings import REDIS_SETTING,DB_SETTINGS,ELASTIC_SETTING,LOGGING_SETTING,REDIS_SETTING_ML

        
def get_mongo_conn(client_uri:str = DB_SETTINGS['mongo_uri'],db:str = DB_SETTINGS['mongo_db'],coll:str = None)->Tuple[MongoClient,Database,Collection]:
    try:
        mongo_client = MongoClient(client_uri)
        db_conn = mongo_client.get_database(db)
        coll_conn = db_conn.get_collection(coll)
        return (mongo_client,db_conn,coll_conn)
    except Exception as e:
        logging.error(str(e),exc_info=True)
        return None,None
    
def close_mongo_conn(mongo_client:MongoClient)->None:
    try:
        mongo_client.close()
    except Exception as e:
        newsdatafeeds_logger.error(str(e),exc_info=True)

def get_msq_conn()->Tuple[Union[PooledMySQLConnection, MySQLConnection],MySQLCursor]:
    try:
        db = mysql.connector.connect(
            host = DB_SETTINGS['mysql_host'],
            port = DB_SETTINGS['mysql_port'], 
            user = DB_SETTINGS['mysql_user'],
            password = DB_SETTINGS['mysql_password'],
            database = DB_SETTINGS['mysql_db'],
            autocommit = True
        )
        return (db,db.cursor())
    except Exception as e:
        newsdatafeeds_logger.error(str(e),exc_info=True)
        return None,None

def close_mysql_conn(db:Union[PooledMySQLConnection, MySQLConnection],cursor:MySQLCursor)->None:
    try:
        cursor.close()
        db.close()
    except Exception as e:
        newsdatafeeds_logger.error(str(e),exc_info=True)

def close_elastic_connection(els_client:Elasticsearch):
    els_client.close()
            
def get_elatic_connection(conn_type:str)->Elasticsearch:
    if conn_type == 'archive':
        return Elasticsearch(
            cloud_id=ELASTIC_SETTING['archive_cloud_id'],
            basic_auth= ("elastic",ELASTIC_SETTING['archive_els_password']),
            request_timeout=30,max_retries=1,retry_on_timeout=True
        )
    else:
        return Elasticsearch(
            cloud_id=ELASTIC_SETTING['custom_cloud_id'],
            basic_auth= ("elastic",ELASTIC_SETTING['custom_els_password']),
            request_timeout=30,max_retries=1,retry_on_timeout=True
        )
