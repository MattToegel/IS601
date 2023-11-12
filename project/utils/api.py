from enum import Enum
import requests
import os
import sys
# Get the parent directory of the current script (api.py)
CURR_DIR = os.path.dirname(os.path.abspath(__file__))

# Add the parent directory to the Python path
PARENT_DIR = os.path.join(CURR_DIR, "..")  # Go up one level from utils to project folder
sys.path.append(PARENT_DIR)
from dotenv import load_dotenv
from sql.db import DB  # Import the DB class from your db.py module
from datetime import datetime, timedelta

load_dotenv()

class HTTP(Enum):
    GET = 1
    POST = 2

class API:
    @staticmethod
    def _get_config(API_REF="API"):
        # Configuration keys and their meanings:
        # BASE_URL: The base URL of the API.
        # HOST: The host name to include in the request headers.
        # KEY: The API key or authentication token.
        # PARAMS_KEY_NAME: The name of the parameter to include the API key.
        # RATE_LIMIT_HEADER: The header field name for rate limit information.
        # RATE_REMAINING_HEADER: The header field name for remaining rate limit.
        # RATE_RESET_HEADER: The header field name for rate limit reset time.
        # RATE_HAS_LIMIT: Flag to indicate whether rate limit checks should be performed.
        return {
            "BASE_URL": os.environ.get(f"{API_REF}_BASE_URL", ""),
            "HOST": os.environ.get(f"{API_REF}_HOST", ""),
            "name": os.environ.get(f"{API_REF}_KEY", ""),
            "PARAMS_KEY_NAME": os.environ.get(f"{API_REF}_PARAMS_KEY_NAME", ""),
            "RATE_LIMIT_HEADER": os.environ.get(f"{API_REF}_RATE_LIMIT_HEADER", "x-ratelimit-requests-limit"),
            "RATE_REMAINING_HEADER": os.environ.get(f"{API_REF}_RATE_REMAINING_HEADER", "x-ratelimit-requests-remaining"),
            "RATE_RESET_HEADER": os.environ.get(f"{API_REF}_RATE_RESET_HEADER", "x-ratelimit-requests-reset"),
            "RATE_HAS_LIMIT": os.environ.get(f"{API_REF}_RATE_HAS_LIMIT", True)  # Default to True
        }

    @staticmethod
    def get(url, params=None, API_REF="API"):
        return API._fetch(url, params, API_REF, HTTP.GET)

    @staticmethod
    def post(url, params=None, API_REF="API"):
        return API._fetch(url, params, API_REF, HTTP.POST)

    @staticmethod
    def _fetch(url, params, API_REF, verb):
        config = API._get_config(API_REF)
        headers = {}
        if config["HOST"]:
            headers["X-RapidAPI-Host"] = config["HOST"]
            headers["X-RapidAPI-Key"] = config["name"]

        if config["PARAMS_KEY_NAME"]:
            params[config["PARAMS_KEY_NAME"]] = config["name"]

        url = config["BASE_URL"] + url

        if verb == HTTP.GET:
            response = requests.get(url, headers=headers, params=params)
        elif verb == HTTP.POST:
            response = requests.post(url, headers=headers, params=params)
        else:
            raise ValueError(f"Invalid HTTP verb: {verb}")

        # Check if RATE_HAS_LIMIT is True before updating rate limit, remaining rate, and rate limit reset time
        if config["RATE_HAS_LIMIT"]:
            API._update_rate_limit(API_REF, response)

        return response.json()

    @staticmethod
    def _update_rate_limit(API_REF, response):
        if not API._is_eligible_to_fetch(API_REF):
            raise Exception("Rate limit reached or exceeded")
        config = API._get_config(API_REF)
        rate_limit_header = config["RATE_LIMIT_HEADER"]
        rate_remaining_header = config["RATE_REMAINING_HEADER"]
        rate_limit_reset_header = config["RATE_RESET_HEADER"]

        rate_limit = int(response.headers.get(rate_limit_header, 0))
        rate_remaining = int(response.headers.get(rate_remaining_header, 0))
        rate_limit_reset_time_seconds = int(response.headers.get(rate_limit_reset_header, 0))

        # Calculate reset time based on current time and reset time in seconds
        current_time = datetime.utcnow()
        reset_time = current_time + timedelta(seconds=rate_limit_reset_time_seconds)

        # Convert reset_time to a string in the format "%Y-%m-%d %H:%M:%S"
        reset_time_str = reset_time.strftime("%Y-%m-%d %H:%M:%S")

        # Create keys for rate limit, remaining rate, and rate limit reset time
        rate_limit_key = f"{API_REF}_RATE_LIMIT"
        rate_remaining_key = f"{API_REF}_RATE_REMAINING"
        rate_limit_reset_key = f"{API_REF}_RATE_LIMIT_RESET_TIME"

        # Create a list of dictionaries with named placeholders for the values
        rate_data = [
            {"key": rate_limit_key, "value": rate_limit},
            {"key": rate_remaining_key, "value": rate_remaining},
            {"key": rate_limit_reset_key, "value": reset_time_str}
        ]

        # Create the insert or update query for the rate limit, remaining rate, and rate limit reset time
        insert_query = "INSERT INTO IS601_System_Properties (`name`, `value`) VALUES (%(key)s, %(value)s) ON DUPLICATE KEY UPDATE `value` = VALUES(value)"

        # Execute the query with the list of data
        DB.insertMany(insert_query, rate_data)

    @staticmethod
    def _check_rate_limit(API_REF):
        config = API._get_config(API_REF)
        rate_remaining_key = f"{API_REF}_RATE_REMAINING"
        rate_limit_reset_key = f"{API_REF}_RATE_LIMIT_RESET_TIME"

        # Fetch remaining rate and rate limit reset time from System_Properties table
        query = "SELECT `value` FROM IS601_System_Properties WHERE `name` IN (%s, %s) ORDER BY name desc"
        params = [rate_remaining_key,rate_limit_reset_key]

        result = DB.selectAll(query, *params)
        rows = result.rows
        if not rows:
            # no record yet, auto pass
            return True
        
        if len(rows) != 2:
            raise Exception("Incomplete rate limit data in System_Properties")
        
        rate_remaining_value = int(rows[0]["value"])
        rate_limit_reset_time_str = rows[1]["value"]

        # Convert rate limit reset time from string to datetime
        rate_limit_reset_time = datetime.strptime(rate_limit_reset_time_str, "%Y-%m-%d %H:%M:%S")

        # Check if rate limit has been exceeded
        if rate_remaining_value <= 0:
            # Rate limit exceeded
            if datetime.utcnow() < rate_limit_reset_time:
                # Rate limit reset time hasn't passed yet
                return False
            else:
                # Rate limit reset time has passed, reset rate remaining to 0
                return True

        # Rate limit not exceeded
        return True

    @staticmethod
    def _is_eligible_to_fetch(API_REF):
        return API._check_rate_limit(API_REF)


if __name__ == "__main__":
    # example using https://rapidapi.com/alphavantage/api/alpha-vantage
    querystring = {"function": "GLOBAL_QUOTE", "symbol": "MSFT", "datatype": "json"}
    
    resp = API.get("/query", querystring)
    print(resp)