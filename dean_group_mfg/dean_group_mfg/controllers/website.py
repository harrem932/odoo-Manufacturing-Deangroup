# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class DeanGroupWebsite(http.Controller):

    # ── Homepage ────────────────────────────────────────────
    @http.route('/', type='http', auth='public', website=True)
    def homepage(self, **kw):
        processes = request.env['dg.casting.process'].sudo().search([('active','=',True)])
        return request.render('dean_group_mfg.homepage', {
            'processes': processes,
        })

    # ── Services ────────────────────────────────────────────
    @http.route('/services', type='http', auth='public', website=True)
    def services(self, **kw):
        processes = request.env['dg.casting.process'].sudo().search([('active','=',True)])
        return request.render('dean_group_mfg.services_page', {
            'processes': processes,
        })

    # ── Markets ─────────────────────────────────────────────
    @http.route('/markets', type='http', auth='public', website=True)
    def markets(self, **kw):
        return request.render('dean_group_mfg.markets_page', {})

    # ── Careers ─────────────────────────────────────────────
    @http.route('/careers', type='http', auth='public', website=True)
    def careers(self, **kw):
        jobs = request.env['hr.job'].sudo().search([
            ('no_of_recruitment', '>', 0)
        ])
        return request.render('dean_group_mfg.careers_page', {
            'jobs': jobs,
        })

    # ── Contact ─────────────────────────────────────────────
    @http.route('/contact', type='http', auth='public', website=True)
    def contact(self, **kw):
        return request.render('dean_group_mfg.contact_page', {})

    # ── Contact form submit ──────────────────────────────────
    @http.route('/contact/submit', type='http', auth='public', website=True,
                methods=['POST'], csrf=True)
    def contact_submit(self, **post):
        # Create CRM lead from website enquiry
        vals = {
            'name': f"Website Enquiry – {post.get('company', post.get('name',''))}",
            'contact_name': post.get('name', ''),
            'email_from':   post.get('email', ''),
            'phone':        post.get('phone', ''),
            'description':  post.get('message', ''),
            'tag_ids': [],
        }
        request.env['crm.lead'].sudo().create(vals)
        return request.render('dean_group_mfg.contact_thanks', {})

    # ── Quote request ────────────────────────────────────────
    @http.route('/get-quote', type='http', auth='public', website=True)
    def get_quote(self, **kw):
        processes = request.env['dg.casting.process'].sudo().search([('active','=',True)])
        return request.render('dean_group_mfg.quote_page', {
            'processes': processes,
        })

    @http.route('/get-quote/submit', type='http', auth='public', website=True,
                methods=['POST'], csrf=True)
    def quote_submit(self, **post):
        process = request.env['dg.casting.process'].sudo().browse(
            int(post.get('process_id', 0))
        )
        vals = {
            'name': _new_ref(request),
            'contact_name': post.get('name', ''),
            'email_from':   post.get('email', ''),
            'phone':        post.get('phone', ''),
            'description': (
                f"Process: {process.name if process else post.get('process','')}\n"
                f"Material: {post.get('material','')}\n"
                f"Quantity: {post.get('quantity','')}\n"
                f"Details: {post.get('details','')}"
            ),
        }
        request.env['crm.lead'].sudo().create(vals)
        return request.render('dean_group_mfg.quote_thanks', {})


def _new_ref(request):
    seq = request.env['ir.sequence'].sudo().next_by_code('dg.casting.enquiry')
    return seq or 'Website Enquiry'


class DeanGroupWebsiteExtra(http.Controller):

    @http.route('/services', type='http', auth='public', website=True)
    def services(self, **kw):
        processes = request.env['dg.casting.process'].sudo().search(
            [('active', '=', True)], order='sequence'
        )
        return request.render('dean_group_mfg.services_page', {'processes': processes})

    @http.route('/markets', type='http', auth='public', website=True)
    def markets(self, **kw):
        return request.render('dean_group_mfg.markets_page', {})

    @http.route('/about', type='http', auth='public', website=True)
    def about(self, **kw):
        return request.render('dean_group_mfg.about_page', {})

    @http.route('/quality', type='http', auth='public', website=True)
    def quality(self, **kw):
        return request.render('dean_group_mfg.quality_page', {})

    @http.route('/terms-and-conditions', type='http', auth='public', website=True)
    def terms(self, **kw):
        return request.render('dean_group_mfg.terms_page', {})

    @http.route('/privacy-policy', type='http', auth='public', website=True)
    def privacy(self, **kw):
        return request.render('dean_group_mfg.privacy_page', {})
