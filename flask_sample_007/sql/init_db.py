import glob
import os



from db import DB
print(os.path.dirname(os.path.abspath(__file__)))
mypath = os.path.dirname(os.path.abspath(__file__))
files = glob.glob(glob.escape(mypath)+"/*.sql")
queries = []
# read .sql file contents
for f in files:
    with open(f, "r") as file:
        queries.append({
            "file": f,
            "sql": file.read()
        })
# sort in prefix order
queries = sorted(queries, key=lambda x:x["file"].lower())
# check if anything can be blocked to save query runs
tables = DB.selectAll("SHOW TABLES")
existing_tables = []
# map to a 1D array for easy checking
for t in tables:
    existing_tables.append(list(t.values())[0])

# execute sql files
for q in queries:
    sql = q["sql"]
    file = q["file"]
    print(f"Trying file: {file}")
    # block existing tables to save queries (we have a quota of 10k per hour)
    if "CREATE TABLE" in sql.upper():
        t = sql.split("(")[0] \
        .replace("CREATE TABLE","") \
        .replace("\n","") \
        .strip()
        if t in existing_tables:
            print(f"Table {t} already exists, blocking query")
            continue
    success = DB.query(sql)
    print(f"Ran {'successfully' if success else 'unsuccessfully'}")
print(f"Finished running {len(queries)} files")
DB.db.close()