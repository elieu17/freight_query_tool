# Freight Rate Query Engine

A FastAPI + SQL freight pricing tool built to simulate real-world ocean freight rate management workflows.

This application allows users to:

- Search freight rates using origin/destination UNLOCODE or full port name
- Filter by contract type (NAC / FAK / SPOT)
- Include Dangerous Goods (DG) surcharges via checkbox
- Calculate bunker fuel charges by trade lane and quarter
- View all-in ocean freight totals
- Download pricing results as CSV exports
- Support multiple equipment types (20GP / 40GP / 40HC)

---

## Business Problem

Booking offices, pricing analysts, customer care teams, and billing teams often spend significant time manually retrieving:

- ocean contract rates
- bunker surcharges
- DG fees
- contract-specific pricing rules

from multiple spreadsheets and disconnected systems.

This creates:

- delayed billing turnaround
- pricing inaccuracies
- manual errors
- poor audit visibility
- inconsistent customer quoting

---

## Solution

This project centralizes freight pricing logic into a single searchable platform using:

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Jinja2
- HTML/CSS

The system supports pricing visibility, faster decision-making, and improved operational consistency.

---

## Features

### Core Features

- Port autocomplete using UNLOCODE + full port name
- Trade-based bunker fuel calculation
- Optional DG surcharge inclusion
- Contract type filtering
- Downloadable CSV exports
- Multi-equipment pricing support

### Future Improvements

- PostgreSQL migration
- User authentication
- Pricing exception alerts
- Inland haulage / free time logic
- Contract version history
- Dashboard reporting

---

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- SQLite
- HTML / CSS
- Git / GitHub
- Render (deployment)

---

## Run Locally

```bash
uvicorn app.main:app --reload

```
## Live Demo

https://freight-rate-query-engine.onrender.com