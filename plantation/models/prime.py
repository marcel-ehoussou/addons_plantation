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
    farmers_display = fields.Text(string="Liste des Planteurs", readonly=True)
    farmers_bonus_1 = fields.Char(string="Bonus des Planteurs", readonly=True)
    farmers_bonus_2 = fields.Char(string="Bonus des Planteurs ¤ ", readonly=True)
    farmers_name_bonus = fields.Char(string="Bonus des Planteurs", readonly=True)

    def get_farmers_by_group(self):
        farmers_by_group = []
        for config in self:
            if config.group_id:
                group_prime = config.group_id
                farmers = group_prime.line_farmer_ids
                farmers_data = "\n".join([f"{farmer.name}" for farmer in farmers])
                config.write({'farmers_display': farmers_data})
                # Créez un enregistrement temporaire pour stocker la liste des planteurs
                farmer_list = self.env['farmer.list.wizard'].create({'farmers_display': farmers_data})

                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Liste des Planteurs',
                    'view_mode': 'form',
                    'res_model': 'farmer.list.wizard',
                    'res_id': farmer_list.id,
                    'target': 'new',
                }


    def calculate_bonus_for_period(self):
        if self.group_id:
            group_prime = self.group_id
            # Recherchez le seuil correspondant dans le groupe
            seuil_prime = self.env['seuil.prime'].search([('group_id', '=', group_prime.id)], limit=1)
            print(">>>> seuil", seuil_prime)
            # Vérifiez si le seuil a été trouvé
            if seuil_prime:
                eligible_farmers = []  # Liste pour stocker les planteurs éligibles
                farmers_bonus_1 = []  # Liste pour stocker les bonus_amount
                farmers_bonus_2 = []  # Liste pour stocker les bonus_amount
                farmers_name_bonus = []  # Liste pour stocker les name_planteur
                # Parcourez chaque planteur du groupe
                for farmer in group_prime.line_farmer_ids:
                    # Recherchez les enregistrements de poids du planteur dans la période donnée
                    weights = self.env['weight.weight'].search([
                        ('supplier_id', '=', farmer.id),
                        ('date', '>=', self.date_debut),
                        ('date', '<=', self.date_fin),
                    ])
                    print(f">>>> Peseur pour {farmer.name}", weights)
                    total_qty = sum(weight.qty for weight in weights)
                    print(f">>>> Total Calcul pour {farmer.name}", total_qty)
                    # Vérifiez si la quantité totale est égale ou supérieure à seuil_tone_1
                    if total_qty >= seuil_prime.seuil_tone_1:
                        # Si oui, attribuez le bonus seuil_atteindre_1 en pourcentage
                        bonus_percentage = seuil_prime.seuil_atteindre_1
                        print(f">>>> Bonus pour 1 {farmer.name}", bonus_percentage)
                    else:
                        # Sinon, attribuez le bonus seuil_atteindre_2 en pourcentage
                        bonus_percentage = seuil_prime.seuil_atteindre_2
                        print(f">>>> Bonus pour 2 {farmer.name}", bonus_percentage)
                    # Calculez le bonus en fonction du pourcentage et de la quantité totale
                    bonus_amount = (bonus_percentage / 100) * total_qty
                    print("bonus amount" , bonus_amount , farmer.name)
                    # Ajoutez le planteur éligible à la liste si le bonus est supérieur à 0
                    if bonus_amount > 0:
                        eligible_farmers.append(farmer.name)
                        # Ajoutez bonus_amount et name_planteur aux listes respectives
                        farmers_bonus_1.append(bonus_amount)
                        name_planteur = f" Pour ({farmer.name}): {bonus_amount}"
                        farmers_name_bonus.append(name_planteur)
                # Mettez à jour les champs avec les valeurs calculées
                self.write({
                    'farmers_bonus_1': "\n".join(map(str, farmers_bonus_1)),
                    'farmers_bonus_2': "\n".join(map(str, farmers_bonus_2)),
                    'farmers_name_bonus': "\n".join(farmers_name_bonus),
                })
                # Retournez la liste des planteurs éligibles
                return eligible_farmers
        return []  # Retournez une liste vide si aucune condition n'est remplie





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

    seuil_tone_1 = fields.Float(string="Seuil à atteindre")
    seuil_ton_2 = fields.Float(string="Seuil secondaire " , invisible=True)
    seuil_atteindre_1 = fields.Float(string="Bonus seuil primaire")
    seuil_atteindre_2 = fields.Float(string="Bonus seuil secondaire")
    group_id = fields.Many2one(comodel_name='group.prime',string=' ', ondelete="cascade")




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
    prime_obtenu = fields.Char(string="Prime")


class PrimeExecpionnelle(models.Model):
    _name = "prime.exceptionnele"

    name = fields.Char(string="Prime")
    date_debut = fields.Date(string="Date début")
    date_fin = fields.Date(string="Date fin")
    prime_obtenu = fields.Char(string="Prime")
    farmers_display_eligible = fields.Text(string="Liste des Planteurs éligibles", readonly=True)

    def display_eligible_farmers(self):
        eligible_farmers = []
        # Remplacez "date_debut" et "date_fin" par les dates appropriées
        date_debut = self.date_debut
        date_fin = self.date_fin
        # Recherchez tous les enregistrements de PrimeConfig dans la période donnée
        prime_configs = self.env['prime.config'].search([
            ('date_debut', '<=', date_debut),
            ('date_fin', '>=', date_fin),
        ])
        # Parcourez chaque enregistrement de PrimeConfig
        for config in prime_configs:
            bonus_amount = config.calculate_bonus_for_period()
            if bonus_amount > 0:
                eligible_farmers.extend([farmer.name for farmer in config.group_id.line_farmer_ids])
        # Supprimez les doublons de la liste des planteurs éligibles
        eligible_farmers = list(set(eligible_farmers))
        # Stockez la liste des planteurs éligibles dans le champ farmers_display_eligible
        self.farmers_display_eligible = "\n".join(eligible_farmers)

        # Vous pouvez faire ce que vous voulez avec la liste des planteurs éligibles, par exemple, l'afficher
        # ou la stocker dans un champ
