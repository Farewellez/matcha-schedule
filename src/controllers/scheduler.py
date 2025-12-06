# src/controllers/scheduler.py

from enum import Enum, auto
from typing import Optional
import datetime
import time
from src.models.order import Order
from src.controllers.priority_queue import ProductionPriorityQueue