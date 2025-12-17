{
    'name': 'Project Statistic',
    'version': '18.0.2.0.0',
    'category': 'Project',
    'summary': 'Enhanced project analytics with dashboard, PDF reports, and timeline tracking',
    'description': """
        Project Analytics Module
        ========================
        Provides comprehensive financial analytics for projects including:

        **Financial Tracking:**
        - Detailed invoice and credit note tracking (separate fields)
        - Vendor bill and refund management with surcharge factors
        - Cost analysis with tax calculations (NET/GROSS)
        - Multiple profit/loss calculations (standard and adjusted)
        - Labor cost tracking with adjustable hourly rates
        - German accounting support (Skonto - cash discounts)

        **Dashboard & Reporting:**
        - Interactive dashboard with KPIs and project cards
        - Top 5 profitable/unprofitable projects
        - Outstanding invoices tracking
        - PDF reports for individual projects and portfolio summary

        **Timeline Analysis:**
        - Monthly and quarterly financial snapshots
        - Trend analysis over time
        - Revenue/cost burn-down tracking
        - Burn rate calculations and projections

        **Views:**
        - Clean restructured UI with Outgoing/Incoming Invoices
        - Kanban dashboard view
        - Pivot and graph views for analysis
        - List view with all financial metrics

        **Technical Features:**
        - Odoo 18 analytic_distribution support
        - Optimized batch processing
        - Automatic snapshot creation (cron jobs)
        - Module-agnostic view references
    """,
    'depends': [
        'project',
        'account',
        'accountant',  # Odoo 18 Enterprise accounting features
        'analytic',
        'hr_timesheet',
        'timesheet_grid',  # Odoo 18 Enterprise timesheet grid
        'sale',
        'sale_project',  # Required for project_id field on sale.order
    ],
    'author': 'Alex Feld',
    'license': 'LGPL-3',
    'data': [
        # Security
        'security/ir.model.access.csv',
        # Configuration
        'data/ir_config_parameter.xml',
        # Wizard
        'wizard/refresh_financial_data_wizard_views.xml',
        # Views (order matters - base views first)
        'views/hr_employee_views.xml',
        'views/project_analytics_views.xml',
        'views/project_financial_snapshot_views.xml',
        'views/project_analytics_dashboard_views.xml',
        # Reports
        'report/project_financial_report_templates.xml',
        # Menu items (loaded last - references actions)
        'data/menuitem.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'uninstall_hook': 'uninstall_hook',
}
