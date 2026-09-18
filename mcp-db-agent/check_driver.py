from dotenv import load_dotenv
import os

load_dotenv()

print("AGENT_DB_DRIVER:", repr(os.getenv("AGENT_DB_DRIVER")))
print("AGENT_DB_SERVER:", repr(os.getenv("AGENT_DB_SERVER")))
print("HIS_DB_DRIVER:", repr(os.getenv("HIS_DB_DRIVER")))