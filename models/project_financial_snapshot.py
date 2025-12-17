from odoo import models, fields, api, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class ProjectFinancialSnapshot(models.Model):
    """
    Stores periodic financial snapshots of projects for timeline analysis.
    Creates monthly/quarterly snapshots for trend analysis and burn-down charts.
    """
    _name = 'project.financial.snapshot'
    _description = 'Project Financial Snapshot'
    _order = 'snapshot_date desc, project_id'
    _rec_name = 'display_name'

    # Reference fields
    project_id = fields.Many2one(
        'project.project',
        string='Project',
        required=True,
        ondelete='cascade',
        index=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        related='project_id.company_id',
        store=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        related='project_id.currency_id',
        store=True,
    )

    # Snapshot metadata
    snapshot_date = fields.Date(
        string='Snapshot Date',
        required=True,
        index=True,
        default=fields.Date.today,
    )
    snapshot_type = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('manual', 'Manual'),
    ], string='Snapshot Type', required=True, default='manual')
    period_label = fields.Char(
        string='Period',
        compute='_compute_period_label',
        store=True,
    )
    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True,
    )

    # Revenue fields (from project at snapshot time)
    customer_invoiced_amount_net = fields.Float(string='Invoiced (NET)')
    customer_paid_amount_net = fields.Float(string='Paid (NET)')
    customer_outstanding_amount_net = fields.Float(string='Outstanding (NET)')
    sale_order_amount_net = fields.Float(string='Sales Orders (NET)')

    # Cost fields
    vendor_bills_total_net = fields.Float(string='Vendor Bills (NET)')
    adjusted_vendor_bill_amount = fields.Float(string='Adjusted Vendor Bills')
    labor_costs = fields.Float(string='Labor Costs')
    labor_costs_adjusted = fields.Float(string='Labor Costs (Adjusted)')
    total_hours_booked = fields.Float(string='Hours Booked')
    total_hours_booked_adjusted = fields.Float(string='Hours (Adjusted)')
    other_costs_net = fields.Float(string='Other Costs (NET)')
    total_costs_net = fields.Float(string='Total Costs (NET)')

    # Profitability fields
    profit_loss_net = fields.Float(string='Profit/Loss (NET)')
    current_calculated_profit_loss = fields.Float(string='Current P&L (Calculated)')
    negative_difference_net = fields.Float(string='Losses (NET)')

    # Skonto fields
    customer_skonto_taken = fields.Float(string='Customer Discounts')
    vendor_skonto_received = fields.Float(string='Vendor Discounts')

    # Delta fields (change from previous snapshot)
    revenue_delta = fields.Float(
        string='Revenue Change',
        compute='_compute_deltas',
        store=True,
    )
    costs_delta = fields.Float(
        string='Costs Change',
        compute='_compute_deltas',
        store=True,
    )
    profit_delta = fields.Float(
        string='Profit Change',
        compute='_compute_deltas',
        store=True,
    )
    hours_delta = fields.Float(
        string='Hours Change',
        compute='_compute_deltas',
        store=True,
    )

    # Burn rate calculations
    monthly_burn_rate = fields.Float(
        string='Monthly Burn Rate',
        compute='_compute_burn_rate',
        store=True,
        help="Average monthly cost burn rate based on project duration"
    )
    estimated_completion_cost = fields.Float(
        string='Estimated Completion Cost',
        compute='_compute_burn_rate',
        store=True,
        help="Projected total cost at completion based on current burn rate"
    )

    @api.depends('snapshot_date', 'snapshot_type')
    def _compute_period_label(self):
        for record in self:
            if record.snapshot_date:
                date = record.snapshot_date
                if record.snapshot_type == 'quarterly':
                    quarter = (date.month - 1) // 3 + 1
                    record.period_label = f'Q{quarter} {date.year}'
                elif record.snapshot_type == 'monthly':
                    record.period_label = date.strftime('%b %Y')
                else:
                    record.period_label = date.strftime('%Y-%m-%d')
            else:
                record.period_label = ''

    @api.depends('project_id', 'period_label')
    def _compute_display_name(self):
        for record in self:
            if record.project_id and record.period_label:
                record.display_name = f"{record.project_id.name} - {record.period_label}"
            elif record.project_id:
                record.display_name = record.project_id.name
            else:
                record.display_name = _('New Snapshot')

    @api.depends('project_id', 'snapshot_date', 'customer_invoiced_amount_net',
                 'total_costs_net', 'profit_loss_net', 'total_hours_booked')
    def _compute_deltas(self):
        for record in self:
            # Find previous snapshot for this project
            previous = self.search([
                ('project_id', '=', record.project_id.id),
                ('snapshot_date', '<', record.snapshot_date),
            ], order='snapshot_date desc', limit=1)

            if previous:
                record.revenue_delta = record.customer_invoiced_amount_net - previous.customer_invoiced_amount_net
                record.costs_delta = record.total_costs_net - previous.total_costs_net
                record.profit_delta = record.profit_loss_net - previous.profit_loss_net
                record.hours_delta = record.total_hours_booked - previous.total_hours_booked
            else:
                record.revenue_delta = record.customer_invoiced_amount_net
                record.costs_delta = record.total_costs_net
                record.profit_delta = record.profit_loss_net
                record.hours_delta = record.total_hours_booked

    @api.depends('project_id', 'snapshot_date', 'total_costs_net', 'vendor_bills_total_net',
                 'labor_costs_adjusted')
    def _compute_burn_rate(self):
        for record in self:
            record.monthly_burn_rate = 0.0
            record.estimated_completion_cost = 0.0

            if not record.project_id or not record.snapshot_date:
                continue

            # Calculate project duration in months
            project = record.project_id
            start_date = project.date_start or project.create_date.date()
            current_date = record.snapshot_date

            if start_date and current_date > start_date:
                months = ((current_date.year - start_date.year) * 12 +
                         (current_date.month - start_date.month))
                if months > 0:
                    total_costs = (record.adjusted_vendor_bill_amount +
                                   record.labor_costs_adjusted +
                                   record.other_costs_net)
                    record.monthly_burn_rate = total_costs / months

                    # Estimate completion cost if project has end date
                    if project.date:
                        remaining_months = ((project.date.year - current_date.year) * 12 +
                                           (project.date.month - current_date.month))
                        if remaining_months > 0:
                            record.estimated_completion_cost = (
                                total_costs + (record.monthly_burn_rate * remaining_months)
                            )

    @api.model
    def create_snapshot(self, project, snapshot_type='manual'):
        """
        Create a financial snapshot for a project.

        Args:
            project: project.project record
            snapshot_type: 'monthly', 'quarterly', or 'manual'

        Returns:
            project.financial.snapshot record
        """
        if not project.has_analytic_account:
            _logger.warning(f"Cannot create snapshot for project {project.name}: no analytic account")
            return self.env['project.financial.snapshot']

        values = {
            'project_id': project.id,
            'snapshot_date': fields.Date.today(),
            'snapshot_type': snapshot_type,
            # Revenue
            'customer_invoiced_amount_net': project.customer_invoiced_amount_net,
            'customer_paid_amount_net': project.customer_paid_amount_net,
            'customer_outstanding_amount_net': project.customer_outstanding_amount_net,
            'sale_order_amount_net': project.sale_order_amount_net,
            # Costs
            'vendor_bills_total_net': project.vendor_bills_total_net,
            'adjusted_vendor_bill_amount': project.adjusted_vendor_bill_amount,
            'labor_costs': project.labor_costs,
            'labor_costs_adjusted': project.labor_costs_adjusted,
            'total_hours_booked': project.total_hours_booked,
            'total_hours_booked_adjusted': project.total_hours_booked_adjusted,
            'other_costs_net': project.other_costs_net,
            'total_costs_net': project.total_costs_net,
            # Profitability
            'profit_loss_net': project.profit_loss_net,
            'current_calculated_profit_loss': project.current_calculated_profit_loss,
            'negative_difference_net': project.negative_difference_net,
            # Skonto
            'customer_skonto_taken': project.customer_skonto_taken,
            'vendor_skonto_received': project.vendor_skonto_received,
        }

        return self.create(values)

    @api.model
    def create_monthly_snapshots(self):
        """
        Cron job method to create monthly snapshots for all active projects.
        Should be scheduled to run on the 1st of each month.
        """
        _logger.info("Creating monthly financial snapshots...")

        projects = self.env['project.project'].search([
            ('has_analytic_account', '=', True),
            ('active', '=', True),
        ])

        created_count = 0
        for project in projects:
            try:
                self.create_snapshot(project, 'monthly')
                created_count += 1
            except Exception as e:
                _logger.error(f"Error creating snapshot for project {project.name}: {e}")

        _logger.info(f"Created {created_count} monthly snapshots")
        return created_count

    @api.model
    def create_quarterly_snapshots(self):
        """
        Cron job method to create quarterly snapshots for all active projects.
        Should be scheduled to run on the 1st day of each quarter.
        """
        _logger.info("Creating quarterly financial snapshots...")

        projects = self.env['project.project'].search([
            ('has_analytic_account', '=', True),
            ('active', '=', True),
        ])

        created_count = 0
        for project in projects:
            try:
                self.create_snapshot(project, 'quarterly')
                created_count += 1
            except Exception as e:
                _logger.error(f"Error creating snapshot for project {project.name}: {e}")

        _logger.info(f"Created {created_count} quarterly snapshots")
        return created_count
