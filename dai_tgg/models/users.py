# -*- coding: utf-8 -*-
from odoo import models, fields, api,exceptions,tools,_
from odoo.addons.dai_tgg.mytools import  name_compute,name_khong_dau_compute

class PartnerABC(models.Model):
    _inherit = ['res.partner']#,'khongdaumodel']
    _auto = True
    department_id = fields.Many2one('hr.department')
    job_id = fields.Many2one('hr.job', string='Job Title')
    name_khong_dau = fields.Char(compute='name_khong_dau_', store=True)
    name_viet_tat =  fields.Char(compute='name_khong_dau_', store=True)
    
    @api.depends('name')
    def name_khong_dau_(self):
        pass
        name_khong_dau_compute(self)
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', '|', ('name', operator, name), ('name_khong_dau', operator, name), ('name_viet_tat', operator, name)]
        obj = self.search(domain + args, limit=limit)
        return obj.name_get()
    
    
    
class User(models.Model):
    _inherit = 'res.users'
#     department_id = fields.Many2one('hr.department')
    ctr_ids = fields.Many2many('ctr', 'ctr_res_users_rel_d4','res_users_id','ctr_id',string=u'Các ca đã trực')
    cac_sep_ids = fields.Many2many('res.users','user_sep_relate','user_id','sep_id', string=u'Các Lãnh Đạo')
    cac_linh_ids = fields.Many2many('res.users','user_sep_relate','sep_id', 'user_id',string=u'Các Nhân Viên')
    is_admin = fields.Boolean(compute='is_admin_')
    all_sep_ids = fields.Many2many('res.users','user_sep_relate','user_id','sep_id', string=u'Tất cả Lãnh Đạo',compute='all_sep_ids')
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', '|', ('name', operator, name), ('name_khong_dau', operator, name), ('name_viet_tat', operator, name)]
        obj = self.search(domain + args, limit=limit)
        return obj.name_get()
    
    
    @api.depends('cac_sep_ids')
    def all_sep_ids_(self):
        for r in self:
            all_sep = []
            for sep in r.cac_sep_ids:
                all_sep.append(sep.id)
                for sep_lon in sep.cac_sep_ids:
                    all_sep.append(sep_lon.id)
    @api.model
    def create(self, vals):
        user = super(User, self).create(vals)
        user.partner_id.write({'email': user.login})
        return user

    @api.multi
    def write(self, vals):
        res = super(User, self).write(vals)
        self.partner_id.write({'email': self.login})
        return res

    @api.multi
    def is_admin_(self):
        for r in self:
            if self.user_has_groups('base.group_erp_manager'):
                r.is_admin = True