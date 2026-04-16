# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class HrPayslipFoundry(models.Model):
    """Extends hr.payslip with foundry-specific payroll fields."""
    _inherit = 'hr.payslip'

    shift_type = fields.Selection([
        ('day',   'Day Shift'),
        ('late',  'Late Shift'),
        ('night', 'Night Shift'),
        ('office','Office Hours'),
    ], string='Shift Type', related='employee_id.shift', store=True)

    overtime_hours    = fields.Float(string='Overtime Hours', digits=(5, 2))
    night_shift_hours = fields.Float(string='Night Shift Hours', digits=(5, 2))
    late_shift_hours  = fields.Float(string='Late Shift Hours', digits=(5, 2))
    bank_holiday_days = fields.Float(string='Bank Holiday Days Worked', digits=(4, 1))
    is_apprentice     = fields.Boolean(
        string='Apprentice Payslip',
        related='employee_id.employee_type', compute='_compute_is_apprentice'
    )
    apprentice_year   = fields.Selection([
        ('1','Year 1'),('2','Year 2'),('3','Year 3'),('4','Year 4+'),
    ], string='Apprenticeship Year')
    pension_enrolled  = fields.Boolean(string='Auto-Enrolment Pension', default=True)
    pension_employee_pct = fields.Float(string='Employee Pension %', default=5.0, digits=(4,1))
    pension_employer_pct = fields.Float(string='Employer Pension %', default=3.0, digits=(4,1))

    @api.depends('employee_id.employee_type')
    def _compute_is_apprentice(self):
        for r in self:
            r.is_apprentice = r.employee_id.employee_type == 'apprentice'


class HrPayrollStructureFoundry(models.Model):
    """Custom payroll structure for Dean Group foundry workers."""
    _inherit = 'hr.payroll.structure'

    is_foundry_structure = fields.Boolean(string='Foundry Structure')
    applies_to_shift = fields.Selection([
        ('all',   'All Shifts'),
        ('day',   'Day Shift Only'),
        ('late',  'Late Shift Only'),
        ('night', 'Night Shift Only'),
    ], string='Applies To Shift', default='all')


class HrPayrollSalaryRule(models.Model):
    """
    Custom salary rules for Dean Group.
    These are the computation rules, actual rule data is in payroll_rules.xml.
    """
    _inherit = 'hr.salary.rule'

    is_uk_rule       = fields.Boolean(string='UK Payroll Rule')
    hmrc_category    = fields.Selection([
        ('basic',      'Basic Pay'),
        ('allowance',  'Allowance'),
        ('deduction',  'Deduction'),
        ('ni',         'National Insurance'),
        ('income_tax', 'Income Tax (PAYE)'),
        ('pension',    'Pension'),
        ('net',        'Net Pay'),
    ], string='HMRC Category')
