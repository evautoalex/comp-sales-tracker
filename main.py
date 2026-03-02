"""
EV Auto Comp Sales Tracker - Main Orchestrator
Runs the full daily pipeline:
1. Scrape all dealer VINs (Tesla + Rivian)
2. Save today's snapshot
3. Compare with yesterday's snapshot
4. Update sales history
5. Generate branded dashboard
6. Post to Slack
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta

from scraper import scrape_all_dealers
from compare import (
    save_snapshot, load_snapshot, compute_daily_sales,
    update_sales_history, load_sales_history,
)
from dashboard import generate_dashboard
from slack_notify import post_to_slack

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_daily_pipeline():
    """Execute the full daily pipeline."""
    today = datetime.now()
    today_str = today.strftime('%Y-%m-%d')
    yesterday_str = (today - timedelta(days=1)).strftime('%Y-%m-%d')

    logger.info(f"{'='*60}")
    logger.info(f"EV Auto Comp Sales Tracker â {today_str}")
    logger.info(f"{'='*60}")

    # Step 1: Scrape all dealers
    logger.info("Step 1: Scraping all dealer inventories...")
    today_snapshot = scrape_all_dealers()

    # Log summary
    for dk, data in today_snapshot.items():
        tesla_count = len(data.get('tesla', []))
        rivian_count = len(data.get('rivian', []))
        logger.info(f"  {data.get('name', dk)}: {tesla_count} Tesla, {rivian_count} Rivian")

    # Step 2: Save today's snapshot
    logger.info("Step 2: Saving today's snapshot...")
    save_snapshot(today_str, today_snapshot)

    # Step 3: Compare with yesterday
    logger.info("Step 3: Comparing with yesterday's data...")
    yesterday_snapshot = load_snapshot(yesterday_str)

    if yesterday_snapshot:
        daily_sales = compute_daily_sales(today_snapshot, yesterday_snapshot)
        logger.info("Daily sales estimates:")
        for dk, data in sorted(daily_sales.items(), key=lambda x: x[1]['total_sold'], reverse=True):
            logger.info(
                f"  {data['name']}: {data['total_sold']} total "
                f"(Tesla: {data['tesla']['sold_count']}, Rivian: {data['rivian']['sold_count']})"
            )
    else:
        logger.info("No yesterday data found â this is the baseline day.")
        # Create a baseline "sales" record with 0 sales
        daily_sales = {}
        for dk, data in today_snapshot.items():
            daily_sales[dk] = {
                'name': data.get('name', dk),
                'is_us': data.get('is_us', False),
                'tesla': {
                    'sold_count': 0,
                    'sold_vins': [],
                    'new_count': len(data.get('tesla', [])),
                    'current_inventory': len(data.get('tesla', [])),
                    'previous_inventory': 0,
                },
                'rivian': {
                    'sold_count': 0,
                    'sold_vins': [],
                    'new_count': len(data.get('rivian', [])),
                    'current_inventory': len(data.get('rivian', [])),
                    'previous_inventory': 0,
                },
                'total_sold': 0,
                'total_inventory': len(data.get('tesla', [])) + len(data.get('rivian', [])),
            }

    # Step 4: Update cumulative history
    logger.info("Step 4: Updating sales history...")
    history = update_sales_history(today_str, daily_sales)

    # Step 5: Generate dashboard
    logger.info("Step 5: Generating dashboard...")
    dashboard_path = generate_dashboard(today_str, daily_sales_detail=daily_sales)
    logger.info(f"Dashboard saved to: {dashboard_path}")

    # Step 6: Post to Slack
    logger.info("Step 6: Posting to Slack...")
    dashboard_url = os.environ.get(
        'DASHBOARD_URL',
        'https://evautoalex.github.io/comp-sales-tracker/data/dashboard.html'
    )

    # Build summary for Slack
    summary = {}
    for dk, data in daily_sales.items():
        summary[dk] = {
            'name': data['name'],
            'is_us': data.get('is_us', False),
            'tesla_sold': data['tesla']['sold_count'],
            'rivian_sold': data['rivian']['sold_count'],
            'total_sold': data['total_sold'],
        }

    slack_result = post_to_slack(dashboard_url, today_str, summary)
    if slack_result:
        logger.info("â Slack notification sent!")
    else:
        logger.warning("â  Slack notification failed (check SLACK_WEBHOOK_URL)")

    logger.info(f"{'='*60}")
    logger.info("Pipeline complete!")
    logger.info(f"{'='*60}")

    return {
        'date': today_str,
        'snapshot_saved': True,
        'has_comparison': yesterday_snapshot is not None,
        'dashboard_path': dashboard_path,
        'slack_sent': slack_result,
        'daily_sales': summary,
    }


if __name__ == '__main__':
    result = run_daily_pipeline()
    print(json.dumps(result, indent=2))
