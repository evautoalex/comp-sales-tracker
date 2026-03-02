"""
EV Auto Comp Sales Tracker - Comparison Engine
Compares daily VIN snapshots to calculate estimated sales.
A VIN present yesterday but missing today = 1 estimated sale.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from config import DATA_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_snapshot_path(date_str):
    """Get file path for a daily snapshot."""
    return os.path.join(DATA_DIR, "snapshots", f"{date_str}.json")


def load_snapshot(date_str):
    """Load a daily VIN snapshot."""
    path = get_snapshot_path(date_str)
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return None


def save_snapshot(date_str, data):
    """Save a daily VIN snapshot."""
    os.makedirs(os.path.join(DATA_DIR, "snapshots"), exist_ok=True)
    path = get_snapshot_path(date_str)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    logger.info(f"Saved snapshot: {path}")


def load_sales_history():
    """Load the cumulative sales history."""
    path = os.path.join(DATA_DIR, "sales_history.json")
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return {"daily": [], "dealers": {}}


def save_sales_history(history):
    """Save the cumulative sales history."""
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, "sales_history.json")
    with open(path, 'w') as f:
        json.dump(history, f, indent=2)


def compute_daily_sales(today_snapshot, yesterday_snapshot):
    """
    Compare two snapshots to estimate daily sales per dealer.
    VINs present yesterday but absent today = estimated sales.
    """
    sales = {}

    for dealer_key in today_snapshot:
        today_data = today_snapshot[dealer_key]
        yesterday_data = yesterday_snapshot.get(dealer_key, {})

        today_tesla = set(today_data.get('tesla', []))
        yesterday_tesla = set(yesterday_data.get('tesla', []))
        today_rivian = set(today_data.get('rivian', []))
        yesterday_rivian = set(yesterday_data.get('rivian', []))

        # VINs gone = estimated sales
        tesla_sold = yesterday_tesla - today_tesla
        rivian_sold = yesterday_rivian - today_rivian

        # New VINs = new inventory added
        tesla_new = today_tesla - yesterday_tesla
        rivian_new = today_rivian - yesterday_rivian

        sales[dealer_key] = {
            'name': today_data.get('name', dealer_key),
            'is_us': today_data.get('is_us', False),
            'tesla': {
                'sold_count': len(tesla_sold),
                'sold_vins': sorted(tesla_sold),
                'new_count': len(tesla_new),
                'current_inventory': len(today_tesla),
                'previous_inventory': len(yesterday_tesla),
            },
            'rivian': {
                'sold_count': len(rivian_sold),
                'sold_vins': sorted(rivian_sold),
                'new_count': len(rivian_new),
                'current_inventory': len(today_rivian),
                'previous_inventory': len(yesterday_rivian),
            },
            'total_sold': len(tesla_sold) + len(rivian_sold),
            'total_inventory': len(today_tesla) + len(today_rivian),
        }

    return sales


def update_sales_history(date_str, daily_sales):
    """Add today's sales to the cumulative history."""
    history = load_sales_history()

    # Add daily record
    daily_record = {
        'date': date_str,
        'dealers': {}
    }
    for dealer_key, data in daily_sales.items():
        daily_record['dealers'][dealer_key] = {
            'name': data['name'],
            'is_us': data['is_us'],
            'tesla_sold': data['tesla']['sold_count'],
            'rivian_sold': data['rivian']['sold_count'],
            'total_sold': data['total_sold'],
            'tesla_inventory': data['tesla']['current_inventory'],
            'rivian_inventory': data['rivian']['current_inventory'],
        }

    # Avoid duplicate entries for the same date
    history['daily'] = [d for d in history['daily'] if d['date'] != date_str]
    history['daily'].append(daily_record)
    history['daily'].sort(key=lambda x: x['date'])

    # Update cumulative dealer totals
    for dealer_key, data in daily_sales.items():
        if dealer_key not in history['dealers']:
            history['dealers'][dealer_key] = {
                'name': data['name'],
                'is_us': data['is_us'],
                'total_tesla_sold': 0,
                'total_rivian_sold': 0,
            }
        history['dealers'][dealer_key]['total_tesla_sold'] += data['tesla']['sold_count']
        history['dealers'][dealer_key]['total_rivian_sold'] += data['rivian']['sold_count']

    save_sales_history(history)
    return history


def get_monthly_summary(history, year, month):
    """Get sales summary for a specific month."""
    prefix = f"{year}-{month:02d}"
    monthly = {}
    for record in history['daily']:
        if record['date'].startswith(prefix):
            for dealer_key, data in record['dealers'].items():
                if dealer_key not in monthly:
                    monthly[dealer_key] = {
                        'name': data['name'],
                        'is_us': data.get('is_us', False),
                        'tesla_sold': 0,
                        'rivian_sold': 0,
                        'total_sold': 0,
                        'days_tracked': 0,
                    }
                monthly[dealer_key]['tesla_sold'] += data['tesla_sold']
                monthly[dealer_key]['rivian_sold'] += data['rivian_sold']
                monthly[dealer_key]['total_sold'] += data['total_sold']
                monthly[dealer_key]['days_tracked'] += 1
    return monthly


def get_yearly_summary(history, year):
    """Get sales summary for a specific year."""
    prefix = f"{year}-"
    yearly = {}
    for record in history['daily']:
        if record['date'].startswith(prefix):
            for dealer_key, data in record['dealers'].items():
                if dealer_key not in yearly:
                    yearly[dealer_key] = {
                        'name': data['name'],
                        'is_us': data.get('is_us', False),
                        'tesla_sold': 0,
                        'rivian_sold': 0,
                        'total_sold': 0,
                        'days_tracked': 0,
                    }
                yearly[dealer_key]['tesla_sold'] += data['tesla_sold']
                yearly[dealer_key]['rivian_sold'] += data['rivian_sold']
                yearly[dealer_key]['total_sold'] += data['total_sold']
                yearly[dealer_key]['days_tracked'] += 1
    return yearly
