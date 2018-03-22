# -*- coding: utf-8 -*-
from odoo import models, fields, api,exceptions,tools,_


class CongTyType(models.Model):
    _name = 'congtytype'
    name = fields.Char()   
class Department(models.Model):
    _inherit = 'hr.department'
    name_for_report = fields.Char()
    cong_ty_type = fields.Many2one('congtytype', string=u'Loại đơn vị')
    ca_sang_bat_dau = fields.Char(default=u'07:00:00', string=u'Ca sáng bắt đầu' )
    ca_chieu_bat_dau = fields.Char(default=u'14:00:00', string=u'Ca chiều bắt đầu'  )
    ca_dem_bat_dau = fields.Char(default=u'22:30:00', string=u'Ca đêm bắt đầu' )
    ca_sang_duration = fields.Float(digits=(6,1),default=7, string = u'Ca sáng ')
    ca_chieu_duration = fields.Float(digits=(6,1),default=8.5)
    ca_dem_duration = fields.Float(digits=(6,1),default=8.5)
    partner_id = fields.Many2one('res.partner')
    get_department_name_for_report = fields.Char(compute='get_department_name_for_report_')
   
    def get_department_name_for_report_(self):
        for r in self:
            names = []
            if r.cong_ty_type.name:
                names.append(r.cong_ty_type.name)
            names.append(r.name)
            r.get_department_name_for_report =  u' '.join(names)
            