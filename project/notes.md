flask-principal
jsons

403, 404 pages
roles blueprint
updated formshelpers
added dropdown nav
fixed closing table in list_sample
added updated version of db.py
renamed var in init_Db.py (not a functional change)
added roles, userroles tables and insert of admin role
updated flask_login user lookup to use sessions instead of a db call per request

[] Create points table (used for stock purchase)
[] Create "character" table represented or associated with a stock
[] CRUD operations for points/characters

Brainstorming
Characters are brokers
brokers associate to stocks (1-10 different symbols based on rarity)
Users can purchase more quantity of specific stock for a broker
stocks are like stats and will be used for battles

sum of stocks price vs high determines power %
sum of volume vs average volume determines defense %
portfolio % determines life %

How would number of shares play a role?