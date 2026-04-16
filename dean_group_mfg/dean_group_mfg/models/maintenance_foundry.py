# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import date, timedelta


class MaintenanceEquipmentFoundry(models.Model):
    """Extends maintenance.equipment with foundry-specific fields."""
    _inherit = 'maintenance.equipment'

    # ── Foundry classification ────────────────────────────────
    foundry_zone = fields.Selection([
        ('wax_room',     'Wax Room'),
        ('shell_room',   'Shell Room'),
        ('casting_floor','Casting Floor'),
        ('heat_treat',   'Heat Treatment'),
        ('finishing',    'Finishing / Shot Blast'),
        ('cnc',          'CNC Machining'),
        ('quality',      'Quality & Metrology'),
        ('utilities',    'Utilities / Services'),
        ('lifting',      'Lifting Equipment'),
    ], string='Foundry Zone')

    casting_process_id = fields.Many2one(
        'dg.casting.process', string='Used In Process'
    )

    # ── Operating specs ───────────────────────────────────────
    max_capacity_kg     = fields.Float(string='Max Capacity (kg)', digits=(8, 2))
    max_temp_c          = fields.Float(string='Max Temperature (°C)', digits=(7, 1))
    operating_hours     = fields.Float(string='Total Operating Hours', digits=(10, 1))
    hours_since_service = fields.Float(
        string='Hours Since Last Service', digits=(10, 1)
    )

    # ── Statutory / certification ─────────────────────────────
    loler_required       = fields.Boolean(string='LOLER Inspection Required')
    loler_cert_date      = fields.Date(string='LOLER Certificate Date')
    loler_next_due       = fields.Date(
        string='LOLER Next Due',
        compute='_compute_loler_due', store=True
    )
    loler_overdue        = fields.Boolean(
        string='LOLER Overdue',
        compute='_compute_loler_due', store=True
    )
    pressure_vessel      = fields.Boolean(string='Pressure Vessel (PSSR)')
    pssr_next_inspection = fields.Date(string='PSSR Next Inspection')
    calibration_required = fields.Boolean(string='Calibration Required')
    calibration_cert_ref = fields.Char(string='Calibration Certificate Ref')
    calibration_due      = fields.Date(string='Calibration Due Date')
    calibration_overdue  = fields.Boolean(
        string='Calibration Overdue',
        compute='_compute_calibration_overdue', store=True
    )

    # ── PPM ───────────────────────────────────────────────────
    ppm_interval_days = fields.Integer(
        string='PPM Interval (days)', default=90
    )
    last_ppm_date     = fields.Date(string='Last PPM Date')
    next_ppm_due      = fields.Date(
        string='Next PPM Due',
        compute='_compute_next_ppm', store=True
    )
    ppm_overdue       = fields.Boolean(
        string='PPM Overdue',
        compute='_compute_next_ppm', store=True
    )

    @api.depends('loler_cert_date')
    def _compute_loler_due(self):
        for r in self:
            if r.loler_required and r.loler_cert_date:
                r.loler_next_due = r.loler_cert_date + timedelta(days=365)
                r.loler_overdue  = r.loler_next_due < date.today()
            else:
                r.loler_next_due = False
                r.loler_overdue  = False

    @api.depends('calibration_due')
    def _compute_calibration_overdue(self):
        for r in self:
            r.calibration_overdue = (
                bool(r.calibration_required and r.calibration_due)
                and r.calibration_due < date.today()
            )

    @api.depends('last_ppm_date', 'ppm_interval_days')
    def _compute_next_ppm(self):
        for r in self:
            if r.last_ppm_date and r.ppm_interval_days:
                r.next_ppm_due = r.last_ppm_date + timedelta(days=r.ppm_interval_days)
                r.ppm_overdue  = r.next_ppm_due < date.today()
            else:
                r.next_ppm_due = False
                r.ppm_overdue  = False

    def action_log_ppm(self):
        """Log a PPM completion and reset next due date."""
        self.write({'last_ppm_date': date.today()})
        self.message_post(
            body=_('✅ PPM completed on %s. Next due: %s') % (
                date.today(), self.next_ppm_due
            ),
            message_type='notification'
        )
