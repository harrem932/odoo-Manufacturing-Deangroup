# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class CrmLeadCasting(models.Model):
    """Extends crm.lead with casting-specific commercial fields."""
    _inherit = 'crm.lead'

    # ── Casting details ───────────────────────────────────────
    casting_process_id = fields.Many2one(
        'dg.casting.process', string='Process Required'
    )
    industry = fields.Selection([
        ('aerospace',    'Aerospace'),
        ('defence',      'Defence'),
        ('oil_gas',      'Oil & Gas'),
        ('medical',      'Medical'),
        ('rail',         'Rail & Transport'),
        ('energy',       'Energy & Power'),
        ('automotive',   'Automotive'),
        ('architecture', 'Architecture'),
        ('engineering',  'General Engineering'),
    ], string='Industry Sector')
    alloy_spec       = fields.Char(string='Material / Alloy')
    quantity_annual  = fields.Integer(string='Annual Quantity (est.)')
    weight_grams     = fields.Float(string='Part Weight (g)', digits=(8, 2))
    drawing_ref      = fields.Char(string='Drawing / Part Reference')
    has_cad          = fields.Boolean(string='CAD Files Available')
    supply_route     = fields.Selection([
        ('uk',    'UK Foundry'),
        ('china', 'China Supply'),
        ('split', 'UK Prototype / China Production'),
    ], string='Preferred Supply Route')

    # ── Commercial ────────────────────────────────────────────
    ppap_required  = fields.Boolean(string='PPAP Required')
    ppap_level     = fields.Selection([
        ('1','Level 1'),('2','Level 2'),('3','Level 3'),
        ('4','Level 4'),('5','Level 5'),
    ], string='PPAP Level')
    nda_signed     = fields.Boolean(string='NDA Signed')
    cert_standard  = fields.Selection([
        ('iso9001',  'ISO 9001:2015'),
        ('as9100',   'AS9100 (Aerospace)'),
        ('iso13485', 'ISO 13485 (Medical)'),
        ('iatf',     'IATF 16949 (Automotive)'),
        ('other',    'Other / TBC'),
    ], string='Quality Standard Required')

    # ── Source ────────────────────────────────────────────────
    lead_source = fields.Selection([
        ('website',    'Dean Group Website'),
        ('referral',   'Customer Referral'),
        ('exhibition', 'Exhibition / Trade Show'),
        ('linkedin',   'LinkedIn'),
        ('cold_call',  'Cold Call'),
        ('returning',  'Returning Customer'),
        ('zenvora',    'Zenvora Lead Gen'),
    ], string='Lead Source')
    enquiry_id = fields.Many2one(
        'dg.casting.enquiry', string='Linked Enquiry'
    )

    # ── Computed helpers ──────────────────────────────────────
    annual_value_est = fields.Float(
        string='Est. Annual Value (£)',
        compute='_compute_annual_value', store=True, digits=(10, 2)
    )

    @api.depends('quantity_annual', 'planned_revenue')
    def _compute_annual_value(self):
        for r in self:
            # Use planned_revenue if set, otherwise estimate from qty
            r.annual_value_est = r.planned_revenue or 0.0

    def action_create_casting_enquiry(self):
        """Convert CRM lead into a formal casting enquiry."""
        enquiry = self.env['dg.casting.enquiry'].create({
            'partner_id':      self.partner_id.id,
            'contact_name':    self.contact_name,
            'process_id':      self.casting_process_id.id,
            'industry':        self.industry,
            'material':        self.alloy_spec,
            'quantity_annual': self.quantity_annual,
            'weight_grams':    self.weight_grams,
            'drawing_ref':     self.drawing_ref,
            'has_cad':         self.has_cad,
            'supply_route':    self.supply_route,
            'crm_lead_id':     self.id,
            'estimated_value': self.planned_revenue or 0,
            'description':     self.description,
        })
        self.enquiry_id = enquiry
        return {
            'type': 'ir.actions.act_window',
            'name': _('Casting Enquiry'),
            'res_model': 'dg.casting.enquiry',
            'res_id': enquiry.id,
            'view_mode': 'form',
        }
