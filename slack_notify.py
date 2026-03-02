"""
EV Auto Comp Sales Tracker - Slack Integration
Posts just the dashboard link to #daily-competitive-analysis-report.
"""

import os
import logging
import requests
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def post_to_slack(dashboard_url, date_str=None, summary=None):
    """Post just the dashboard link to Slack."""
    webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
    if not webhook_url:
        logger.error("SLACK_WEBHOOK_URL not set")
        return False

    payload = {"text": dashboard_url}

    try:
        resp = requests.post(webhook_url, json=payload, timeout=10)
        if resp.status_code == 200:
            logger.info("â Posted to Slack successfully")
            return True
        else:
            logger.error(f"Slack returned {resp.status_code}: {resp.text}")
            return False
    except Exception as e:
        logger.error(f"Failed to post to Slack: {e}")
        return False


if __name__ == '__main__':
    post_to_slack("https://evautoalex.github.io/comp-sales-tracker/data/dashboard.html")
