# -*- coding: utf-8 -*-
from odoo import models, fields, api,exceptions,tools,_
import re
from tao_instance_new import importthuvien
from tao_instance import import_strect

M = {'LTK':['LTK'],'PTR':['pas'],'TTI':['TTI'],'BDG':['BDG'],'VTU':['VTU']}
def convert_sheetname_to_tram(sheet_name):
    if sheet_name ==False:
        return False
    else:
        for tram,key_tram_list in M.items():
            for key_tram in key_tram_list:
                rs = re.search(key_tram,sheet_name)
                if rs:
                    find_tram = tram
                    return find_tram
        return sheet_name  
class ImportThuVien(models.Model):
    _name = 'importthuvien' 
    type_choose = fields.Selection([
        (u'stock.inventory.line',u'stock.inventory.line'),
        (u'Thư viện công việc',u'Thư viện công việc'),
                                    (u'User',u'User')
                                    #,(u'Công Ty',u'Công Ty')
                                    ,(u'Department',u'Department')
                                    ,(u'Stock Location',u'Stock Location')
                                    ,(u'stock production lot',u'stock production lot')
                                    ,(u'Kiểm Kê',u'Kiểm Kê'),(u'Vật Tư LTK',u'Vật Tư LTK')
                                    ,(u'x',u'x'),(u'640',u'640G 1850 ')
                                    ,(u'INVENTORY_240G',u'INVENTORY_240G')
                                    ,(u'INVENTORY_RING_NAM_CIENA',u'INVENTORY_RING_NAM_CIENA')
                                    ,(u'Inventory-120G',u'Inventory-120G')
                                    ,(u'Inventory-330G',u'Inventory-330G')
                                    ,(u'INVENTORY-FW4570',u'INVENTORY-FW4570')
                                    ,(u'INVETORY 1670',u'INVETORY 1670')
                                    ,(u'iventory hw8800',u'iventory hw8800')
                                    ,(u'iventory7500',u'iventory7500')
                                    ],required = True)
    file = fields.Binary()
    filename = fields.Char()
    update_number=fields.Integer()
    create_number=fields.Integer()
    skipupdate_number=fields.Integer()
    thong_bao_khac = fields.Char()
    trigger_model = fields.Selection([(u'kiemke',u'kiemke'),
                                    (u'vattu',u'vattu'),(u'kknoc',u'kknoc'),
                                    (u'cvi',u'cvi')
                                    ])
    log = fields.Text()
#     f1 = fields.Boolean()
#     f2 = fields.Boolean()
#     f3 = fields.Boolean()
#     f4 = fields.Boolean()
    def test_code(self):
        self.env['stock.inventory'].browse([13]).line_ids.unlink()
#         tong =u''
#         fields= self.env['stock.production.lot']._fields
# #         tong +=u'%s'%fields
#         count =0
#         for f,field  in fields.iteritems():
#             count +=1
#             
# #             if count ==1:
# #                 tong = u'%s'%field.__dict__
#             print 'field',f,type(field),field.type,'field.related',field.related,'type(field.related)',type(field.related),'field.comodel_name',field.comodel_name
#             
#             if field.related_field:
#                 print 'field.related_field.model_name',field.related_field.model_name
#         self.log = tong
#         not_active_include_search = True
#         if not_active_include_search:
#             domain_not_active = [('f1','=','a')]
#         else:
#             domain_not_active = []
#         domain = [('f2','=','a'),('f3','=','a')]
#         domain = expression.OR([domain_not_active, domain])
            
#         res = self.env['tvcv'].search(domain)
        
#         tong = ''
#         _sql = "select 1 + 1"
#         self._cr.execute(_sql)
#         kq_fetch =  self._cr.fetchall()
#         _sql = "select 2 + 2"
#         self._cr.execute(_sql)
#         kq_fetch = self._cr.fetchall()
#       
# 
# 
#         _logger.info('***22222222222222222****'*20 + u'%s'%kq_fetch)
#         two = len(one)
#         tong +=u'%s'%two + '\n%s'%three + '\n%s'%four
#         tong = u''
#         tong += u'%s\n'%self.env.user.groups_id
#         tong += u'%s\n'%self.env.ref('base.group_erp_manager').id
#         tong += u'%s\n'%(self.env.ref('base.group_erp_manager') in self.env.user.groups_id)
#         self.log =tong
    def trigger(self):
        if self.trigger_model:
            count = 0
            self.env[self.trigger_model].search([]).write({'trig_field':'ok'})
#             for r in self.env[self.trigger_model].search([]):
#                 #print  count
#                 r.sn = r.sn
#                 count +=1
        else:
            raise UserWarning(u'Bạn phải chọn trigger model')
    def importthuvien(self):
        importthuvien(self)
        return True
    def import_strect(self):
        import_strect(self)
        return True
    def get_tram_from_sheet_name(self):
        M = {'LTK':['LTK'],'PTR':['PTR'],'TTI':['TTI'],'BDG':['BDG','VTU']}
        count = 0
        map_count = 0
        for r in self.env['kknoc'].search([]):
            count +=1
            #print count
            r.tram =convert_sheetname_to_tram(r.sheet_name)
            if r.tram:
                map_count +=1
        self.thong_bao_khac = 'so tram ltk, ptr %s'%map_count
                
                
    def map_kiemke_voi_noc(self):
        so_luong_mapping = 0
        count = 0
        for r in self.env['kiemke'].search([]):
            #print count
            if r.sn:
                mapping = self.env['kknoc'].search([('sn','=',r.sn)],limit=1)
                if mapping:
                    so_luong_mapping +=1
                    r.map_kknoc_id = mapping.id
            else:
                r.map_kknoc_id = False
            count +=1
        self.thong_bao_khac = u'Có %s kk mapping kknoc' %( so_luong_mapping)
        return True       
    def map_noc_voi_ltk(self):
        so_luong_mapping = 0
        count = 0
        for r in self.env['kknoc'].search([]):
            #print count
            if r.sn:
                mapping = self.env['vattu'].search([('sn','=',r.sn)],limit=1)
                if mapping:
                    so_luong_mapping +=1
                    #print 'co %s mapping'%(so_luong_mapping)
                    r.map_ltk_id = mapping.id
            else:
                r.map_ltk_id = False
            count +=1
        self.thong_bao_khac = u'Có %s noc mapping ltk' %( so_luong_mapping)
        return True   
    def map_noc_voi_kiemke(self):
        so_luong_mapping = 0
        count = 0
        for r in self.env['kknoc'].search([]):
            #print count
            if r.sn:
                mapping = self.env['kiemke'].search([('sn','=',r.sn)],limit=1)
                if mapping:
                    so_luong_mapping +=1
                    #print 'co %s mapping noc với kiểm kê'%(so_luong_mapping)
                    r.map_kiemke_id = mapping
            else:
                r.map_kiemke_id = False
            count +=1
        self.thong_bao_khac = u'Có %s noc mapping Kiểm kê' %( so_luong_mapping)
        return True   