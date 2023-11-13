import os
# fix for testing just this file
if __name__ == "__main__":
   
    import sys
    # Get the parent directory of the current script (api.py)
    CURR_DIR = os.path.dirname(os.path.abspath(__file__))

    # Add the parent directory to the Python path
    PARENT_DIR = os.path.join(CURR_DIR, "..")  # Go up one level from utils to project folder
    sys.path.append(PARENT_DIR)
from api import API
class AlphaVantage(API):
    @staticmethod
    def quote(symbol):
        params = {}
        params["function"] = "GLOBAL_QUOTE"
        params["symbol"] = f"{symbol}"
        params["datatype"] = "json"
        url = "/query"
        resp = API.get(url, params)
        fixed = {}
        # this API is "odd" and includes numbers as part of the keys like 01. 02. 03. etc and below removes that and returns just the named keys
        # below also converts the remaining spaces into _ to avoid space problems
        # I think the API is mostly targeted at the csv output option instead of the json option although it supports both
        if resp and resp["Global Quote"]:
            gq = resp["Global Quote"]
            for k,v in gq.items():
                if "." in k:
                    k = k.split(".")[1].strip()
                    fixed[k.replace(" ", "_")] = v
        else:
            fixed = resp
        return fixed

if __name__ == "__main__":
    resp = AlphaVantage.quote("COIN")
    print(resp)