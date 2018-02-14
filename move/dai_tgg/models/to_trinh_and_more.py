# -*- coding: utf-8 -*-
from odoo import models, fields, api,exceptions,tools,_

class ToTrinh(models.Model):
    _name = 'totrinh'
    name = fields.Char(u'Về Việc',required=True)
    so_to_trinh = fields.Char()
    ngay_to_trinh = fields.Date()