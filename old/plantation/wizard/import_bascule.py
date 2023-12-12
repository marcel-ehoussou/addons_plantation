    # -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Business Applications
#    Copyright (C) 2004-2012 OpenERP S.A. (<http://openerp.com>).
##############################################################################

from odoo import fields, models,api,exceptions

class Weight(models.Model):
    _name = 'weight.weight'
    _description = 'Weight'

    name = fields.Char("Ticket pesée",readonly=False)
    carrier = fields.Char("N° de Vehicule",readonly=False)
    driver = fields.Char("Chauffeur",readonly=False)
    first_weigher = fields.Char("Peseur",readonly=False)
    code_product = fields.Char(string='Code produit', required=True)
    code_farmer = fields.Char(string='Matricule planteur', required=True)
    locality = fields.Char(string='Localité', required=False)
    sector = fields.Char(string='Secteur', required=False)
    village = fields.Char(string='Village', required=False)
    date = fields.Date(string='Date livraison', required=True,readonly=False)
    supplier_id = fields.Many2one(comodel_name='res.partner',string='Planteurs',required=False,readonly=True)
    product_id = fields.Many2one(comodel_name='product.template',string='Article',required=False,readonly=True)
    weigth_1 = fields.Float(string='Pesée 1')
    weigth_2 = fields.Float(string='Pesée 2')
    qty = fields.Float(string='Poids Net', required=True)
    weigth_supplier = fields.Float(string='Poids du Fournisseur')
    state = fields.Selection(string='Etat',selection=[('draft', 'Brouillon'),('done', 'Valider')], required=True, default="draft",readonly=True)

    def unlink(self):
        for r in self:
            if r.state != "draft":
                raise exceptions.ValidationError("Vous ne pouvez pas supprimer une pesée qui n'est pas l'étape brouillon")
        super().unlink()

    def cancel(self):
        return self.write({'state':'draft'})


    def find_partner(self, supplier,product):
        supplier_id = self.env['res.partner'].search([('ref', '=', supplier)], limit=1)
        product_id = self.env['product.template'].search([('code', '=',product)],limit=1)
        if not supplier_id:
            raise exceptions.UserError("Le code Planteur [%s]  n'existe pas !" % (supplier))
        if not product_id :
            raise exceptions.UserError("Le code produit [%s]  n'existe pas !" % (product))

        return supplier_id.id,product_id.id

    def action_confirm(self):
        res = self.search([('state', '=', 'draft')])
        for rec in res :
            partner = self.find_partner(rec.code_farmer,rec.code_product)
            rec.supplier_id = partner[0]
            rec.product_id = partner[1]
            self.env['farmer.pay'].create({
                'name': rec.name,
                'date': rec.date,
                'farmer_id': partner[0],
                'product_id': partner[1],
                'qty': rec.qty
            })
            rec.write({'state': 'done'})
        return {"view_mode": 'tree,form', 'name': 'Planteur à payer',
                'res_model': 'farmer.pay', 'type': 'ir.actions.act_window', }

class FarmerPay(models.Model):

    _name = 'farmer.pay'
    _description = 'Verification des planteurs à payer'

    name = fields.Char('Numero de ticket', size=20, required=True, readonly=True)
    farmer_id = fields.Many2one('res.partner', 'Planteur', required=False, readonly=True)
    product_id = fields.Many2one('product.template','Produit', required=False, readonly=True)
    qty = fields.Float(string='Poids net', required=True, readonly=True)
    date = fields.Date(string='Date', required=True, readonly=True)
    state = fields.Selection(string='Statut', selection=[('un_paid', 'Non Payé'), ('paid', 'Payé')], default="un_paid", required=False, readonly=True)

