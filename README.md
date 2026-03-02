# EV Auto â Competitive Sales Tracker

Automated daily tracking of Tesla and Rivian sales across EV Auto and competitors, powered by VIN-level inventory monitoring.

## How It Works

1. **Daily Scrape** â Every day at 8:00 AM MT, the system scrapes Tesla and Rivian VINs from each dealer's website
2. **Compare** â VINs present yesterday but missing today = estimated sale
3. **Dashboard** â A branded dashboard shows rankings by day, month, and year
4. **Slack Alert** â A link to the dashboard is posted to `#daily-competitive-analysis-report`

## Dealers Tracked

| Dealer | Website | Type |
|--------|---------|------|
| **EV Auto** | evauto.com | Us |
| Kentson Car Company | kentsonbountiful.com, kentsonamericanfork.com | Competitor |
| Recharged | recharged.com | Competitor |
| Axio EV | axioev.com | Competitor |
| Electric Cars HQ | electriccarshq.com | Competitor |
| Mountain Auto SLC | mountainautoslc.com | Competitor |
| Ever Cars | evercars.com | Competitor |
| Family Auto | familyautoslc.com | Competitor |
| Redline Auto | drivecoolcars.com | Competitor |
| Asay Auto | asayauto.com | Competitor |

## Setup

1. **Clone this repo**
2. **Add Slack webhook** â Go to Settings â Secrets â Actions â Add `SLACK_WEBHOOK_URL`
3. **Enable GitHub Pages** â Settings â Pages â Source: `gh-pages` branch
4. **Run manually** â Actions â Daily Comp Sales Report â Run workflow (first run = baseline)

## Tech

- Python 3.11 + BeautifulSoup + Requests
- GitHub Actions (scheduled daily)
- GitHub Pages (dashboard hosting)
- Slack Incoming Webhook (notifications)
