# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class MrpProductionCasting(models.Model):
    """
    Extends mrp.production with casting-specific fields.
    This is the core replacement for Dean Group's MS Access production database.
    """
    _inherit = 'mrp.production'

    # ── Casting identification ────────────────────────────────
    casting_process_id = fields.Many2one(
        'dg.casting.process', string='Casting Process',
        tracking=True
    )
    enquiry_id = fields.Many2one(
        'dg.casting.enquiry', string='Casting Enquiry',
        tracking=True
    )
    supply_site = fields.Selection([
        ('manchester', 'UK Foundry – Manchester'),
        ('china',      'China Partner'),
    ], string='Production Site', default='manchester', tracking=True)

    # ── Casting material ──────────────────────────────────────
    alloy_spec      = fields.Char(string='Alloy / Material Spec')
    heat_lot_no     = fields.Char(string='Heat / Lot Number')
    mould_tool_ref  = fields.Char(string='Mould / Tool Reference')
    drawing_rev     = fields.Char(string='Drawing Revision')

    # ── Wax & metal weights (investment casting) ───────────────
    wax_weight_g    = fields.Float(string='Wax Pattern Weight (g)', digits=(8, 2))
    metal_weight_g  = fields.Float(string='Poured Metal Weight (g)', digits=(8, 2))
    casting_yield   = fields.Float(
        string='Casting Yield %', digits=(5, 1),
        compute='_compute_yield', store=True
    )

    # ── Quality gate ──────────────────────────────────────────
    ppap_required       = fields.Boolean(string='PPAP Required')
    ppap_level          = fields.Selection([
        ('1','Level 1'),('2','Level 2'),('3','Level 3'),
        ('4','Level 4'),('5','Level 5'),
    ], string='PPAP Level')
    first_article       = fields.Boolean(string='First Article Inspection')
    cert_language       = fields.Selection([
        ('en','English'),('zh','Chinese'),
        ('de','German'),('fr','French'),('ar','Arabic'),
    ], string='CoC Language', default='en')
    quality_hold        = fields.Boolean(string='Quality Hold', tracking=True)
    quality_hold_reason = fields.Text(string='Hold Reason')

    # ── Scrap & rework ────────────────────────────────────────
    qty_scrapped  = fields.Float(string='Qty Scrapped',  digits=(8, 2))
    qty_reworked  = fields.Float(string='Qty Reworked',  digits=(8, 2))
    scrap_cost    = fields.Float(string='Scrap Cost (£)', digits=(10, 2))
    ncr_ref       = fields.Char(string='NCR Reference')

    # ── Customer & delivery ───────────────────────────────────
    customer_id        = fields.Many2one(
        'res.partner', string='End Customer',
        domain=[('customer_rank', '>', 0)]
    )
    customer_order_ref = fields.Char(string='Customer PO Reference')
    delivery_deadline  = fields.Date(string='Customer Delivery Deadline')

    @api.depends('wax_weight_g', 'metal_weight_g')
    def _compute_yield(self):
        for r in self:
            if r.wax_weight_g and r.metal_weight_g:
                r.casting_yield = (r.metal_weight_g / r.wax_weight_g) * 100
            else:
                r.casting_yield = 0.0

    def action_place_quality_hold(self):
        self.write({'quality_hold': True})
        self.message_post(
            body=_('⚠️ Quality hold placed on this manufacturing order.'),
            message_type='notification'
        )

    def action_release_quality_hold(self):
        self.write({'quality_hold': False, 'quality_hold_reason': False})
        self.message_post(
            body=_('✅ Quality hold released.'),
            message_type='notification'
        )


class MrpBomCasting(models.Model):
    """Extends BOM with casting-specific fields."""
    _inherit = 'mrp.bom'

    casting_process_id = fields.Many2one(
        'dg.casting.process', string='Casting Process'
    )
    alloy_spec   = fields.Char(string='Alloy Specification')
    tool_ref     = fields.Char(string='Tool / Mould Reference')
    surface_treatment = fields.Selection([
        ('none',      'As-Cast'),
        ('shot_blast','Shot Blast'),
        ('machined',  'Machined'),
        ('plated',    'Plated'),
        ('anodised',  'Anodised'),
        ('painted',   'Painted'),
        ('heat_treat','Heat Treated'),
    ], string='Surface Treatment', default='none')
    ppap_required = fields.Boolean(string='PPAP Required on First Run')
    supply_site   = fields.Selection([
        ('manchester', 'UK Foundry'),
        ('china',      'China Partner'),
        ('either',     'Either – Cost Dependent'),
    ], default='manchester', string='Preferred Supply Site')
    notes = fields.Text(string='Engineering Notes')


class MrpRoutingCasting(models.Model):
    """Casting-specific routing operations."""
    _inherit = 'mrp.routing.workcenter'

    casting_step = fields.Selection([
        ('wax',       'Wax Injection'),
        ('assembly',  'Wax Assembly / Tree'),
        ('shell',     'Shell Dipping'),
        ('dewax',     'Dewax / Autoclave'),
        ('burnout',   'Shell Burnout'),
        ('casting',   'Metal Pouring'),
        ('knockout',  'Knock-Out / Cutoff'),
        ('shot_blast','Shot Blast'),
        ('inspection','Dimensional Inspection'),
        ('machining', 'CNC Machining'),
        ('finishing', 'Surface Finishing'),
        ('final_qc',  'Final QC & Release'),
        ('packing',   'Packing & Despatch'),
    ], string='Casting Step')
    temperature_c   = fields.Float(string='Process Temp (°C)', digits=(6, 1))
    dwell_time_min  = fields.Float(string='Dwell Time (min)', digits=(6, 1))
    operator_count  = fields.Integer(string='Operators Required', default=1)
