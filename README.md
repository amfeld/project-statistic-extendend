# Project Statistic for Odoo 18 Enterprise

**Version:** 18.0.2.0.0 | **License:** LGPL-3 | **Author:** Alex Feld

---

## Overview / Überblick

**EN:** Project Statistic is a comprehensive financial analytics module for Odoo 18 Enterprise providing detailed project profitability tracking, interactive dashboards, PDF reports, and timeline analysis.

**DE:** Project Statistic ist ein umfassendes Finanzanalyse-Modul für Odoo 18 Enterprise mit detaillierter Projektrentabilitätsverfolgung, interaktiven Dashboards, PDF-Berichten und Zeitverlaufsanalysen.

---

## Table of Contents / Inhaltsverzeichnis

1. [Features](#features)
2. [Installation](#installation)
3. [Configuration / Konfiguration](#configuration--konfiguration)
4. [Usage / Nutzung](#usage--nutzung)
5. [Key Metrics / Kennzahlen](#key-metrics--kennzahlen)
6. [Dashboard & Reports](#dashboard--reports)
7. [Timeline Analysis / Zeitverlaufsanalyse](#timeline-analysis--zeitverlaufsanalyse)
8. [Technical Details / Technische Details](#technical-details--technische-details)
9. [Troubleshooting](#troubleshooting)
10. [Changelog](#changelog)

---

## Features

### Financial Tracking / Finanzverfolgung
| Feature | Description / Beschreibung |
|---------|----------------------------|
| **Revenue Analysis** | Track customer invoices, credit notes, payments (NET/GROSS) |
| **Cost Management** | Monitor vendor bills, labor costs, other expenses |
| **Profit/Loss** | Multiple P&L calculations (standard & adjusted) |
| **German Accounting** | Skonto (cash discount) support for SKR03/SKR04 |

### Dashboard & Reporting
| Feature | Description / Beschreibung |
|---------|----------------------------|
| **Kanban Dashboard** | Visual project cards with KPIs |
| **Top/Bottom Projects** | Quick visibility into performance |
| **Outstanding Invoices** | Track unpaid invoices |
| **PDF Reports** | Detailed project & portfolio reports |

### Timeline Analysis / Zeitverlaufsanalyse
| Feature | Description / Beschreibung |
|---------|----------------------------|
| **Financial Snapshots** | Automatic monthly/quarterly snapshots |
| **Trend Analysis** | Track metrics over time |
| **Burn Rate** | Monthly cost burn & projections |
| **Delta Calculations** | Period-over-period comparison |

---

## Installation

### Prerequisites / Voraussetzungen

- Odoo 18 Enterprise
- Required modules / Erforderliche Module:
  - `project`, `account`, `accountant` (Enterprise)
  - `analytic`, `hr_timesheet`, `timesheet_grid` (Enterprise)
  - `sale`, `sale_project`

### Steps / Schritte

1. Copy module to addons directory
2. Update apps list: `Apps > Update Apps List`
3. Search "Project Statistic" and install

---

## Configuration / Konfiguration

### System Parameters / Systemparameter

| Parameter | Default | Description |
|-----------|---------|-------------|
| `project_statistic.general_hourly_rate` | 66.0 EUR | Hourly rate for labor costs |
| `project_statistic.vendor_bill_surcharge_factor` | 1.30 | Vendor bill surcharge (30%) |

Update via: **Refresh Financial Data** wizard

### Employee HFC Factor / Mitarbeiter HFC-Faktor

Location: `Employees > Employee > HR Settings > Project Analytics`

| Value | Effect |
|-------|--------|
| 1.0 | No adjustment (default) |
| 1.2 | +20% hours counted |
| 0.8 | -20% hours counted |

### Project Setup / Projekt-Einrichtung

For financial tracking:
1. Assign **Analytic Account** (Plan: Projects)
2. Set **Analytic Distribution** on invoice/bill lines
3. Post invoices and bills

---

## Usage / Nutzung

### Menu Location / Menüpfad

```
Accounting > Reports > Project Statistic
├── Dashboard          (Kanban overview)
├── Project List       (Detailed list view)
├── Top Profitable     (Profitable projects)
├── Requires Attention (Loss-making projects)
├── Outstanding Invoices
└── Financial Timeline (Snapshots & trends)
```

### Quick Actions / Schnellaktionen

| Action | Location |
|--------|----------|
| View Financial Analysis | Project Form > Financial Analysis button |
| View Invoices & Bills | Analytics Form > Invoices & Bills button |
| Create Snapshot | Select projects > Action > Create Financial Snapshot |
| Generate PDF Report | Select projects > Print > Project Financial Report |
| Refresh Data | List/Form header > Refresh Financial Data |

---

## Key Metrics / Kennzahlen

### Revenue Metrics / Umsatzkennzahlen

| Field | Formula / Formel |
|-------|------------------|
| **Revenue (NET)** | Customer Invoices - Credit Notes (without VAT) |
| **Paid (NET)** | Revenue × Payment Ratio |
| **Outstanding (NET)** | Revenue - Paid |

### Cost Metrics / Kostenkennzahlen

| Field | Formula / Formel |
|-------|------------------|
| **Vendor Bills (NET)** | Bills - Vendor Credit Notes (without VAT) |
| **Adjusted Vendor Bills** | Vendor Bills × Surcharge Factor |
| **Hours (Adjusted)** | Σ(Hours × Employee HFC Factor) |
| **Labor Costs (Adjusted)** | Hours Adjusted × General Hourly Rate |
| **Total Costs (NET)** | Labor Costs + Other Costs |

### Profitability / Rentabilität

| Field | Formula / Formel |
|-------|------------------|
| **Profit/Loss (NET)** | (Revenue - Customer Skonto) - (Vendor Bills - Vendor Skonto + Total Costs) |
| **Current P&L (Calc.)** | Revenue - Adjusted Vendor Bills - Adjusted Labor - Other Costs |
| **Losses** | abs(min(0, Profit/Loss)) |

### Why NET Basis? / Warum NETTO-Basis?

```
Example / Beispiel:

Customer pays / Kunde zahlt:     €10,000 GROSS (with 19% VAT)
Actual revenue / Echte Einnahme:  €8,403 NET

Vendor costs / Lieferant kostet:  €3,000 GROSS (with 19% VAT)
Actual cost / Echte Kosten:       €2,521 NET

❌ WRONG (GROSS): €10,000 - €3,000 = €7,000 profit
✅ CORRECT (NET): €8,403 - €2,521 = €5,882 profit

VAT is pass-through - not real profit!
MwSt ist Durchlaufposten - kein echter Gewinn!
```

---

## Dashboard & Reports

### Kanban Dashboard

The dashboard shows project cards with:
- Project name and client
- Revenue vs Costs
- Profit/Loss with color coding
- Hours booked
- Profitability badge

### PDF Reports

#### Project Financial Report (Single Project)

Contents:
- KPIs (Revenue, Costs, Profit, Margin)
- Revenue breakdown (Invoices, Credit Notes, Skonto)
- Cost analysis (Vendor Bills, Labor, Other)
- Payment status
- Budget variance
- Historical trend (if snapshots exist)

#### Portfolio Summary Report (Multiple Projects)

Contents:
- Total KPIs across all projects
- Project status distribution
- Top 5 profitable projects
- Projects requiring attention
- Complete project comparison table

### How to Generate / Wie generieren

1. Select project(s) in list view
2. Click `Print` menu
3. Choose report type

---

## Timeline Analysis / Zeitverlaufsanalyse

### Financial Snapshots / Finanzielle Momentaufnahmen

Snapshots capture project state at a point in time:

| Type | Frequency | Created By |
|------|-----------|------------|
| Monthly | 1st of month | Cron job |
| Quarterly | 1st of quarter | Cron job |
| Manual | On demand | User action |

### What's Captured / Was erfasst wird

- Revenue metrics (invoiced, paid, outstanding)
- Cost metrics (vendor bills, labor, other)
- Profitability (P&L, calculated P&L)
- Time tracking (hours, adjusted hours)
- Skonto amounts

### Trend Analysis / Trendanalyse

The snapshot list provides:
- **Delta calculations:** Change vs previous period
- **Burn rate:** Monthly cost consumption
- **Projections:** Estimated completion cost

### Views Available / Verfügbare Ansichten

| View | Purpose |
|------|---------|
| List | All snapshots with metrics |
| Pivot | Cross-tabulation by project/period |
| Graph | Line chart of trends over time |
| Form | Detailed snapshot breakdown |

---

## Technical Details / Technische Details

### Models / Modelle

| Model | Purpose |
|-------|---------|
| `project.project` | Extended with 30+ financial fields |
| `project.financial.snapshot` | Periodic financial snapshots |
| `project.analytics.dashboard` | SQL view for aggregated KPIs |
| `hr.employee` | Extended with HFC factor |

### Hooks / Trigger

| Model | Event | Action |
|-------|-------|--------|
| `account.move.line` | create/write/unlink | Recompute project analytics |
| `account.analytic.line` | create/write/unlink | Recompute project analytics |

### Odoo 18 Compliance

- Uses `analytic_distribution` JSON field
- Proper deferred expense/revenue handling
- `aggregator='sum'` for stored computed fields
- Module-agnostic view references

### Cron Jobs / Geplante Aufgaben

| Job | Schedule | Action |
|-----|----------|--------|
| Monthly Snapshots | 1st of month | Create monthly snapshots for all projects |
| Quarterly Snapshots | 1st of quarter | Create quarterly snapshots for all projects |

---

## Troubleshooting

### No Financial Data Displayed / Keine Finanzdaten angezeigt

1. Check project has analytic account assigned
2. Verify invoice lines have analytic distribution
3. Ensure invoices/bills are "Posted"
4. Run "Refresh Financial Data" wizard

### Sums Not Showing / Summen werden nicht angezeigt

- Sums appear at bottom when scrolling
- Check view is using correct list view ID

### Dashboard Empty / Dashboard leer

- Only projects with `has_analytic_account = True` are shown
- Assign analytic accounts to projects

### PDF Report Issues / PDF-Bericht Probleme

- Ensure wkhtmltopdf is installed
- Check report action binding is correct

---

## Changelog

### v18.0.2.0.0 (Current)

**New Features:**
- Dashboard with Kanban view and KPIs
- PDF reports (single project & portfolio summary)
- Financial Snapshots for timeline tracking
- Trend analysis and burn rate calculations
- Cron jobs for automatic snapshots

**Improvements:**
- Optimized batch processing
- Module-agnostic view references
- Complete German translation (1160+ entries)

**Fixes:**
- Consolidated menu structure
- Fixed decoration-bf syntax
- Fixed link widget references
- Removed duplicate fields

### v18.0.1.2.1

- Frontend fixes and best practices
- Menu consolidation
- Enhanced analytic entries view

### v18.0.1.0.0

- Initial release
- Financial tracking (NET/GROSS)
- German accounting support (Skonto)
- Background calculations with hooks

---

## Support

For issues and feature requests:
- GitHub: [Issue Tracker](https://github.com/amfeld/projekt-statistik-v3/issues)

---

## License / Lizenz

This module is licensed under **LGPL-3**.
See LICENSE file for details.
