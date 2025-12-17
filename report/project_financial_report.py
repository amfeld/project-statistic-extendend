from odoo import models, api, _
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class ProjectFinancialReport(models.AbstractModel):
    """
    Report model for Project Financial Analysis PDF.
    Provides data for the QWeb report template.
    """
    _name = 'report.project_statistic.project_financial_report'
    _description = 'Project Financial Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        """
        Generate report values for the PDF template.

        Args:
            docids: List of project IDs to generate report for
            data: Optional additional data

        Returns:
            dict: Report values for QWeb template
        """
        projects = self.env['project.project'].browse(docids)

        # Get company info
        company = self.env.company

        # Get configuration values
        config_params = self.env['ir.config_parameter'].sudo()
        general_hourly_rate = float(config_params.get_param(
            'project_statistic.general_hourly_rate', '66.0'
        ))
        vendor_bill_surcharge = float(config_params.get_param(
            'project_statistic.vendor_bill_surcharge_factor', '1.30'
        ))

        # Prepare project data with additional calculations
        project_data = []
        for project in projects:
            # Calculate profit margin
            profit_margin = 0
            if project.customer_invoiced_amount_net > 0:
                profit_margin = (project.profit_loss_net /
                                project.customer_invoiced_amount_net) * 100

            # Calculate cost breakdown percentages
            total_costs = (project.vendor_bills_total_net +
                          project.labor_costs_adjusted +
                          project.other_costs_net)
            vendor_pct = (project.vendor_bills_total_net / total_costs * 100
                         if total_costs > 0 else 0)
            labor_pct = (project.labor_costs_adjusted / total_costs * 100
                        if total_costs > 0 else 0)
            other_pct = (project.other_costs_net / total_costs * 100
                        if total_costs > 0 else 0)

            # Get recent snapshots for trend
            snapshots = self.env['project.financial.snapshot'].search([
                ('project_id', '=', project.id),
            ], order='snapshot_date desc', limit=6)

            # Calculate revenue vs budget variance
            budget = project.sale_order_amount_net or 0
            revenue_variance = project.customer_invoiced_amount_net - budget if budget > 0 else 0
            revenue_variance_pct = (revenue_variance / budget * 100) if budget > 0 else 0

            project_data.append({
                'project': project,
                'profit_margin': round(profit_margin, 2),
                'total_costs': total_costs,
                'vendor_pct': round(vendor_pct, 1),
                'labor_pct': round(labor_pct, 1),
                'other_pct': round(other_pct, 1),
                'snapshots': snapshots,
                'budget': budget,
                'revenue_variance': revenue_variance,
                'revenue_variance_pct': round(revenue_variance_pct, 1),
                'is_profitable': project.profit_loss_net >= 0,
                'is_on_budget': revenue_variance >= 0 if budget > 0 else True,
            })

        return {
            'doc_ids': docids,
            'doc_model': 'project.project',
            'docs': projects,
            'project_data': project_data,
            'company': company,
            'report_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'general_hourly_rate': general_hourly_rate,
            'vendor_bill_surcharge': vendor_bill_surcharge,
            'currency_symbol': company.currency_id.symbol,
        }


class ProjectFinancialReportSummary(models.AbstractModel):
    """
    Summary report model for multiple projects.
    Provides aggregated data for portfolio analysis.
    """
    _name = 'report.project_statistic.project_financial_report_summary'
    _description = 'Project Financial Summary Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        """
        Generate summary report values.
        """
        projects = self.env['project.project'].browse(docids)
        company = self.env.company

        # Aggregated metrics
        total_revenue = sum(projects.mapped('customer_invoiced_amount_net'))
        total_costs = sum(projects.mapped('total_costs_net'))
        total_vendor_bills = sum(projects.mapped('vendor_bills_total_net'))
        total_profit = sum(projects.mapped('profit_loss_net'))
        total_hours = sum(projects.mapped('total_hours_booked'))
        total_outstanding = sum(projects.mapped('customer_outstanding_amount_net'))

        # Project status counts
        profitable_count = len(projects.filtered(lambda p: p.profit_loss_net > 0))
        loss_count = len(projects.filtered(lambda p: p.profit_loss_net < 0))
        breakeven_count = len(projects.filtered(lambda p: p.profit_loss_net == 0))

        # Top and bottom projects
        sorted_by_profit = projects.sorted(key=lambda p: p.profit_loss_net, reverse=True)
        top_5 = sorted_by_profit[:5]
        bottom_5 = sorted_by_profit[-5:] if len(sorted_by_profit) >= 5 else sorted_by_profit

        # Calculate averages
        avg_profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
        avg_revenue_per_project = total_revenue / len(projects) if projects else 0

        return {
            'doc_ids': docids,
            'doc_model': 'project.project',
            'docs': projects,
            'company': company,
            'report_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'currency_symbol': company.currency_id.symbol,
            # Aggregated metrics
            'total_projects': len(projects),
            'total_revenue': total_revenue,
            'total_costs': total_costs + total_vendor_bills,
            'total_vendor_bills': total_vendor_bills,
            'total_profit': total_profit,
            'total_hours': total_hours,
            'total_outstanding': total_outstanding,
            # Status counts
            'profitable_count': profitable_count,
            'loss_count': loss_count,
            'breakeven_count': breakeven_count,
            # Rankings
            'top_5': top_5,
            'bottom_5': bottom_5,
            # Averages
            'avg_profit_margin': round(avg_profit_margin, 2),
            'avg_revenue_per_project': round(avg_revenue_per_project, 2),
        }
