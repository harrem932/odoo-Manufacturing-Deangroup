# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class StockLocationFoundry(models.Model):
    """Extends stock location with foundry-specific fields."""
    _inherit = 'stock.location'

    is_foundry_location = fields.Boolean(string='Foundry Location')
    foundry_zone = fields.Selection([
        ('raw_material',    'Raw Material Store'),
        ('wax_room',        'Wax Room'),
        ('shell_room',      'Shell Room'),
        ('casting_floor',   'Casting Floor'),
        ('finishing',       'Finishing / Machining'),
        ('quality_hold',    'Quality Hold'),
        ('finished_goods',  'Finished Goods Warehouse'),
        ('china_quarantine','China Supply – Quarantine'),
        ('china_released',  'China Supply – Released'),
        ('despatch',        'Despatch Bay'),
        ('scrap',           'Scrap'),
    ], string='Foundry Zone')
    site = fields.Selection([
        ('manchester', 'Manchester – UK Foundry'),
        ('china',      'China Partner Site'),
    ], string='Site', default='manchester')


class StockLotFoundry(models.Model):
    """Extends stock lot with casting-specific traceability fields."""
    _inherit = 'stock.lot'

    heat_number      = fields.Char(string='Heat / Melt Number')
    alloy_spec       = fields.Char(string='Alloy Specification')
    material_cert_ref = fields.Char(string='Material Certificate Ref')
    casting_process_id = fields.Many2one(
        'dg.casting.process', string='Casting Process'
    )
    production_site  = fields.Selection([
        ('manchester', 'Manchester – UK Foundry'),
        ('china',      'China Partner'),
    ], string='Production Site')
    customer_id      = fields.Many2one(
        'res.partner', string='Customer',
        domain=[('customer_rank', '>', 0)]
    )
    ppap_approved    = fields.Boolean(string='PPAP Approved')
    quality_cert_ids = fields.One2many(
        'dg.quality.inspection', 'lot_id',
        string='Quality Inspections'
    )
    inspection_count = fields.Integer(
        string='Inspections',
        compute='_compute_inspection_count'
    )

    @api.depends('quality_cert_ids')
    def _compute_inspection_count(self):
        for r in self:
            r.inspection_count = len(r.quality_cert_ids)

    def action_view_inspections(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Quality Inspections'),
            'res_model': 'dg.quality.inspection',
            'view_mode': 'list,form',
            'domain': [('lot_id', '=', self.id)],
            'context': {'default_lot_id': self.id},
        }


class StockPickingFoundry(models.Model):
    """Extends stock picking (delivery/receipt) with casting fields."""
    _inherit = 'stock.picking'

    casting_enquiry_id  = fields.Many2one(
        'dg.casting.enquiry', string='Casting Enquiry'
    )
    china_supply_id     = fields.Many2one(
        'dg.china.supply', string='China Supply Order'
    )
    cert_required       = fields.Boolean(string='CoC Required')
    cert_language       = fields.Selection([
        ('en','English'),('zh','Chinese'),
        ('de','German'),('fr','French'),('ar','Arabic'),
    ], string='CoC Language', default='en')
    certs_issued        = fields.Boolean(string='Certs Issued')
    quality_inspected   = fields.Boolean(string='Quality Inspected')
    is_china_supply     = fields.Boolean(
        string='China Supply Delivery',
        compute='_compute_is_china', store=True
    )

    @api.depends('china_supply_id')
    def _compute_is_china(self):
        for r in self:
            r.is_china_supply = bool(r.china_supply_id)

    def action_mark_certs_issued(self):
        self.write({'certs_issued': True})


class StockWarehouseFoundry(models.Model):
    """Extend warehouse with foundry defaults."""
    _inherit = 'stock.warehouse'

    is_foundry_warehouse = fields.Boolean(string='Foundry Warehouse')
    site = fields.Selection([
        ('manchester', 'Manchester – UK Foundry'),
        ('china',      'China Partner'),
    ], string='Site')
