# -*- coding: utf-8 -*-
from odoo import models, fields, api,exceptions,tools,_
import re
import pytz
from odoo.exceptions import ValidationError,UserError
import datetime
from lxml import etree
from odoo.osv import expression
import logging
import json
from unidecode import unidecode
_logger = logging.getLogger(__name__)
from odoo.addons.dai_tgg.mytools import  convert_utc_to_gmt_7,name_compute,convert_odoo_datetime_to_vn_datetime,convert_odoo_datetime_to_vn_str,name_compute_char_join_rieng,convert_vn_datetime_to_utc_datetime
# from odoo.addons.dai_tgg.models.cvi import skip_depends_if_not_congviec_decorator
### ngày 05/10/2017 ##
############### BEGIN DAI HCM ##################


# def name_compute_char_join_rieng(r,adict=None,join_char = u' - '):
#     names = []
# #     adict = [('cate_cvi',{'pr':''}),('noi_dung',{'pr':'','func':lambda r: r.name }),('id',{'pr':''})]
#     sum_txt = ''
#     for c,fname_and_attr_dict in enumerate(adict):
#         fname,attr_dict = fname_and_attr_dict
#         val = getattr(r,fname)
#         func = attr_dict.get('func',None)
#         pr_more = attr_dict.get('pr_more','')
#         sf_more = attr_dict.get('sf_more','')
#         join_char_of_one_field = attr_dict.get('join_char',join_char)
#         if func:
#             val = func(val)
#         if  not val:# Cho có trường hợp New ID
#             if attr_dict.get('skip_if_False',True) and  (pr_more=='' and sf_more==''):
#                 continue
#             if  fname=='id' :
#                 val ='New'
#             else:
#                 val ='_'
#         if attr_dict.get('pr',None) != None:
#             item =  attr_dict['pr'] + u': ' + unicode(val)
#         else:
#             item = unicode (val)
#             
#         if pr_more:
#             item =  pr_more +  val
#         if sf_more:
#             item =  val + sf_more
#         if c ==0:
#             pass
#         else:
#             item =join_char_of_one_field + item
#         sum_txt = sum_txt + item
# #         names.append(item)
# #     if names:
# #         name = join_char.join(names)
# #     else:
# #         name = False
#     if sum_txt:
#         pass
#     else:
#         sum_txt = False
#     return sum_txt
# 
# 
# def convert_memebers_to_str(member_ids):
#     return u','.join(member_ids.mapped('name'))
# 
# def Convert_date_orm_to_str(date_orm_str,format_date = '%d/%m/%y'):
#     if date_orm_str:
#         date_obj = fields.Date.from_string(date_orm_str)
#         return date_obj.strftime(format_date)
#     else:
#         return False
#     
# # def Convert_datetime_orm_to_str(date_orm_str):
# #     if date_orm_str:
# #         date_obj = fields.Datetime.from_string(date_orm_str)
# #         return date_obj.strftime('%d/%m/%y %H:%M')
# #     else:
# #         return False
#     
#     
# def convert_utc_to_gmt_7(utc_datetime_inputs):
#     local = pytz.timezone('Etc/GMT-7')
#     utc_tz =pytz.utc
#     gio_bat_dau_utc_native = utc_datetime_inputs#fields.Datetime.from_string(self.gio_bat_dau)
#     gio_bat_dau_utc = utc_tz.localize(gio_bat_dau_utc_native, is_dst=None)
#     gio_bat_dau_vn = gio_bat_dau_utc.astimezone (local)
#     return gio_bat_dau_vn
# def convert_odoo_datetime_to_vn_datetime(odoo_datetime):
#         utc_datetime_inputs = fields.Datetime.from_string(odoo_datetime)
#         vn_time = convert_utc_to_gmt_7(utc_datetime_inputs)
#         return vn_time
#   
# def convert_vn_datetime_to_utc_datetime(native_ca_gio_in_vn):
#             local = pytz.timezone('Etc/GMT-7')
#             utc_tz =pytz.utc
#             gio_bat_dau_in_vn = local.localize(native_ca_gio_in_vn, is_dst=None)
#             gio_bat_dau_in_utc = gio_bat_dau_in_vn.astimezone (utc_tz)
#             return gio_bat_dau_in_utc
#         
# def convert_odoo_datetime_to_vn_str(odoo_datetime):
#     if odoo_datetime:
#         utc_datetime_inputs = fields.Datetime.from_string(odoo_datetime)
#         vn_time = convert_utc_to_gmt_7(utc_datetime_inputs)
#         vn_time_str = vn_time.strftime('%d/%m/%Y %H:%M')
#         return vn_time_str
#     else:
#         return False
    
    

################ CA TRỰC ##############



    
########################SỰ CỐ####################
#SUCO_SUVU_LIST = ('su_co',u'Sự Cố'),('su_vu',u'Sự Vụ')
# SUCO_SUVU_DICT = {'su_co':u'Sự Cố','su_vu':u'Sự Vụ'}


        
        




            
# class DoiTac(models.Model):
#     _name = 'doitac'
#     name = fields.Char(string=u'Tên đối tác')
#     department_id = fields.Many2one('congty',string=u'Đơn vị')
#     chuc_vu = fields.Char(string=u'Chức vụ')

    
#     @api.model
#     def search(self, args, offset=0, limit=None, order=None, count=False):
#         if args == None:
#             args = []
#         cd_user_id =  self._context.get('cd_user_id')
#         if cd_user_id:
#             cd_user_id = json.loads(cd_user_id)
#             if cd_user_id !=[] or cd_user_id !=False:
#                 add_domain = [('id','!=',cd_user_id)]
#                 args = expression.AND([args,add_domain])
#             
#         return super(User, self).search(args, offset, limit, order, count=count)  
    
#     

    
    
#     nhan_vien_ids = fields.One2many('res.users','department_id')
    
# class CongTy(models.Model):
#     _name = 'congty'
#     _parent_name = 'parent_id'
#     name=fields.Char()
#     parent_id = fields.Many2one('congty',string=u'Đơn vị Cha')
#     child_ids = fields.One2many('congty', 'parent_id', string=u'Các đơn vị con')
#     cong_ty_type = fields.Many2one('congtytype', string=u'Loại đơn vị')
#     ca_sang_bat_dau = fields.Char(default=u'07:00:00', string=u'Ca sáng bắt đầu' )
#     ca_chieu_bat_dau = fields.Char(default=u'14:00:00', string=u'Ca chiều bắt đầu'  )
#     ca_dem_bat_dau = fields.Char(default=u'22:30:00', string=u'Ca đêm bắt đầu' )
#     ca_sang_duration = fields.Float(digits=(6,1),default=7, string = u'Ca sáng ')
#     ca_chieu_duration = fields.Float(digits=(6,1),default=8.5)
#     ca_dem_duration = fields.Float(digits=(6,1),default=8.5)
#     nhan_vien_ids = fields.One2many('res.users','department_id')
#     @api.constrains('parent_id')
#     def _check_category_recursion_check_category_recursion(self):
#         if not self._check_recursion():
#             raise ValidationError(_('Error ! You cannot create recursive categories.'))
#         return True
#     @api.multi
#     def name_get(self):
#         def get_names(cat):
#             ''' Return the list [cat.name, cat.parent_id.name, ...] '''
#             res = []
#             if cat.name != False:
#                 while cat:
#                         res.append(cat.name)
#                         cat = cat.parent_id
#             return res
#         return [(cat.id, ' / '.join(reversed(get_names(cat)))) for cat in self]
#     ### tao lao bi dao  dfsddfasdfd
#     @api.model
#     def name_search(self, name, args=None, operator='ilike', limit=100):
#         if not args:
#             args = []
#         if name:
#             # Be sure name_search is symetric to name_get
#             category_names = name.split(' / ')
#             parents = list(category_names)
#             child = parents.pop()
#             domain = [('name', operator, child)]
#             if parents:
#                 names_ids = self.name_search(' / '.join(parents), args=args, operator='ilike', limit=limit)
#                 category_ids = [name_id[0] for name_id in names_ids]
#                 if operator in expression.NEGATIVE_TERM_OPERATORS:
#                     categories = self.search([('id', 'not in', category_ids)])
#                     domain = expression.OR([[('parent_id', 'in', categories.ids)], domain])
#                 else:
#                     domain = expression.AND([[('parent_id', 'in', category_ids)], domain])
#                 for i in range(1, len(category_names)):
#                     domain = [[('name', operator, ' / '.join(category_names[-1 - i:]))], domain]
#                     if operator in expression.NEGATIVE_TERM_OPERATORS:
#                         domain = expression.AND(domain)
#                     else:
#                         domain = expression.OR(domain)
#             categories = self.search(expression.AND([domain, args]), limit=limit)
#         else:
#             categories = self.search(args, limit=limit)
#         return categories.name_get()
    
    

    
###################### END CA TRỰC #################3
############FILE###########
class File(models.Model):
    _name = 'dai_tgg.file'
    name = fields.Char(string=u'File name')
    file = fields.Binary( attachment=True)
    mo_ta = fields.Text(string=u'Mô tả file')
#     cvi_id = fields.Many2one('cvi')
########END FILE############

###############  CÔNG VIỆC ###############





        
        





    
     



               
############### END SỰ KIỆN ################
class PN(models.Model):  
    _name = 'pn'
    name = fields.Char()
    kiemke_ids = fields.One2many('kiemke','pn_id')
    vattu_ids = fields.One2many('vattu','pn_id')



def map_another_object(self_,val,field_map,model_map):
    self = self_
    if val:
        mappings = self.env[model_map].search([(field_map,'=ilike',val)],limit=1)
        if mappings:
            return mappings
    return False
            
                
class KiemKe(models.Model):  
    _name = 'kiemke'
    name = fields.Char(compute='name_',store=True)
    kiem_ke_id = fields.Char()
    stt = fields.Integer(string='STT')
    ten_vat_tu = fields.Char(string=u'Tên tài sản')
    so_the = fields.Char(string=u'Số Thẻ')
    ma_du_an = fields.Char(string=u'Mã dự án')
    ten_du_an = fields.Char(string=u'Tên dự án')
    pn = fields.Char(string=u'Part-Number')
    sn = fields.Char(string=u'Serial number')
    ma_vach = fields.Char(string=u'Mã vạch')
    ma_vach_thuc_te = fields.Char(string=u'Serial/Mã vạch thực tế ')
    trang_thai = fields.Char(string=u'Trạng thái')
    hien_trang_su_dung = fields.Char(string=u'Hiện trạng sử dụng')
    ghi_chu = fields.Char(string=u'Ghi chú')
    don_vi = fields.Char(string=u'Đơn vị')
    vi_tri_lap_dat = fields.Char(string=u'Vị trí lắp đặt')
    loai_tai_san = fields.Char(string=u'Loại tài sản')
    len_duplicate_sn_vat_tu_ids = fields.Integer(compute='duplicate_sn_vat_tu_ids_',store=True)
    sn_false = fields.Char()
    pn_id = fields.Many2one('pn')
    duplicate_sn_vat_tu_ids = fields.Many2many('kiemke','kiemke_kiemke_relate','kiemke_id','kiemke2_id',compute='duplicate_sn_vat_tu_ids_',store=True)
    yes_no_search = fields.Boolean(store=False)
    map_ltk_id = fields.Many2one('vattu',compute='map_ltk_id_',store=True)
   
    map_kknoc_id = fields.Many2one('kknoc',compute='map_kknoc_id_',store=True)
    tram = fields.Char(related='map_kknoc_id.tram',string=u'Trạm',store=True)
    len_sn = fields.Integer(compute='len_sn_',store=True)
    trig_field = fields.Char()
    
    ilike_map_ltk_ids = fields.Many2many('vattu',compute='ilike_map_ltk_id_',store=True)
    len_ilike_map_ltk_ids = fields.Integer(compute='ilike_map_ltk_id_',store=True)  
   
    ilike_map_kknoc_ids = fields.Many2many('kknoc',compute='ilike_map_kknoc_ids_',store=True)
    len_ilike_map_kknoc_ids = fields.Integer(compute='ilike_map_kknoc_ids_',store=True)  
    
    @api.depends('sn','trig_field','map_kknoc_id')
    def ilike_map_kknoc_ids_(self):
        for r in self:
            if not r.map_kknoc_id:
                rs = self.env['kknoc'].search([('sn','ilike',r.sn)])
                if rs:
                    r.ilike_map_kknoc_ids = rs.ids
                    r.len_ilike_map_kknoc_ids = len(rs)
                    
    
    @api.depends('sn','trig_field','map_ltk_id')
    def ilike_map_ltk_id_(self):
        for r in self:
            if not r.map_ltk_id:
                rs = self.env['vattu'].search([('sn','ilike',r.sn)])
                if rs:
                    r.ilike_map_ltk_ids = rs.ids
                    r.len_ilike_map_ltk_ids = len(rs)
                
    @api.depends('sn','trig_field')
    def len_sn_(self):
        for c,r in enumerate(self):
            ##print 'len_sn',c
            if r.sn:
                r.len_sn  =len(r.sn)
    
    @api.depends('sn','trig_field')
    def map_ltk_id_(self):
        field_map = 'sn'
        model_map = 'vattu'
        for r in self:
            val = r.sn
            map_id = map_another_object(self,val,field_map,model_map)
            r.map_ltk_id = map_id
    @api.depends('sn','trig_field')
    def map_kknoc_id_(self):
        field_map = 'sn'
        model_map = 'kknoc'
        for r in self:
            val = r.sn
            map_id = map_another_object(self,val,field_map,model_map)
            r.map_kknoc_id = map_id
            
    @api.depends('sn','trig_field')
    def duplicate_sn_vat_tu_ids_(self):
        for r in self:
            if r.sn:
                mappings = self.env['kiemke'].search([('sn','=',r.sn)])
                mapping_list = mappings.ids
                if r.id:
                    mapping_list = filter(lambda i : i!=r.id,mapping_list)
                r.duplicate_sn_vat_tu_ids =mapping_list
                r.len_duplicate_sn_vat_tu_ids = len(mapping_list)
    @api.depends('sn','pn')
    def name_(self):
        for r in self:
            name  = name_compute(r,adict=[
                                            ('id',{'pr':u'vt ketoan, id'}),
                                            ('pn',{'pr':u'P/N'}),
                                            ('sn',{'pr':u'S/N'}),
                                            ]
                                 )
            r.name = name
#     @api.multi
#     def name_get(self):
#         def get_names(r):
#             name = name_compute(r,adict=[('name',{}),
#                                           ('pn',{'pr':u'P/N','skip_if_False':True},),
#                                           ('sn',{'pr':u'S/N','skip_if_False':True},),
#                                           ]
#                                  )
#             return name
#             
#         return [(r.id, get_names(r)) for r in self]
        
    


    
class Vattu(models.Model):  
    _name = 'vattu'
    name = fields.Char(compute='name_',store=True)
    stt = fields.Integer()
    phan_loai = fields.Char(string=u'Phân Loại')
    loai_card = fields.Char(string=u'Loại Card')
    he_thong = fields.Char(string=u'Hệ Thống')
    cabinet_rack = fields.Char()
    shelf = fields.Char()
    stt_shelf = fields.Char()
    slot = fields.Char()
    ghi_chu = fields.Char()
    pn = fields.Char()
    pn_id = fields.Many2one('pn')
    sn = fields.Char(string=u'SN')
    map_kiem_ke_id = fields.Many2one('kiemke',compute='map_kiem_ke_id_',store=True)
    map_kknoc_id = fields.Many2one('kknoc',compute='map_kknoc_id_',store=True)
    tram = fields.Char(related='map_kknoc_id.tram',string=u'Trạm',store=True)
    is_not_also_map_pn = fields.Boolean(compute='is_not_also_map_pn_',store=True)
    duplicate_sn_vat_tu_ids = fields.Many2many('vattu','vattu_vattu_relate','vattu_id','vattu2_id',compute='duplicate_sn_vat_tu_ids_',store=True)
    len_duplicate_sn_vat_tu_ids = fields.Integer(compute='duplicate_sn_vat_tu_ids_',store=True)
    sn_false = fields.Char()
    len_sn = fields.Integer(compute='len_sn_',store=True)
    trig_field = fields.Char()
    ilike_map_kk_ids = fields.Many2many('kiemke',compute='ilike_map_ltk_id_',store=True)
    len_ilike_map_kk_ids = fields.Integer(compute='ilike_map_ltk_id_',store=True)  
    @api.depends('sn','trig_field','map_kiem_ke_id')
    def ilike_map_ltk_id_(self):
        for c,r in enumerate(self):
            ##print  'map i like _ids',c
            if not r.map_kiem_ke_id :
                rs = self.env['kiemke'].search([('sn','ilike',r.sn)])
                if rs:
                    r.ilike_map_kk_ids = rs.ids
                    r.len_ilike_map_kk_ids = len(rs)
                    
                    
                    
    @api.depends('sn','trig_field')
    def len_sn_(self):
        for r in self:
            if r.sn:
                r.len_sn  =len(r.sn)
    
    @api.depends('sn')
    def map_kknoc_id_(self):
        for r in self:
            r.map_kknoc_id = map_another_object(self,r.sn,'sn','kknoc')
    @api.depends('sn')
    def map_kiem_ke_id_(self):
        for r in self:
            r.map_kiem_ke_id = map_another_object(self,r.sn,'sn','kiemke')
    @api.depends('sn','pn')
    def name_(self):
        for r in self:
            name  = name_compute(r,adict=[
                                            ('id',{'pr':u'vt ltk, id'}),
                                            ('pn',{'pr':u'P/N'}),
                                            ('sn',{'pr':u'S/N'}),
                                            ]
                                 )
            r.name = name
    @api.multi
    def name_get(self):
        def get_names(r):
            name = name_compute(r,adict=[
                                           ('id',{'pr':u'vt ltk, id'}),
                                            ('stt',{'pr':u'STT'}),
                                            ('pn',{'pr':u'P/N'}),
                                            ('sn',{'pr':u'S/N'}),
                                          ]
                                 )
            return name
             
        return [(r.id, get_names(r)) for r in self]

    @api.depends('sn')
    def duplicate_sn_vat_tu_ids_(self):
        for r in self:
            if r.sn:
                mappings = self.env['vattu'].search([('sn','=',r.sn)])
                mapping_list = mappings.ids
                if r.id:
                    mapping_list = filter(lambda i : i!=r.id,mapping_list)
                r.duplicate_sn_vat_tu_ids =mapping_list
                r.len_duplicate_sn_vat_tu_ids = len(mapping_list)
    
    @api.depends('map_kiem_ke_id','pn')
    def is_not_also_map_pn_(self):
        for r in self:
            ##print '2 Begin is_not_also_map_pn_'
            if r.map_kiem_ke_id:
                ##print '2 in is_not_also_map_pn_'
                if r.pn !=r.map_kiem_ke_id.pn:
                    r.is_not_also_map_pn = True
         
    

    

class KKNoc(models.Model):  
    _name = 'kknoc'
    name = fields.Char(compute='name_',store=True)
    stt = fields.Integer()
    pn = fields.Char(string=u'P/N')
    clei = fields.Char(strin=u'CLEI')
    sn = fields.Char(string=u'S/N')
    pn_id = fields.Many2one('pn')
    len_duplicate_sn_vat_tu_ids = fields.Integer(compute='duplicate_sn_vat_tu_ids_',store=True)
    sn_false = fields.Char()
    data = fields.Text()
    duplicate_sn_vat_tu_ids = fields.Many2many('kknoc','kknoc_kknoc_relate','kknoc_id','kknoc2_id',compute='duplicate_sn_vat_tu_ids_',store=True)
    sheet_name = fields.Char()
    file_name = fields.Char(string=u'File của Noc')
    tram = fields.Char(string=u'Trạm',compute='tram_',store=True)
    map_ltk_id = fields.Many2one('vattu',compute='map_ltk_id_',store=True,string=u'Map với LTK')
    map_kiemke_id = fields.Many2one('kiemke',compute='map_kiemke_id_',store=True,string=u'Map với Kiểm Kê')
    trig_field = fields.Char()
    len_sn = fields.Integer(compute='len_sn_',store=True)
    ilike_map_kk_ids = fields.Many2many('kiemke',compute='ilike_map_kk_ids_',store=True)
    len_ilike_map_kk_ids = fields.Integer(compute='ilike_map_kk_ids_',store=True)  
    ilike_map_vattu_ids = fields.Many2many('vattu',compute='ilike_map_vattu_ids_',store=True)
    len_ilike_map_vattu_ids = fields.Integer(compute='ilike_map_vattu_ids_',store=True)  
    
    @api.depends('sn','trig_field','map_ltk_id')
    def ilike_map_vattu_ids_(self):
        for c,r in enumerate(self):
            ##print '222ilike_map_vattu_ids_222',c
            if not r.map_ltk_id:
                rs = self.env['vattu'].search([('sn','ilike',r.sn)])
                if rs:
                    r.ilike_map_vattu_ids = rs.ids
                    r.len_ilike_map_vattu_ids = len(rs)
    
    @api.depends('sn','trig_field','map_kiemke_id')
    def ilike_map_kk_ids_(self):
        for c,r in enumerate(self):
            ##print '333map_kiemke_id333',c
            if not r.map_kiemke_id:
                rs = self.env['kiemke'].search([('sn','ilike',r.sn)])
                if rs:
                    r.ilike_map_kk_ids = rs.ids
                    r.len_ilike_map_kk_ids = len(rs)
                    
                    
    @api.depends('sn','trig_field')
    def len_sn_(self):
        for c,r in enumerate(self):
            ##print '00000 len_sn0000',c
            if r.sn:
                r.len_sn  =len(r.sn)
    @api.depends('sn','sheet_name','trig_field')
    def tram_(self):
        for c,r in enumerate(self):
            ##print '1xxxtram',c
            r.tram = convert_sheetname_to_tram(r.sheet_name)
    @api.depends('sn','trig_field')
    def map_kiemke_id_(self):
        for c,r in enumerate(self):
            ##print '111map_kiemke_id_111',c
            r.map_kiemke_id = map_another_object(self,r.sn,'sn','kiemke')
    @api.depends('sn','trig_field')
    def map_ltk_id_(self):
        for r in self:
            r.map_ltk_id = map_another_object(self,r.sn,'sn','vattu')
    @api.depends('sn')
    def duplicate_sn_vat_tu_ids_(self):
        for r in self:
            if r.sn:
                mappings = self.env['kknoc'].search([('sn','=',r.sn)])
                mapping_list = mappings.ids
                if r.id:
                    mapping_list = filter(lambda i : i!=r.id,mapping_list)
                r.duplicate_sn_vat_tu_ids =mapping_list
                r.len_duplicate_sn_vat_tu_ids = len(mapping_list)
    @api.depends('sn','pn')
    def name_(self):
        for r in self:
            name  = name_compute(r,adict=[
                                            ('id',{'pr':u'vt noc, id'}),
                                            ('pn',{'pr':u'P/N','skip_if_False':True}),
                                            ('sn',{'pr':u'S/N','skip_if_False':True}),
                                            ]
                                 )
            r.name = name



class GCCV(models.Model):
    _name='gccv'
    name= fields.Char()
    noi_dung=fields.Text(string=u'Nội dung') 
    thanh_cong_hay_that_bai = fields.Selection ([(u'Thành Công',u'Thành Công'),(u'Thất Bại',u'Thất Bại')],default=u'Thành Công') 
    loi_code = fields.Text(string=u'Lỗi')
    gccv_type_ids = fields.Many2many('gccvtype','gccv_gccvtype_relate','gccv_id','gccvtype_id',u'Các Loại ghi chú')
    doi_lap_id = fields.Many2one('gccv',u'Ghi chú đối lập')
    doi_lap_ids = fields.One2many('gccv','doi_lap_id',u'Những ghi chú đối lập')
    ket_qua_du_doan = fields.Text(string=u'Kết quả dự đoán')
    thac_mac =  fields.Text(string=u'Thắc Mắc')
    ket_qua_thuc_te = fields.Text(string=u'Kết quả thực tế')
    dung_voi_ket_qua_du_doan = fields.Boolean(string=u'Kết quả đúng với thực tế hay không')
    
    image_truoc_test = fields.Binary(string=u'Ảnh trước khi test')
    image_sau_test = fields.Binary(string=u'Ảnh sau khi test')
    
class GCCVType(models.Model):
    _name = 'gccvtype'
    _parent_name = 'parent_id'
    name = fields.Char()
    minh_hoa = fields.Text(string=u'Minh Họa')
    parent_id = fields.Many2one('gccvtype',string=u'Loại ghi chú Cha')
    gccv_ids=fields.Many2many('gccv','gccv_gccvtype_relate','gccvtype_id','gccv_id',u'Các Ghi chú')
    @api.constrains('parent_id')
    def _check_category_recursion_check_category_recursion(self):
        if not self._check_recursion():
            raise ValidationError(_('Error ! You cannot create recursive categories.'))
        return True
    @api.multi
    def name_get(self):
        def get_names(cat):
            ''' Return the list [cat.name, cat.parent_id.name, ...] '''
            res = []
            if cat.name != False:
                while cat:
                        res.append(cat.name)
                        cat = cat.parent_id
            return res
        return [(cat.id, ' / '.join(reversed(get_names(cat)))) for cat in self]
 
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if not args:
            args = []
        if name:
            # Be sure name_search is symetric to name_get
            category_names = name.split(' / ')
            parents = list(category_names)
            child = parents.pop()
            domain = [('name', operator, child)]
            if parents:
                names_ids = self.name_search(' / '.join(parents), args=args, operator='ilike', limit=limit)
                category_ids = [name_id[0] for name_id in names_ids]
                if operator in expression.NEGATIVE_TERM_OPERATORS:
                    categories = self.search([('id', 'not in', category_ids)])
                    domain = expression.OR([[('parent_id', 'in', categories.ids)], domain])
                else:
                    domain = expression.AND([[('parent_id', 'in', category_ids)], domain])
                for i in range(1, len(category_names)):
                    domain = [[('name', operator, ' / '.join(category_names[-1 - i:]))], domain]
                    if operator in expression.NEGATIVE_TERM_OPERATORS:
                        domain = expression.AND(domain)
                    else:
                        domain = expression.OR(domain)
            categories = self.search(expression.AND([domain, args]), limit=limit)
        else:
            categories = self.search(args, limit=limit)
        return categories.name_get()            

                
################### END LOAI SUCO####################                             
                
                
  
                
                
                
                





  

    

      





    



        
        
        
        





  
                
                
                
                
                
                
                
                
        
        
        
        
        