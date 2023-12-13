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



class PrimeConfig(models.Model):
    _name = "prime.config"

    name = fields.Char(string="Libellé")
    date_debut = fields.Date(string="Date début")
    date_fin = fields.Date(string="Date fin")
    group_id = fields.Many2one( "group.prime" , string="Groupe prime")


    def update_weight_seuils(self):
        weight_obj = self.env['weight.weight']
        # Recherche des enregistrements de Weight concernés
        # en fonction du groupe dans PrimeConfig
        weights = weight_obj.search([('supplier_id.group_id', '=', self.group_id.id)])
        # Mise à jour des seuils dans chaque enregistrement de Weight
        weights.update_seuil_atteindre()

    def action_confirm(self):
        farmers_to_display = []
        for weight in self:
            group_prime = weight.group_id
            if group_prime and group_prime.date_debut <= weight.date_debut <= group_prime.date_fin:
                seuil_prime = self.env['seuil.prime'].search([('group_id', '=', group_prime.id)], limit=1)
                if seuil_prime and weight.qty >= seuil_prime.seuil_tone_1:
                    # Obtenir tous les planteurs associés au groupe
                    farmers = self.env['group.prime'].search([('group_id', '=', group_prime.id)])
                    # Ajouter les planteurs qui remplissent la condition à la liste farmers_to_display
                    farmers_to_display.extend(farmer.name for farmer in farmers)

        # Faites ce que vous voulez avec la liste farmers_to_display, par exemple, l'afficher
        print("Farmers meeting the condition:", farmers_to_display)

        return farmers_to_display


class GroupPrime(models.Model):
    _name = "group.prime"
    _description = " Groupe de prix"
    _rec_naame = "name"

    date_debut = fields.Date(string="Date début")
    date_fin = fields.Date(string="Date fin")
    name = fields.Char(string='Groupe',required=True)
    line_farmer_ids = fields.One2many(comodel_name="res.partner", inverse_name="prime_id", string="Planteurs", required=False,)
    seuil_ids = fields.One2many(comodel_name="seuil.prime", inverse_name="group_id", string="Seuil", required=False,)
    line_ids = fields.One2many(comodel_name="planting.pricing.prime", inverse_name="group_id", string="Prix Planteurs", required=False,)

class SeuilPrime(models.Model):
    _name = "seuil.prime"

    seuil_tone_1 = fields.Float(string="Seuil primaire")
    seuil_ton_2 = fields.Float(string="Seuil secondaire ")
    seuil_atteindre_1 = fields.Float(string="Seuil atteindre primaire")
    seuil_atteindre_2 = fields.Float(string="Seuil atteindre secondaire")
    group_id = fields.Many2one(comodel_name='group.prime',string=' ',required=True, ondelete="cascade")




class PlantingPrime(models.Model):
    _name = "planting.prime"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Historique Prix Planteurs"
    _order = "date desc"

    # @api.model
    # def default_get(self, values):
    #     res = super(PlantingPrime, self).default_get(values)
    #     if 'date' in values:
    #         res['name'] = "Prix Planteur " + time.strftime('%d/%m/%Y')
    #     return res

    name = fields.Char(string='Periode de prix', required=True)
    date = fields.Date(string='Date', required=True)
    # date = fields.Date(string='Date', required=True, default=lambda *a: time.strftime('%Y-%m-%d'))
    line_ids = fields.One2many(comodel_name='planting.pricing.prime',inverse_name='price_id', tracking=True, string='Ligne de prix',required=False)

    # @api.onchange('date')
    # def onchange_date(self):
    #     if self.date:
    #         self.name = "Prix Planteur " + self.date.strftime('%d/%m/%Y')


class PlantingPricingPrime(models.Model):
    _name = "planting.pricing.prime"
    _description = "Ligne Prix Planteurs"
    _order = "date desc"

    price_id = fields.Many2one(comodel_name='planting.prime',string='Historique prix ',required=True, ondelete="cascade")
    group_id = fields.Many2one(comodel_name='group.prime',string='Groupe planteur',required=True)
    price = fields.Float(string='Prix Achat', digits="Product Unit Of Measure", required=True,)
    price_driver = fields.Float(string='Transport (T)', digits="Product Unit Of Measure", required=True,)
    prime = fields.Float(string='Prime', digits="Product Unit Of Measure", required=True,)
    date = fields.Date(string='Date', related="price_id.date")


class PrimeExecpionnelle(models.Model):
    _name = "prime.exceptionnele"

    name = fields.Char(string="Prime")
    date_debut = fields.Date(string="Date début")
    date_fin = fields.Date(string="Date fin")
