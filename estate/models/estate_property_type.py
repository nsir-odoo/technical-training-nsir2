from odoo import models,fields

class Type(models.Model):
    _name='estate.property.type'
    _description='Estate property type description'
    _order="sequence,name"

    name=fields.Char(required=True)

    sequence=fields.Integer()

    property_ids=fields.One2many("estate.property","property_type_id",string="Props")

    offer_ids=fields.One2many("estate.property.offer","property_type_id")
    offer_count=fields.Integer(compute="_compute_offer")

    #SQL Constraints
    _sql_constraints=[('check_type_name','UNIQUE(name)','Property type should be unique')]

    def _compute_offer(self):
        for offer in self:
            offer.offer_count = len(offer.offer_ids)