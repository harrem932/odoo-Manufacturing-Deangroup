# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


# ══════════════════════════════════════════
#  SALE ORDER EXTENSION
# ══════════════════════════════════════════
class SaleOrderCasting(models.Model):
    """Extends sale.order with casting delivery and certification fields."""
    _inherit = 'sale.order'

    casting_enquiry_id  = fields.Many2one(
        'dg.casting.enquiry', string='Casting Enquiry'
    )
    cert_required       = fields.Boolean(string='CoC Required', default=True)
    cert_language       = fields.Selection([
        ('en','English'),('zh','Chinese (Simplified)'),
        ('de','German'),('fr','French'),('ar','Arabic'),
    ], string='Certificate Language', default='en')
    ppap_required       = fields.Boolean(string='PPAP Required')
    ppap_level          = fields.Selection([
        ('1','Level 1'),('2','Level 2'),('3','Level 3'),
        ('4','Level 4'),('5','Level 5'),
    ], string='PPAP Level')
    customer_po_ref     = fields.Char(string='Customer PO Reference')
    supply_site         = fields.Selection([
        ('manchester', 'UK Foundry – Manchester'),
        ('china',      'China Supply'),
        ('split',      'UK Prototype / China Production'),
    ], string='Supply Route', default='manchester')
    nda_in_place        = fields.Boolean(string='NDA in Place')
    industry            = fields.Selection([
        ('aerospace',   'Aerospace'),
        ('defence',     'Defence'),
        ('oil_gas',     'Oil & Gas'),
        ('medical',     'Medical'),
        ('rail',        'Rail & Transport'),
        ('energy',      'Energy & Power'),
        ('engineering', 'General Engineering'),
    ], string='Industry')
    drawing_ref         = fields.Char(string='Drawing Reference')
    alloy_spec          = fields.Char(string='Alloy / Material Spec')
    inspection_note     = fields.Text(string='Inspection Requirements')


class SaleOrderLineCasting(models.Model):
    """Extends sale order line with casting line fields."""
    _inherit = 'sale.order.line'

    casting_process_id = fields.Many2one(
        'dg.casting.process', string='Casting Process'
    )
    mould_ref     = fields.Char(string='Mould / Tool Ref')
    alloy_spec    = fields.Char(string='Alloy')
    unit_weight_g = fields.Float(string='Unit Weight (g)', digits=(8, 2))
    total_weight_kg = fields.Float(
        string='Total Weight (kg)', digits=(8, 3),
        compute='_compute_total_weight', store=True
    )

    @api.depends('product_uom_qty', 'unit_weight_g')
    def _compute_total_weight(self):
        for r in self:
            r.total_weight_kg = (r.product_uom_qty * r.unit_weight_g) / 1000


# ══════════════════════════════════════════
#  PURCHASE ORDER EXTENSION
# ══════════════════════════════════════════
class PurchaseOrderCasting(models.Model):
    """Extends purchase.order with casting supplier management fields."""
    _inherit = 'purchase.order'

    china_supply_id     = fields.Many2one(
        'dg.china.supply', string='China Supply Order'
    )
    supplier_approved   = fields.Boolean(
        string='Supplier Approved', default=False
    )
    supplier_iso_cert   = fields.Boolean(string='Supplier ISO 9001 Certified')
    quality_gate        = fields.Boolean(
        string='Quality Gate on Receipt', default=True
    )
    is_china_order      = fields.Boolean(
        string='China Supply Order',
        compute='_compute_is_china', store=True
    )
    etd_china           = fields.Date(string='ETD (China)')
    eta_manchester      = fields.Date(string='ETA (Manchester)')
    incoterm_note       = fields.Char(
        string='Incoterms', default='FOB Shanghai'
    )
    casting_process_id  = fields.Many2one(
        'dg.casting.process', string='Casting Process'
    )
    cert_required       = fields.Boolean(
        string='CoC Required from Supplier', default=True
    )
    cert_received       = fields.Boolean(string='CoC Received')
    quarantine_required = fields.Boolean(
        string='Place in Quarantine on Arrival', default=True
    )

    @api.depends('china_supply_id', 'partner_id')
    def _compute_is_china(self):
        for r in self:
            r.is_china_order = bool(r.china_supply_id) or (
                r.partner_id.country_id.code == 'CN' if r.partner_id.country_id else False
            )


class PurchaseOrderLineCasting(models.Model):
    """Extends purchase order line with casting fields."""
    _inherit = 'purchase.order.line'

    alloy_spec        = fields.Char(string='Alloy Spec')
    casting_process_id = fields.Many2one(
        'dg.casting.process', string='Process'
    )
    unit_weight_g     = fields.Float(string='Unit Weight (g)', digits=(8, 2))
    drawing_ref       = fields.Char(string='Drawing Ref')
