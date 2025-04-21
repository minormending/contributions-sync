#!/usr/bin/env python3
import argparse
import datetime
import logging
import os
from datetime import datetime as dt
from typing import Dict, Any, Optional

import requests
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# Load environment variables from .env file.
from dotenv import load_dotenv

load_dotenv()
logging.info("Loaded environment variables from .env file")

