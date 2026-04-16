# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta


class HrAttendanceFoundry(models.Model):
    """Extends hr.attendance with shift and overtime tracking."""
    _inherit = 'hr.attendance'

    shift_type = fields.Selection([
        ('day',   'Day   06:00–14:00'),
        ('late',  'Late  14:00–22:00'),
        ('night', 'Night 22:00–06:00'),
        ('office','Office 08:00–17:30'),
    ], string='Shift', compute='_compute_shift', store=True)

    overtime_hours = fields.Float(
        string='Overtime Hours', digits=(5, 2),
        compute='_compute_overtime', store=True
    )
    is_bank_holiday = fields.Boolean(string='Bank Holiday')
    late_arrival    = fields.Boolean(
        string='Late Arrival', compute='_compute_late', store=True
    )
    absence_reason  = fields.Selection([
        ('authorised',  'Authorised Absence'),
        ('sick',        'Sick Leave'),
        ('holiday',     'Annual Leave'),
        ('emergency',   'Emergency Leave'),
        ('unauthorised','Unauthorised'),
    ], string='Absence Reason')

    @api.depends('employee_id.shift', 'check_in')
    def _compute_shift(self):
        for r in self:
            r.shift_type = r.employee_id.shift or 'day'

    @api.depends('worked_hours', 'shift_type')
    def _compute_overtime(self):
        standard = {'day': 8.0, 'late': 8.0, 'night': 8.0, 'office': 9.0}
        for r in self:
            std = standard.get(r.shift_type or 'day', 8.0)
            r.overtime_hours = max(0.0, (r.worked_hours or 0) - std)

    @api.depends('check_in', 'shift_type')
    def _compute_late(self):
        shift_start = {
            'day':   6, 'late': 14, 'night': 22, 'office': 8
        }
        for r in self:
            if r.check_in and r.shift_type:
                expected_hour = shift_start.get(r.shift_type, 8)
                # Allow 5-min grace
                grace = r.check_in.replace(
                    hour=expected_hour, minute=5, second=0
                )
                r.late_arrival = r.check_in > grace
            else:
                r.late_arrival = False


class FoundryShiftSchedule(models.Model):
    """
    Shift rotation schedule for Dean Group foundry.
    Tracks which employees are on which shift pattern each week.
    """
    _name = 'dg.shift.schedule'
    _description = 'Foundry Shift Schedule'
    _order = 'week_start desc'

    name           = fields.Char(string='Week Reference', compute='_compute_name', store=True)
    week_start     = fields.Date(string='Week Starting (Monday)', required=True)
    week_end       = fields.Date(string='Week Ending (Sunday)', compute='_compute_week_end', store=True)
    shift_line_ids = fields.One2many('dg.shift.schedule.line', 'schedule_id', string='Shift Lines')
    notes          = fields.Text(string='Shift Notes')
    published      = fields.Boolean(string='Published to Employees', default=False)
    state          = fields.Selection([
        ('draft',     'Draft'),
        ('published', 'Published'),
        ('archived',  'Archived'),
    ], default='draft')

    @api.depends('week_start')
    def _compute_name(self):
        for r in self:
            if r.week_start:
                r.name = f"Week {r.week_start.strftime('%d %b %Y')}"

    @api.depends('week_start')
    def _compute_week_end(self):
        for r in self:
            if r.week_start:
                r.week_end = r.week_start + timedelta(days=6)

    def action_publish(self):
        self.write({'state': 'published', 'published': True})


class FoundryShiftScheduleLine(models.Model):
    """Individual employee shift assignment for a week."""
    _name = 'dg.shift.schedule.line'
    _description = 'Shift Schedule Line'

    schedule_id  = fields.Many2one('dg.shift.schedule', string='Schedule', ondelete='cascade')
    employee_id  = fields.Many2one('hr.employee', string='Employee', required=True)
    shift        = fields.Selection([
        ('day',   'Day   06:00–14:00'),
        ('late',  'Late  14:00–22:00'),
        ('night', 'Night 22:00–06:00'),
        ('office','Office 08:00–17:30'),
        ('off',   'Rest Day / Off'),
    ], string='Shift', required=True)
    mon = fields.Selection(
        [('day','Day'),('late','Late'),('night','Night'),('office','Office'),('off','Off')],
        string='Mon', default='day'
    )
    tue = fields.Selection(
        [('day','Day'),('late','Late'),('night','Night'),('office','Office'),('off','Off')],
        string='Tue', default='day'
    )
    wed = fields.Selection(
        [('day','Day'),('late','Late'),('night','Night'),('office','Office'),('off','Off')],
        string='Wed', default='day'
    )
    thu = fields.Selection(
        [('day','Day'),('late','Late'),('night','Night'),('office','Office'),('off','Off')],
        string='Thu', default='day'
    )
    fri = fields.Selection(
        [('day','Day'),('late','Late'),('night','Night'),('office','Office'),('off','Off')],
        string='Fri', default='day'
    )
    sat = fields.Selection(
        [('day','Day'),('late','Late'),('night','Night'),('office','Office'),('off','Off')],
        string='Sat', default='off'
    )
    sun = fields.Selection(
        [('day','Day'),('late','Late'),('night','Night'),('office','Office'),('off','Off')],
        string='Sun', default='off'
    )
    notes = fields.Char(string='Notes')
