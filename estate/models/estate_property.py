from odoo import fields, models,api
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError,ValidationError

class Property(models.Model):
    _name='estate.property'
    _description='Estate property description'
    _order="id desc"

    active = fields.Boolean(default=True)
    name=fields.Char(required=True, default='Unknown')
    description=fields.Text()
    postcode=fields.Char()
    date_availability=fields.Date(copy=False,default=fields.Date.today()+relativedelta(months=3))
    expected_price=fields.Float(required=True)
    selling_price=fields.Float(readonly=True, copy=False)
    bedrooms=fields.Integer(default=2)
    living_area=fields.Float()
    facades=fields.Integer()
    garage=fields.Boolean()
    garden=fields.Boolean()
    garden_area=fields.Float()
    garden_orientation=fields.Selection(selection=[('north','North'),('south','South'),
                                                    ('east','East'),('west','West')])
    state=fields.Selection(selection=[('new','New'),('offer received','Offer Received'),
                                      ('offer accepted','Offer Accepted'),('sold','Sold'),
                                      ('cancelled','Cancelled')],required=True,copy=False,default='new')
    
    property_type_id=fields.Many2one("estate.property.type", string="Property Type")
    seller_id=fields.Many2one("res.users",default=lambda self: self.env.user,readonly=True)
    buyer_id=fields.Many2one("res.partner",copy=False,readonly=True)

    tag_ids=fields.Many2many("estate.property.tag")

    offer_ids=fields.One2many("estate.property.offer","property_id",string="Offers")

    total_area=fields.Float(compute='_compute_total')

    best_price=fields.Float(compute='_compute_price')

    @api.depends('living_area','garden_area')
    def _compute_total(self):
        for property in self:
            property.total_area=property.living_area+property.garden_area
            
    @api.depends('offer_ids.price')
    def _compute_price(self):
        for property in self:
            property.best_price=max(property.offer_ids.mapped("price"),default=0.0)

    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area=10
            self.garden_orientation='north'
        else:
            self.garden_area=0
            self.garden_orientation=False

    def action_sold_button(self):
        for prop in self:
            if prop.state=='cancelled':
                raise UserError("Cancelled Property cannot be sold")
            prop.state='sold'
        return True
    
    def action_cancel_button(self):
        for prop in self:
            if prop.state=='sold':
                raise UserError("Sold Property cannot be cancelled")
            prop.state='cancelled'
        return True

    #SQL Constraints
    _sql_constraints=[('check_expected_price','CHECK(expected_price > 0)','The expexted price must be strictly positive'),
                      ('check_selling_price','CHECK(selling_price >= 0)','The selling price must be positive')]

    # Python Constraints
    @api.constrains('selling_price','expected_price')
    def _check_selling_price(self):
        for prop in self:
            if(prop.selling_price!=0 and prop.selling_price<(prop.expected_price*90)/100):
                raise ValidationError("The selling price must be at least 90% of the expected price! " + 
                                      "You must reduce the expected price if you want to accept this offer.")

    @api.ondelete(at_uninstall=False)
    def _unlink_if_offer_state(self):
        for prop in self:
            if prop.state not in ["new","cancelled"]:
                raise UserError("Only new or cancelled properties can be deleted")
        