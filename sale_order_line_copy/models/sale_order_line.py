# Copyright 2020 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models, api


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def copy_sale_order_line(self):
        self.ensure_one()
        
        line_data = self.copy_data()[0]
        
        line_data['order_id'] = self.order_id.id
        line_data['sequence'] = self.sequence + 10
        
        new_line = self.create(line_data)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }