from odoo import models,Command

class EstateProperty(models.Model):
    _inherit="estate.property"

    def action_sold_button(self):
        for prop in self:
            invoice=self.env['account.move'].create(
                {
                    'partner_id':prop.buyer_id.id,
                    'move_type':'out_invoice',
                    'invoice_line_ids':[
                        Command.create({
                            'name':'Property Tax (6% of selling price)',
                            'quantity':1,
                            'price_unit':prop.selling_price*0.06
                        }),
                        Command.create({
                            'name':'Administrative Fees',
                            'quantity':1,
                            'price_unit':100.00
                        })],
                }
            )
        return super().action_sold_button()