from odoo import fields, models, api
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare

class Offer(models.Model):
    _name='estate.property.offer'
    _description='Estate property offer description'
    _order="price desc"

    price=fields.Float()
    status=fields.Selection(selection=[('accepted','Accepted'),('refused','Refused')],copy=False,readonly=True)
    partner_id=fields.Many2one("res.partner",required=True,string="Buyer")
    property_id=fields.Many2one("estate.property",required=True,readonly=True)

    validity=fields.Integer(default=7)
    date_deadline=fields.Date(compute='_compute_deadline', inverse='_inverse_compute_deadline')

    property_type_id=fields.Many2one('estate.property.type',related='property_id.property_type_id', store=True)

    @api.depends('validity')
    def _compute_deadline(self):
        for offer in self:
            offer.date_deadline=fields.Date.today()+relativedelta(days=offer.validity)

    #Inverse Function
    def _inverse_compute_deadline(self):
        for offer in self:
            if offer.date_deadline:
                offer.validity=(offer.date_deadline-fields.Date.today()).days

    # Buttons
    def action_accept_button(self):
        for offer in self:
            if offer.property_id.selling_price != 0 :
                raise UserError("Already accepted an offer!")
            else:
                offer.status='accepted'
                offer.property_id.selling_price=offer.price
                offer.property_id.buyer_id=offer.partner_id
                offer.property_id.state="offer accepted"
            for it in offer.property_id.offer_ids:
                if(it.status!='accepted'):
                    it.status='refused'
        return True
    
    def action_refuse_button(self):
        for offer in self:
            if offer.property_id.selling_price != 0 and offer.status=='accepted':
                offer.property_id.selling_price=0
                offer.property_id.buyer_id=""
            offer.status='refused'
        return True
    
    # SQL Constraints
    _sql_constraints=[('check_price','CHECK(price > 0)','The offer price must be strictly positive')]
    
    @api.model
    def create(self,vals):
        property=self.env['estate.property'].browse(vals['property_id'])
        maximum_price=property.best_price
        property.state="offer received"
        if maximum_price==None:
            maximum_price=0
        if float_compare(vals.get('price'),maximum_price,precision_rounding=0.01)<0:
            raise ValidationError(message="Enter price higher than %d" %maximum_price)
        return super().create(vals)