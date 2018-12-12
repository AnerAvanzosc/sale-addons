# -*- coding: utf-8 -*-
# (c) 2017 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api
from dateutil.relativedelta import relativedelta


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.multi
    def _renovate_contract_from_wizard(self, increase, sale=False):
        for contract in self:
            vals = {'date_start': (fields.Date.from_string(contract.date) +
                                   relativedelta(days=1)),
                    'date': (fields.Date.from_string(contract.date) +
                             relativedelta(years=1))}
            if contract.recurring_next_date:
                vals['recurring_next_date'] = vals.get('date_start')
            contract.copy(vals)._update_new_contract_renovate_information(
                contract, increase, sale)
            contract.set_close()

    def _update_new_contract_renovate_information(self, origin_contract,
                                                  increase, origin_sale):
        year = int(fields.Date.from_string(self.date_start).year)
        if str(year-1) in origin_contract.name:
            self.name = origin_contract.name
            self.name = self.name.replace(str(year-1), str(year))
        else:
            self.name = u'{} {}'.format(origin_contract.name, year)
        if increase:
            for line in self.recurring_invoice_line_ids.filtered(
                    lambda x: x.price_unit):
                line.price_unit = (line.price_unit +
                                   (line.price_unit * increase))
        if (self.recurring_rule_type == 'monthly' and
                self.recurring_interval > 1):
            self.recurring_next_date = (
                fields.Date.from_string(self.date_start) +
                relativedelta(months=self.recurring_interval - 1))
        self.set_open()
        if origin_sale:
            self._duplicate_sale_order_from_contract(origin_sale,
                                                     origin_contract)

    def _duplicate_sale_order_from_contract(self, origin_sale,
                                            origin_contract):
        new_sale = origin_sale.copy()
        new_sale.write({'generated_from_sale_order': origin_sale.id,
                        'project_id': self.id})
        if origin_sale and origin_sale.name == origin_contract.name:
            self.name = new_sale.name
        return new_sale
