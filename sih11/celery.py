# sih11/celery.py

import os
from celery import Celery
import dotenv
from pathlib import Path  # <-- 1. Import the Path library

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sih11.settings")

# --- THIS IS THE NEW, MORE ROBUST WAY TO LOAD THE .ENV FILE ---

# 2. Define the project's base directory (the folder containing manage.py)
# This finds the 'sih11' folder and goes up one level.
BASE_DIR = Path(__file__).resolve().parent.parent

# 3. Construct the full, absolute path to your .env file
dotenv_path = os.path.join(BASE_DIR, '.env')

# 4. Load the .env file from that specific path
dotenv.load_dotenv(dotenv_path=dotenv_path)

# --- END OF NEW SECTION ---

app = Celery("sih11")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()