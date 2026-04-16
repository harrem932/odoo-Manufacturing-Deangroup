# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ChinaSupplyOrder(models.Model):
    _name = 'dg.china.supply'
    _description = 'China Supply Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'order_date desc'

    name = fields.Char(
        string='PO Reference', required=True, copy=False,
        readonly=True, default=lambda self: _('New')
    )
    vendor_id    = fields.Many2one(
        'res.partner', string='China Supplier', required=True,
        domain=[('supplier_rank','>',0)]
    )
    product_id   = fields.Many2one('product.product', string='Component')
    process_id   = fields.Many2one('dg.casting.process', string='Process')
    quantity     = fields.Integer(string='Quantity')
    unit_price   = fields.Float(string='Unit Price (CNY)', digits=(10,4))
    exchange_rate = fields.Float(string='CNY/GBP Rate', default=9.05, digits=(8,4))
    total_cny    = fields.Float(compute='_compute_total', store=True, string='Total (CNY)')
    total_gbp    = fields.Float(compute='_compute_total', store=True, string='Total (GBP)')
    order_date   = fields.Date(default=fields.Date.today)
    etd_date     = fields.Date(string='ETD (China)')
    eta_date     = fields.Date(string='ETA (Manchester)')
    state = fields.Selection([
        ('draft',      'Draft'),
        ('confirmed',  'Confirmed'),
        ('in_transit', 'In Transit'),
        ('customs',    'UK Customs'),
        ('received',   'Received'),
        ('inspected',  'Inspected & Released'),
        ('cancelled',  'Cancelled'),
    ], default='draft', tracking=True)
    quality_hold      = fields.Boolean(string='Quality Hold')
    notes             = fields.Text()
    purchase_order_id = fields.Many2one('purchase.order', string='Linked PO')
    company_id        = fields.Many2one('res.company', default=lambda s: s.env.company)

    @api.depends('quantity', 'unit_price', 'exchange_rate')
    def _compute_total(self):
        for r in self:
            r.total_cny = (r.quantity or 0) * (r.unit_price or 0)
            r.total_gbp = r.total_cny / r.exchange_rate if r.exchange_rate else 0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = (
                    self.env['ir.sequence'].next_by_code('dg.china.supply') or _('New')
                )
        return super().create(vals_list)

    def action_confirm(self):   self.state = 'confirmed'
    def action_transit(self):   self.state = 'in_transit'
    def action_received(self):  self.state = 'received'
    def action_released(self):  self.state = 'inspected'
