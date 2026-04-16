# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class QualityInspection(models.Model):
    _name = 'dg.quality.inspection'
    _description = 'Casting Quality Inspection'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'inspection_date desc'

    name = fields.Char(
        string='Inspection Ref', required=True, copy=False,
        readonly=True, default=lambda self: _('New')
    )
    product_id   = fields.Many2one('product.product', string='Component', required=True)
    lot_id       = fields.Many2one('stock.lot',        string='Batch / Lot')
    mo_id        = fields.Many2one('mrp.production',   string='Manufacturing Order')
    partner_id   = fields.Many2one('res.partner',      string='Customer')
    inspector_id = fields.Many2one('hr.employee',      string='Inspector')

    inspection_date = fields.Date(default=fields.Date.today, required=True)
    inspection_type = fields.Selection([
        ('incoming',  'Incoming – Raw Material'),
        ('inprocess', 'In-Process'),
        ('final',     'Final Inspection'),
        ('ppap',      'PPAP Submission'),
    ], default='final', required=True, tracking=True)

    # Results
    dimensional_result = fields.Selection(
        [('pass','Pass'),('fail','Fail'),('na','N/A')], default='na')
    dimensional_notes  = fields.Text()
    visual_result      = fields.Selection(
        [('pass','Pass'),('fail','Fail'),('na','N/A')], default='na')
    visual_notes       = fields.Text()
    chemical_result    = fields.Selection(
        [('pass','Pass'),('fail','Fail'),('na','N/A')], default='na')
    material_cert_ref  = fields.Char(string='Material Cert Ref')
    ndt_required       = fields.Boolean(string='NDT Required')
    ndt_method         = fields.Selection([
        ('xray','X-Ray'), ('ut','Ultrasonic'),
        ('pt','Dye Penetrant'), ('mt','Magnetic Particle'),
    ])
    ndt_result = fields.Selection(
        [('pass','Pass'),('fail','Fail'),('na','N/A')], default='na')

    overall_result = fields.Selection([
        ('pass',  'PASS – Release'),
        ('fail',  'FAIL – Rework'),
        ('scrap', 'SCRAP'),
        ('hold',  'HOLD – Pending Decision'),
    ], default='hold', required=True, tracking=True)

    qty_inspected = fields.Integer(string='Qty Inspected')
    qty_rejected  = fields.Integer(string='Qty Rejected')
    qty_accepted  = fields.Integer(
        string='Qty Accepted', compute='_compute_qty', store=True)
    rejection_pct = fields.Float(
        string='Rejection %', compute='_compute_qty', store=True, digits=(5,2))

    certificate_issued = fields.Boolean(string='CoC Issued')
    cert_language = fields.Selection([
        ('en', 'English'),
        ('zh', 'Chinese (Simplified)'),
        ('de', 'German'),
        ('fr', 'French'),
        ('ar', 'Arabic'),
    ], default='en', string='Certificate Language')

    notes      = fields.Text()
    company_id = fields.Many2one('res.company', default=lambda s: s.env.company)

    @api.depends('qty_inspected', 'qty_rejected')
    def _compute_qty(self):
        for r in self:
            r.qty_accepted = (r.qty_inspected or 0) - (r.qty_rejected or 0)
            r.rejection_pct = (
                (r.qty_rejected / r.qty_inspected * 100) if r.qty_inspected else 0
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = (
                    self.env['ir.sequence'].next_by_code('dg.quality.inspection') or _('New')
                )
        return super().create(vals_list)

    def action_issue_cert(self):
        self.certificate_issued = True
        return self.env.ref(
            'dean_group_mfg.action_report_quality_cert'
        ).report_action(self)
