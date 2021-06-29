__author__ = "mibengt@kth.se"

import modules.helpers as helpers
import modules.mongo as mongo
import re
import traceback

def run():
    try:
        output = "Backup is configured for following databases:\n\n```"
        output += f"{'Type':12}{'Host':70}\n"
        for backup in mongo.get_database_list():
            if "type" in backup:
                if backup["type"] == "mongodb":
                    host = backup["host"]
                elif backup["type"] == "postgresql":
                    match = re.search('host=([^ ]+) ', backup["host"])
                    if match:
                        host = match.groups()[0]
                    else:
                        continue
                else:
                    continue
                output += f"{backup['type']:12}{host:70}\n"
    
        return output + "```"
    except Exception as e:
        return f'Failed to list databases:\n ```{e}\n{traceback.format_exc()} ```'