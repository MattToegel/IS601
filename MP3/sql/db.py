from enum import Enum
import mysql.connector
from mysql.connector import Error
import json

class CRUD(Enum):
    CREATE = 1,
    READ = 2,
    UPDATE = 3,
    DELETE = 4,
    ALTER = 5


class DBResponse:
    def __init__(self, status, row=None, rows=None, insert_id=None):
        self.status = status
        if row is not None:
            self.row = row
        else:
            self.row = None
        if rows is not None:
            self.rows = rows
        else:
            self.rows = []
        self.insert_id = insert_id

    def __str__(self):
        return json.dumps(self.__dict__)


class DB:
    db = None
    debug = False

    def __runQuery(op, isMany, queryString, args=None):
        response = None
        try:
            db = DB.getDB()
            # cursor = db.cursor(dictionary=True)
            cursor = db.cursor(prepared=True, dictionary=True)
            status = False
            if DB.debug:
                print(f"db.py query {queryString}")
                print(f"db.py args {args}")
            if not isMany or op == CRUD.READ:
                if args is not None and len(args) > 0:
                    if type(args[0]) is dict:
                        args = {k: v for d in args for k, v in d.items()}
                    status = cursor.execute(queryString, args)
                    if status is None:
                        status = True
                else:
                    status = cursor.execute(queryString)
                    #print(f"status is {status}")
                    status = True
            else:
                if args is not None and len(args) > 0:
                    status = cursor.executemany(queryString, args)
                    if status is None:
                        status = True
                else:
                    status = cursor.executemany(queryString)
                    if status is None:
                        status = True
            if op == CRUD.READ:
                if not isMany:
                    result = cursor.fetchone()
                    status = True if status >= 0 else False
                    
                    response = DBResponse(status=status, row=result)
                else:
                    result = cursor.fetchall()
                    status = True if status >= 0 else False
                    response = DBResponse(status=status, rows=result)
            else:
                if op != CRUD.ALTER:
                    if not db.autocommit:
                        db.commit()
                status = True if status >= 0 else False
                insert_id = DB.db.fetch_eof_status()["insert_id"]
                response = DBResponse(status=status, insert_id=insert_id)
            if op != CRUD.READ:
                # Get the number of rows affected
                rows_affected = cursor.rowcount
                print(f'db.py {op} {rows_affected} rows affected')
            try:
                cursor.close()
            except Exception as ce:
                print("cursor close error", ce)

        except Error as e:
            print(f"Error {e}")
            if e.errno == 2006:  # MySQL server has gone away
                DB.close()
            raise Exception(e)
        return response

    @staticmethod
    def delete(queryString, *args):
        return DB.__runQuery(CRUD.DELETE, False, queryString, args)
        
    @staticmethod
    def update(queryString, *args):
        return DB.__runQuery(CRUD.UPDATE, False, queryString, args)

    @staticmethod
    def query(queryString):
        if "CREATE TABLE" in queryString.upper():
            return DB.__runQuery(CRUD.CREATE, False, queryString)
        elif queryString.upper().startswith("ALTER"):
            return DB.__runQuery(CRUD.ALTER, False, queryString)
        else:
            return DB.__runQuery(CRUD.ALTER, False, queryString)

    @staticmethod
    def insertMany(queryString, data):
        return DB.__runQuery(CRUD.CREATE, True, queryString, data)

    @staticmethod
    def insertOne(queryString, *args):
        return DB.__runQuery(CRUD.CREATE, False, queryString, args)

    @staticmethod
    def selectAll(queryString, *args):
        return DB.__runQuery(CRUD.READ, True, queryString, args)

    @staticmethod
    def selectOne(queryString, *args):
        return DB.__runQuery(CRUD.READ, False, queryString, args)
    
    @staticmethod
    def close():
        try:
            DB.db.close()
        except:
            pass
        DB.db = None

    @staticmethod
    def getDB():
        if DB.db is None or not DB.db.is_connected():
            import os
            import re
            from dotenv import load_dotenv
            load_dotenv()
            db_url = os.environ.get("DB_URL")
            from urllib.parse import urlparse
            url = urlparse(db_url)
            if url:
                user = url.username
                password = url.password
                host = url.hostname
                port = url.port
                database = url.path.strip("/")
                try:
                    DB.db = mysql.connector.connect(
                        host=host, user=user, password=password, database=database, port=int(port))
                except Error as e:
                    print("Error while connecting to MySQL", e)
                    raise e
            else:  # old logic as fallback
                data = re.findall(
                    "mysql://(\w+):(\w+)@([\w\.]+):([\d]+)/([\w]+)", db_url)
                if len(data) > 0:
                    data = data[0]
                    if len(data) >= 5:
                        try:
                            user, password, host, port, database = data
                            DB.db = mysql.connector.connect(
                                host=host, user=user, password=password, database=database, port=int(port))
                        except Error as e:
                            print("Error while connecting to MySQL", e)
                            raise e
                    else:
                        raise Exception("Missing connection details")
                else:
                    raise Exception("Invalid connection string")
        # enable autocommit (quick fix for common issues)
        if DB.db:
            DB.db.autocommit = True
        return DB.db

if __name__ == "__main__":
    # verifies connection works
    print(DB.selectOne("SELECT 'test' from dual"))
