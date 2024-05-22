from odoo import models,fields

class Tag(models.Model):
    _name='estate.property.tag'
    _description='Estate property tag description'
    _order="name"

    name=fields.Char(required=True)

    color=fields.Integer()

    #SQL Constraints
    _sql_constraints=[('check_tag_name','UNIQUE(name)','Property tag should be unique')]