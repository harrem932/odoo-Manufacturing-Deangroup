# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class FoundryEmployee(models.Model):
    _inherit = 'hr.employee'

    foundry_skill = fields.Selection([
        ('casting',     'Casting Operative'),
        ('wax',         'Wax Room'),
        ('shell',       'Shell Room'),
        ('quality',     'Quality Inspector'),
        ('machinist',   'CNC Machinist'),
        ('maintenance', 'Maintenance Engineer'),
        ('engineering', 'Process Engineer'),
        ('sales',       'Sales & Commercial'),
        ('admin',       'Administration'),
        ('management',  'Management'),
    ])
    shift = fields.Selection([
        ('day',   'Day   06:00–14:00'),
        ('late',  'Late  14:00–22:00'),
        ('night', 'Night 22:00–06:00'),
        ('office','Office 08:00–17:30'),
    ], default='day')
    employee_type = fields.Selection([
        ('permanent',  'Permanent'),
        ('apprentice', 'Apprentice'),
        ('contract',   'Contractor'),
        ('agency',     'Agency'),
    ], default='permanent')
    site = fields.Selection([
        ('manchester', 'Manchester – UK Foundry'),
        ('china',      'China Partner Site'),
        ('remote',     'Remote / Field'),
    ], default='manchester')
    nvq_level = fields.Selection([
        ('none','None'),('1','NVQ 1'),('2','NVQ 2'),
        ('3','NVQ 3'),('4','NVQ 4 / HNC'),('5','Degree+'),
    ], default='none')
    ppe_certified         = fields.Boolean(string='PPE Training Complete')
    health_surveillance   = fields.Date(string='Next Health Surveillance')
    apprenticeship_start  = fields.Date()
    apprenticeship_end    = fields.Date()


class JobApplicationExt(models.Model):
    _inherit = 'hr.applicant'

    applied_via = fields.Selection([
        ('website',  'Dean Group Website'),
        ('indeed',   'Indeed'),
        ('linkedin', 'LinkedIn'),
        ('referral', 'Employee Referral'),
        ('agency',   'Recruitment Agency'),
        ('walk_in',  'Walk-In'),
    ], default='website')
    is_apprentice          = fields.Boolean(string='Apprenticeship Application')
    has_foundry_experience = fields.Boolean(string='Previous Foundry Experience')
    notice_period_weeks    = fields.Integer(string='Notice Period (weeks)')
    expected_salary        = fields.Float(string='Expected Salary (£)', digits=(10,2))
