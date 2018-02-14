# -*- coding: utf-8 -*-
from odoo import models, fields, api,exceptions,tools,_


class CongTyType(models.Model):
    _name = 'congtytype'
    name = fields.Char()   
class Department(models.Model):
    _inherit = 'hr.department'
    cong_ty_type = fields.Many2one('congtytype', string=u'Loại đơn vị')
    ca_sang_bat_dau = fields.Char(default=u'07:00:00', string=u'Ca sáng bắt đầu' )
    ca_chieu_bat_dau = fields.Char(default=u'14:00:00', string=u'Ca chiều bắt đầu'  )
    ca_dem_bat_dau = fields.Char(default=u'22:30:00', string=u'Ca đêm bắt đầu' )
    ca_sang_duration = fields.Float(digits=(6,1),default=7, string = u'Ca sáng ')
    ca_chieu_duration = fields.Float(digits=(6,1),default=8.5)
    ca_dem_duration = fields.Float(digits=(6,1),default=8.5)
#     location_ids = fields.One2many('stock.location','department_id')
    partner_id = fields.Many2one('res.partner')
    get_department_name_for_report = fields.Char(compute='get_department_name_for_report_')
#     @api.model
# #     @api.returns('self', lambda value: value.id)
#     def _company_default_get(self, object=False, field=False):
#         """ Returns the default company (usually the user's company).
#         The 'object' and 'field' arguments are ignored but left here for
#         backward compatibility and potential override.
#         """
#         if object =='stock.quant': 
#             res =  self.env['hr.department'].search([('name','=',u'Đài HCM')])[0]
#         else:
#             res =  super(Company,self)._company_default_get(object,field)#self.env['res.users']._get_company()
#         print "***company***",res,'**object**',object
#         return res
    
    def get_department_name_for_report_(self):
        for r in self:
            names = []
            if r.cong_ty_type.name:
                names.append(r.cong_ty_type.name)
            names.append(r.name)
            r.get_department_name_for_report =  u' '.join(names)
            