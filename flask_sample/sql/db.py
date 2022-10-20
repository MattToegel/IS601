from mysql.connector import Error
class DB:
    db = None

    @staticmethod
    def query(queryString):
        db = DB.getDB()
        status = False
        try:
            cursor = db.cursor()
            status = cursor.execute(queryString)
            db.commit()
        except Error as e:
            print("Error executing query", e)
        finally:
            if db.is_connected():
                cursor.close()
        return status

    @staticmethod
    def insertMany(queryString, data):
        db = DB.getDB()
        status = False
        try:
            cursor = db.cursor()
            status = cursor.executemany(queryString, data)
            db.commit()
        except Error as e:
            print("Error inserting data into MySQL table", e)
        finally:
            if db.is_connected():
                cursor.close()
        return status

    @staticmethod
    def insertOne(queryString, *args):
        db = DB.getDB()
        status = False
        try:
            cursor = db.cursor()
            status = cursor.execute(queryString, args)
            db.commit()
        except Error as e:
            print("Error inserting data into MySQL table", e)
        finally:
            if db.is_connected():
                cursor.close()
        return status


    @staticmethod
    def selectAll(queryString, *args):
        db = DB.getDB()
        rows = []
        try:
            cursor = db.cursor(dictionary=True)
            cursor.execute(queryString, args)
            rows = cursor.fetchall()
        except Error as e:
            print("Error reading data from MySQL table", e)
        finally:
            if db.is_connected():
                cursor.close()
        return rows


    @staticmethod
    def selectOne(queryString, *args):
        db = DB.getDB()
        row = ()
        try:
            cursor = db.cursor(dictionary=True)
            cursor.execute(queryString, args)
            row = cursor.fetchone()
        except Error as e:
            print("Error reading data from MySQL table", e)
        finally:
            if db.is_connected():
                cursor.close()
        return row

    @staticmethod
    def close():
        if DB.db and DB.db.is_connected:
            DB.db.close()
            DB.db = None

    @staticmethod
    def getDB():
        if DB.db is None:
            import mysql.connector
            import os
            import re
            
            db_url  = os.environ.get("DB_URL", "mysql://mt85:tCjoOsPgpNmd@db.ethereallab.app:3306/mt85")
            data = re.findall("mysql:\/\/(\w+):(\w+)@([\w\.]+):([\d]+)\/([\w]+)", db_url)
            if len(data) > 0:
                data = data[0]
                if len(data) >= 5:
                    try:
                        user,password,host,port,database = data
                        DB.db = mysql.connector.connect(host=host, user=user, password=password, database=database, port=port)
                    except Error as e:
                        print("Error while connecting to MySQL", e)
                else:
                    raise Exception("Missing connection details")
            else:
                raise Exception("Invalid connection string")
        return DB.db

if __name__ == "__main__":
    # verifies connection works
    print(DB.selectOne("SELECT 'test' from dual"))