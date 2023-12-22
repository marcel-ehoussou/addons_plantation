# -*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 OpenERP SA (<http://openerp.com>). All Rights Reserved

#
##############################################################################


from odoo import fields, models, api, exceptions
import math
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval



class FarmerList(models.TransientModel):
    _name = "farmer.list.wizard"
    _description = "Farmer List"


    group_id = fields.Many2one('group.prime', string='Group Prime')
    farmers_display = fields.Text(string="Liste des Planteurs", readonly=True)
    farmers_display_eligible = fields.Text(string="Liste des Planteurs eligible", readonly=True)

# class FarmerListEligible(models.TransientModel):
#     _name = "farmer.list.wizard.eligible"
#     _description = "Farmer eligible"
#
#
#     group_id = fields.Many2one('group.prime', string='Group Prime')
#     farmers_display_eligible = fields.Text(string="Liste des Planteurs eligible", readonly=True)
