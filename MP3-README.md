You'll be implementing a basic Business Management site. \
There will be some provided files fully working as-is and some skeleton files you'll need to fill in. \
The files you need to fill in will have TODO items or comments mentioning what's expected. \
Some files will have "DO NOT EDIT" mentioned, please don't edit these. If there's a doubt about any of them ask.\
There are provided test case files too that all must be passing for full credit. Do not edit these test case files.\
If a test case isn't possible to complete, capture the failed test case locally via `pytest BusinessManagement -rA` first, then you can rename the function to `off_original_name`.\
The site will handle CRUD operations for Companies and Employees as well as allowing import of Company/Employee data via a csv file.\
Note: db.py has been updated to use pymysql instead of mysql-connector-python to aid in easier queries.\

Baseline files: https://github.com/MattToegel/IS601/tree/F23-MiniProject-3 \
May want to download branch as a zip, then copy/paste the files into your repo (if/when you do, please immediately do a git add/commit to record the baseline items)\
\
Provided files you don't need to edit:
- 000_create_table_companies.sql
- 001_create_table_employees.sql
- db.py
- init_db.py
- flash.html
- company_dropdown.html
- country_state_selector.html
- upload.html
- sort_filter.html
- all test files
- geography.py
- __init__.py (remains empty)
- Dockerfile
- main.py
- index.py
All other files likely have requirements to fill in.
