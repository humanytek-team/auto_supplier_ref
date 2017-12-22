# -*- coding: utf-8 -*-
# Copyright 2017 Humanytek - Manuel Marquez <manuel@humanytek.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import api, models
from openerp.exceptions import ValidationError
from openerp.tools.translate import _
import logging


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def _get_supplier_ref(self):
        """Returns the "Internal Reference" for the supplier."""

        IrConfigParameter = self.env['ir.config_parameter']

        parameter_supplier_ref_prefix = IrConfigParameter.search([
            ('key', '=', 'supplier_ref_prefix')
        ])

        parameter_supplier_ref_sequence_number_digits = IrConfigParameter.search([
            ('key', '=', 'supplier_ref_sequence_number_digits')
        ])

        if parameter_supplier_ref_prefix and parameter_supplier_ref_sequence_number_digits:

            number_digits = int(
                parameter_supplier_ref_sequence_number_digits[0].value)

            suppliers = self.with_context(active_test=False).search([
                ('supplier', '=', True),
                ('ref', 'like', '%s%%' %
                 (parameter_supplier_ref_prefix[0].value)),
            ])

            if suppliers:

                current_max_sequence = max(suppliers.mapped('ref'))

                sequence = str(int(
                    current_max_sequence[-number_digits:]) + 1).zfill(
                        number_digits)

            else:
                sequence = '1'.zfill(number_digits)

            default_code = '%s%s' % (
                parameter_supplier_ref_prefix[0].value, sequence)

            return default_code

        else:
            raise ValidationError(_(
                'The system parameters supplier_ref_sequence_number_digits and/or supplier_ref_sequence_number_digits does not exist'))

    @api.model
    def create(self, vals):

        if vals.get('supplier', False):
            vals['ref'] = self._get_supplier_ref()

        return super(ResPartner, self).create(vals)
