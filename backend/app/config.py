import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env.back.template"))

OCTOPRINT_URL = os.getenv("OCTOPRINT_URL", "http://localhost")
OCTOPRINT_API_KEY = os.getenv("OCTOPRINT_API_KEY", "")
