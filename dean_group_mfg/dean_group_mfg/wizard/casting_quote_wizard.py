# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CastingQuoteWizard(models.TransientModel):
    """
    Multi-step wizard to build a casting quotation.
    Step 1: Select process and material
    Step 2: Confirm quantities and lead time
    Step 3: Generate quote / CRM lead
    """
    _name = 'dg.casting.quote.wizard'
    _description = 'Casting Quote Wizard'

    # ── Step 1 ────────────────────────────────────────────────
    step = fields.Integer(default=1)
    partner_id        = fields.Many2one('res.partner', string='Customer', required=True)
    contact_name      = fields.Char(string='Contact Name')
    industry          = fields.Selection([
        ('aerospace',   'Aerospace'),
        ('defence',     'Defence'),
        ('oil_gas',     'Oil & Gas'),
        ('medical',     'Medical'),
        ('rail',        'Rail & Transport'),
        ('energy',      'Energy & Power'),
        ('engineering', 'General Engineering'),
    ], string='Industry Sector')

    # ── Step 2 ────────────────────────────────────────────────
    casting_process_id = fields.Many2one('dg.casting.process', string='Casting Process')
    alloy_spec         = fields.Char(string='Material / Alloy')
    quantity_annual    = fields.Integer(string='Annual Quantity (est.)')
    weight_grams       = fields.Float(string='Part Weight (g)', digits=(8, 2))
    drawing_ref        = fields.Char(string='Drawing Reference')
    has_cad            = fields.Boolean(string='CAD Files Available')
    supply_route       = fields.Selection([
        ('uk',    'UK Foundry'),
        ('china', 'China Supply'),
        ('split', 'UK Prototype / China Production'),
    ], string='Supply Route', default='uk')
    ppap_required      = fields.Boolean(string='PPAP Required')
    special_notes      = fields.Text(string='Special Requirements')

    # ── Step 3: lead time estimate ────────────────────────────
    lead_time_estimate = fields.Integer(
        string='Estimated Lead Time (days)',
        compute='_compute_lead_time'
    )
    estimated_value    = fields.Float(
        string='Estimated Annual Value (£)', digits=(10, 2)
    )
    create_crm_lead    = fields.Boolean(string='Create CRM Lead', default=True)
    create_enquiry     = fields.Boolean(string='Create Casting Enquiry', default=True)

    @api.depends('casting_process_id', 'supply_route')
    def _compute_lead_time(self):
        for r in self:
            p = r.casting_process_id
            if not p:
                r.lead_time_estimate = 0
            elif r.supply_route == 'uk':
                r.lead_time_estimate = p.lead_time_uk or 35
            else:
                r.lead_time_estimate = p.lead_time_china or 112

    def action_next(self):
        self.step += 1
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_back(self):
        self.step = max(1, self.step - 1)
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_confirm(self):
        """Create CRM lead and/or casting enquiry from wizard data."""
        if not self.partner_id:
            raise UserError(_('Please select a customer.'))

        result_ids = []

        if self.create_enquiry:
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
                'estimated_value': self.estimated_value,
                'description':     self.special_notes,
            })

        if self.create_crm_lead:
            lead = self.env['crm.lead'].create({
                'name':            f"Casting Enquiry – {self.partner_id.name}",
                'partner_id':      self.partner_id.id,
                'contact_name':    self.contact_name,
                'casting_process_id': self.casting_process_id.id,
                'industry':        self.industry,
                'alloy_spec':      self.alloy_spec,
                'quantity_annual': self.quantity_annual,
                'planned_revenue': self.estimated_value,
                'ppap_required':   self.ppap_required,
                'supply_route':    self.supply_route,
                'description':     self.special_notes,
            })

        return {'type': 'ir.actions.act_window_close'}


class BulkCertificateWizard(models.TransientModel):
    """
    Wizard to generate certificates of conformity in bulk.
    Select multiple quality inspections and download as a zip
    in the chosen language.
    """
    _name = 'dg.bulk.cert.wizard'
    _description = 'Bulk Certificate of Conformity Wizard'

    inspection_ids = fields.Many2many(
        'dg.quality.inspection',
        string='Inspections',
        domain=[('overall_result', '=', 'pass')]
    )
    cert_language = fields.Selection([
        ('en', 'English'),
        ('zh', 'Chinese (Simplified)'),
        ('de', 'German'),
        ('fr', 'French'),
        ('ar', 'Arabic'),
    ], string='Certificate Language', default='en', required=True)
    mark_as_issued = fields.Boolean(
        string='Mark All as Issued After Printing', default=True
    )
    record_count = fields.Integer(
        string='Records Selected',
        compute='_compute_count'
    )

    @api.depends('inspection_ids')
    def _compute_count(self):
        for r in self:
            r.record_count = len(r.inspection_ids)

    def action_generate(self):
        if not self.inspection_ids:
            raise UserError(_('Please select at least one inspection record.'))

        # Set language on all selected records then print
        self.inspection_ids.write({'cert_language': self.cert_language})

        if self.mark_as_issued:
            self.inspection_ids.write({'certificate_issued': True})

        return self.env.ref(
            'dean_group_mfg.action_report_quality_cert'
        ).report_action(self.inspection_ids)
