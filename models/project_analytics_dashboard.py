from odoo import models, fields, api, _
from odoo.tools import SQL
import logging

_logger = logging.getLogger(__name__)


class ProjectAnalyticsDashboard(models.Model):
    """
    Dashboard model for Project Statistics.
    Provides KPIs, aggregations, and top/bottom project rankings.
    """
    _name = 'project.analytics.dashboard'
    _description = 'Project Analytics Dashboard'
    _auto = False  # This is a SQL view, not a real table

    # KPI Fields
    total_projects = fields.Integer(string='Total Projects', readonly=True)
    projects_with_profit = fields.Integer(string='Profitable Projects', readonly=True)
    projects_with_loss = fields.Integer(string='Loss-Making Projects', readonly=True)

    total_revenue_net = fields.Float(string='Total Revenue (NET)', readonly=True)
    total_costs_net = fields.Float(string='Total Costs (NET)', readonly=True)
    total_profit_loss_net = fields.Float(string='Total Profit/Loss (NET)', readonly=True)

    total_hours_booked = fields.Float(string='Total Hours Booked', readonly=True)
    total_outstanding_net = fields.Float(string='Total Outstanding (NET)', readonly=True)

    avg_profit_margin = fields.Float(string='Average Profit Margin %', readonly=True)
    avg_project_revenue = fields.Float(string='Avg Project Revenue', readonly=True)

    def init(self):
        """Create the SQL view for dashboard KPIs."""
        self.env.cr.execute("""
            DROP VIEW IF EXISTS project_analytics_dashboard CASCADE;
            CREATE OR REPLACE VIEW project_analytics_dashboard AS (
                SELECT
                    1 AS id,
                    COUNT(*) FILTER (WHERE has_analytic_account = TRUE) AS total_projects,
                    COUNT(*) FILTER (WHERE profit_loss_net > 0 AND has_analytic_account = TRUE) AS projects_with_profit,
                    COUNT(*) FILTER (WHERE profit_loss_net < 0 AND has_analytic_account = TRUE) AS projects_with_loss,
                    COALESCE(SUM(customer_invoiced_amount_net) FILTER (WHERE has_analytic_account = TRUE), 0) AS total_revenue_net,
                    COALESCE(SUM(total_costs_net + vendor_bills_total_net) FILTER (WHERE has_analytic_account = TRUE), 0) AS total_costs_net,
                    COALESCE(SUM(profit_loss_net) FILTER (WHERE has_analytic_account = TRUE), 0) AS total_profit_loss_net,
                    COALESCE(SUM(total_hours_booked) FILTER (WHERE has_analytic_account = TRUE), 0) AS total_hours_booked,
                    COALESCE(SUM(customer_outstanding_amount_net) FILTER (WHERE has_analytic_account = TRUE), 0) AS total_outstanding_net,
                    CASE
                        WHEN SUM(customer_invoiced_amount_net) FILTER (WHERE has_analytic_account = TRUE) > 0
                        THEN (SUM(profit_loss_net) FILTER (WHERE has_analytic_account = TRUE) /
                              SUM(customer_invoiced_amount_net) FILTER (WHERE has_analytic_account = TRUE)) * 100
                        ELSE 0
                    END AS avg_profit_margin,
                    CASE
                        WHEN COUNT(*) FILTER (WHERE has_analytic_account = TRUE) > 0
                        THEN SUM(customer_invoiced_amount_net) FILTER (WHERE has_analytic_account = TRUE) /
                             COUNT(*) FILTER (WHERE has_analytic_account = TRUE)
                        ELSE 0
                    END AS avg_project_revenue
                FROM project_project
                WHERE active = TRUE
            );
        """)

    @api.model
    def get_dashboard_data(self, company_id=None):
        """
        Get comprehensive dashboard data including KPIs and top/bottom projects.

        Args:
            company_id: Optional company filter

        Returns:
            dict: Dashboard data with KPIs and project rankings
        """
        domain = [('has_analytic_account', '=', True), ('active', '=', True)]
        if company_id:
            domain.append(('company_id', '=', company_id))

        projects = self.env['project.project'].search(domain)

        # Calculate KPIs
        total_projects = len(projects)
        projects_with_profit = len(projects.filtered(lambda p: p.profit_loss_net > 0))
        projects_with_loss = len(projects.filtered(lambda p: p.profit_loss_net < 0))

        total_revenue = sum(projects.mapped('customer_invoiced_amount_net'))
        total_costs = sum(projects.mapped('total_costs_net')) + sum(projects.mapped('vendor_bills_total_net'))
        total_profit = sum(projects.mapped('profit_loss_net'))
        total_hours = sum(projects.mapped('total_hours_booked'))
        total_outstanding = sum(projects.mapped('customer_outstanding_amount_net'))

        avg_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
        avg_revenue = total_revenue / total_projects if total_projects > 0 else 0

        # Top 5 profitable projects
        top_profitable = projects.sorted(key=lambda p: p.profit_loss_net, reverse=True)[:5]
        # Bottom 5 (most loss-making) projects
        bottom_profitable = projects.sorted(key=lambda p: p.profit_loss_net)[:5]

        # Top 5 by revenue
        top_revenue = projects.sorted(key=lambda p: p.customer_invoiced_amount_net, reverse=True)[:5]

        # Projects with highest outstanding amounts
        top_outstanding = projects.sorted(key=lambda p: p.customer_outstanding_amount_net, reverse=True)[:5]

        return {
            'kpis': {
                'total_projects': total_projects,
                'projects_with_profit': projects_with_profit,
                'projects_with_loss': projects_with_loss,
                'total_revenue_net': total_revenue,
                'total_costs_net': total_costs,
                'total_profit_loss_net': total_profit,
                'total_hours_booked': total_hours,
                'total_outstanding_net': total_outstanding,
                'avg_profit_margin': round(avg_margin, 2),
                'avg_project_revenue': round(avg_revenue, 2),
            },
            'top_profitable': [{
                'id': p.id,
                'name': p.name,
                'client_name': p.client_name or '',
                'profit_loss_net': p.profit_loss_net,
                'customer_invoiced_amount_net': p.customer_invoiced_amount_net,
            } for p in top_profitable],
            'bottom_profitable': [{
                'id': p.id,
                'name': p.name,
                'client_name': p.client_name or '',
                'profit_loss_net': p.profit_loss_net,
                'customer_invoiced_amount_net': p.customer_invoiced_amount_net,
            } for p in bottom_profitable],
            'top_revenue': [{
                'id': p.id,
                'name': p.name,
                'client_name': p.client_name or '',
                'customer_invoiced_amount_net': p.customer_invoiced_amount_net,
                'profit_loss_net': p.profit_loss_net,
            } for p in top_revenue],
            'top_outstanding': [{
                'id': p.id,
                'name': p.name,
                'client_name': p.client_name or '',
                'customer_outstanding_amount_net': p.customer_outstanding_amount_net,
                'customer_invoiced_amount_net': p.customer_invoiced_amount_net,
            } for p in top_outstanding],
        }

    @api.model
    def get_trend_data(self, project_id=None, period='monthly', limit=12):
        """
        Get trend data from financial snapshots.

        Args:
            project_id: Optional project filter (None for all projects)
            period: 'monthly' or 'quarterly'
            limit: Number of periods to return

        Returns:
            dict: Trend data for charts
        """
        domain = [('snapshot_type', '=', period)]
        if project_id:
            domain.append(('project_id', '=', project_id))

        snapshots = self.env['project.financial.snapshot'].search(
            domain,
            order='snapshot_date desc',
            limit=limit * (1 if project_id else 10)  # More if aggregating all projects
        )

        if project_id:
            # Single project trend
            return {
                'labels': [s.period_label for s in reversed(snapshots)],
                'revenue': [s.customer_invoiced_amount_net for s in reversed(snapshots)],
                'costs': [s.total_costs_net + s.vendor_bills_total_net for s in reversed(snapshots)],
                'profit': [s.profit_loss_net for s in reversed(snapshots)],
                'hours': [s.total_hours_booked for s in reversed(snapshots)],
                'burn_rate': [s.monthly_burn_rate for s in reversed(snapshots)],
            }
        else:
            # Aggregate trend across all projects
            from collections import defaultdict
            aggregated = defaultdict(lambda: {
                'revenue': 0, 'costs': 0, 'profit': 0, 'hours': 0
            })

            for snapshot in snapshots:
                period_key = snapshot.period_label
                aggregated[period_key]['revenue'] += snapshot.customer_invoiced_amount_net
                aggregated[period_key]['costs'] += snapshot.total_costs_net + snapshot.vendor_bills_total_net
                aggregated[period_key]['profit'] += snapshot.profit_loss_net
                aggregated[period_key]['hours'] += snapshot.total_hours_booked

            # Sort by date and limit
            sorted_periods = sorted(aggregated.keys(), reverse=True)[:limit]
            sorted_periods.reverse()

            return {
                'labels': sorted_periods,
                'revenue': [aggregated[p]['revenue'] for p in sorted_periods],
                'costs': [aggregated[p]['costs'] for p in sorted_periods],
                'profit': [aggregated[p]['profit'] for p in sorted_periods],
                'hours': [aggregated[p]['hours'] for p in sorted_periods],
            }

    @api.model
    def get_burn_down_data(self, project_id):
        """
        Get burn-down chart data for a specific project.

        Args:
            project_id: Project ID

        Returns:
            dict: Burn-down data including planned vs actual costs
        """
        project = self.env['project.project'].browse(project_id)
        if not project.exists():
            return {}

        # Get snapshots for this project
        snapshots = self.env['project.financial.snapshot'].search([
            ('project_id', '=', project_id),
        ], order='snapshot_date asc')

        if not snapshots:
            return {
                'labels': [],
                'planned_costs': [],
                'actual_costs': [],
                'budget_remaining': [],
            }

        # Calculate budget (use sales order amount as budget baseline)
        budget = project.sale_order_amount_net or project.customer_invoiced_amount_net

        labels = []
        actual_costs = []
        cumulative_cost = 0

        for snapshot in snapshots:
            labels.append(snapshot.period_label)
            cumulative_cost = (
                snapshot.adjusted_vendor_bill_amount +
                snapshot.labor_costs_adjusted +
                snapshot.other_costs_net
            )
            actual_costs.append(cumulative_cost)

        # Calculate linear planned costs (simple linear projection)
        if project.date_start and project.date:
            total_days = (project.date - project.date_start).days
            if total_days > 0:
                planned_costs = []
                for i, snapshot in enumerate(snapshots):
                    days_elapsed = (snapshot.snapshot_date - project.date_start).days
                    planned = budget * (days_elapsed / total_days) if budget > 0 else 0
                    planned_costs.append(planned)
            else:
                planned_costs = [budget / len(snapshots) * (i + 1) for i in range(len(snapshots))]
        else:
            planned_costs = [budget / len(snapshots) * (i + 1) for i in range(len(snapshots))]

        budget_remaining = [budget - cost for cost in actual_costs]

        return {
            'labels': labels,
            'budget': budget,
            'planned_costs': planned_costs,
            'actual_costs': actual_costs,
            'budget_remaining': budget_remaining,
        }
