import sys
import os

# Ensure the criteria_api root (parent of 'app') is on sys.path so 'import app.*' works
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # apps/criteria_api
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
