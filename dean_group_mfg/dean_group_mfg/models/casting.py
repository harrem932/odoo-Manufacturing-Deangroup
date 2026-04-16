# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CastingProcess(models.Model):
    _name = 'dg.casting.process'
    _description = 'Casting Process Type'
    _order = 'sequence, name'

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    code = fields.Selection([
        ('investment', 'Investment Casting'),
        ('die',        'Die Casting'),
        ('aluminium',  'Aluminium Casting (ELITE)'),
        ('forging',    'Forging'),
        ('mim',        'MIM / Powder Pressing'),
        ('printing',   '3D Printing for Casting'),
        ('machining',  'Machining & Finishing'),
    ], required=True)
    description = fields.Text(translate=True)
    supply_location = fields.Selection([
        ('uk',    'UK Foundry – Manchester'),
        ('china', 'China Partner'),
        ('both',  'UK + China'),
    ], default='uk')
    lead_time_uk    = fields.Integer(string='UK Lead Time (days)')
    lead_time_china = fields.Integer(string='China Lead Time (days)')
    min_quantity    = fields.Integer(string='Min Batch Qty')
    max_tolerance   = fields.Float(string='Max Tolerance (mm)', digits=(4, 4))
    website_url     = fields.Char(string='Website Page URL')
    active = fields.Boolean(default=True)
    color  = fields.Integer()

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Process code must be unique.')
    ]


class CastingEnquiry(models.Model):
    _name = 'dg.casting.enquiry'
    _description = 'Casting Enquiry'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _rec_name = 'name'

    name = fields.Char(
        string='Reference', required=True, copy=False,
        readonly=True, default=lambda self: _('New')
    )
    partner_id   = fields.Many2one('res.partner', string='Customer', required=True, tracking=True)
    contact_name = fields.Char(string='Contact Name')
    email        = fields.Char(related='partner_id.email', readonly=True)
    phone        = fields.Char(related='partner_id.phone', readonly=True)

    process_id = fields.Many2one('dg.casting.process', string='Process', tracking=True)
    industry   = fields.Selection([
        ('aerospace',   'Aerospace'),
        ('defence',     'Defence'),
        ('oil_gas',     'Oil & Gas'),
        ('medical',     'Medical'),
        ('rail',        'Rail & Transport'),
        ('energy',      'Energy & Power'),
        ('automotive',  'Automotive'),
        ('architecture','Architecture'),
        ('engineering', 'General Engineering'),
    ], string='Industry', tracking=True)

    material        = fields.Char(string='Material / Alloy')
    quantity_annual = fields.Integer(string='Annual Qty (est.)')
    weight_grams    = fields.Float(string='Part Weight (g)', digits=(8, 2))
    drawing_ref     = fields.Char(string='Drawing Ref')
    has_cad         = fields.Boolean(string='CAD File Provided')
    description     = fields.Text(string='Component Description')

    supply_route = fields.Selection([
        ('uk',    'UK Foundry'),
        ('china', 'China Supply'),
        ('split', 'UK Prototype / China Production'),
    ], string='Supply Route')

    estimated_value = fields.Float(string='Est. Annual Value (£)', digits=(10, 2))

    state = fields.Selection([
        ('new',       'New Enquiry'),
        ('review',    'Under Review'),
        ('quoted',    'Quoted'),
        ('sampling',  'Sampling / First Article'),
        ('approved',  'Approved – Active'),
        ('lost',      'Lost'),
        ('cancelled', 'Cancelled'),
    ], default='new', tracking=True, group_expand='_expand_states')

    priority = fields.Selection([
        ('0', 'Normal'), ('1', 'Urgent'), ('2', 'Critical')
    ], default='0')

    sale_order_id = fields.Many2one('sale.order',  string='Sale Order')
    crm_lead_id   = fields.Many2one('crm.lead',    string='CRM Lead')
    company_id    = fields.Many2one('res.company', default=lambda s: s.env.company)
    user_id       = fields.Many2one('res.users',   default=lambda s: s.env.user,
                                    string='Sales Engineer')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = (
                    self.env['ir.sequence'].next_by_code('dg.casting.enquiry') or _('New')
                )
        return super().create(vals_list)

    def action_set_review(self):   self.write({'state': 'review'})
    def action_set_quoted(self):   self.write({'state': 'quoted'})
    def action_set_approved(self): self.write({'state': 'approved'})
    def action_set_lost(self):     self.write({'state': 'lost'})

    @api.model
    def _expand_states(self, states, domain, order):
        return [k for k, _ in self._fields['state'].selection]


class FoundryWorkOrderExt(models.Model):
    """Extends mrp.workorder with casting-specific fields."""
    _inherit = 'mrp.workorder'

    casting_process_id = fields.Many2one('dg.casting.process', string='Casting Process')
    mould_ref          = fields.Char(string='Mould / Tool Ref')
    heat_lot           = fields.Char(string='Heat / Lot No.')
    wax_weight_g       = fields.Float(string='Wax Weight (g)', digits=(8, 2))
    metal_weight_g     = fields.Float(string='Metal Weight (g)', digits=(8, 2))
    yield_pct          = fields.Float(
        string='Yield %', digits=(5, 2),
        compute='_compute_yield', store=True
    )
    supply_site = fields.Selection([
        ('manchester', 'Manchester – UK Foundry'),
        ('china',      'China Partner'),
    ], default='manchester', string='Production Site')
    inspection_result = fields.Selection([
        ('pending', 'Pending'),
        ('pass',    'Pass'),
        ('fail',    'Fail – Rework'),
        ('scrap',   'Scrap'),
    ], default='pending', string='Inspection')

    @api.depends('wax_weight_g', 'metal_weight_g')
    def _compute_yield(self):
        for r in self:
            if r.wax_weight_g:
                r.yield_pct = (r.metal_weight_g / r.wax_weight_g * 100) if r.metal_weight_g else 0
            else:
                r.yield_pct = 0
