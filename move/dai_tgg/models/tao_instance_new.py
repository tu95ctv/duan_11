 # -*- coding: utf-8 -*-
import re
import xlrd
import time
import datetime
from odoo.exceptions import UserError
from odoo import  fields
import base64
from copy import deepcopy
import logging
_logger = logging.getLogger(__name__)
from odoo.osv import expression

def get_or_create_object_has_x2m (self, class_name, search_dict,
                                write_dict ={},is_must_update=False, noti_dict=None,
                                inactive_include_search = False, x2m_key=[]):
    
    if x2m_key:
        x2m_key_first = x2m_key[0]
        key_first_values = search_dict[x2m_key_first]
        result = []
        for key_first_value in key_first_values:
            search_dict[x2m_key_first] = key_first_value
            object = get_or_create_object_sosanh(self, class_name, search_dict,
                                    write_dict =write_dict, is_must_update=is_must_update, noti_dict=noti_dict,
                                    inactive_include_search = inactive_include_search)
            result.append(object.id)
            
        return [(6,False,result)]
    else:
        return get_or_create_object_sosanh(self, class_name, search_dict,
                                    write_dict =write_dict, is_must_update=is_must_update, noti_dict=noti_dict,
                                    inactive_include_search = inactive_include_search).id



        

def get_or_create_object_sosanh(self, class_name, search_dict,
                                write_dict ={},is_must_update=False, noti_dict=None,
                                inactive_include_search = False):
    
    
    if noti_dict !=None:
        this_model_noti_dict = noti_dict.setdefault(class_name,{})
    else:
        this_model_noti_dict = None
    if inactive_include_search:
        domain_not_active = ['|',('active','=',True),('active','=',False)]
    else:
        domain_not_active = []
    domain = []
    for i in search_dict:
        tuple_in = (i,'=',search_dict[i])
        domain.append(tuple_in)
    domain = expression.AND([domain_not_active, domain])
    searched_object  = self.env[class_name].search(domain)
    if not searched_object:
        search_dict.update(write_dict)
        print '***search_dict***',search_dict
        created_object = self.env[class_name].create(search_dict)
        if this_model_noti_dict !=None:
            this_model_noti_dict['create'] = this_model_noti_dict.get('create', 0) + 1
        return_obj =  created_object
    else:
        if not is_must_update:
            is_write = False
            for f_name in write_dict:
                field_dict_val = write_dict[f_name]
                orm_field_val = getattr(searched_object, f_name)
                try:
                    converted_orm_val_to_dict_val = getattr(orm_field_val, 'id', orm_field_val)
                    if converted_orm_val_to_dict_val == None: #recorderset.id ==None when recorder sset = ()
                        converted_orm_val_to_dict_val = False
                except:#not singelton
                    pass
                if isinstance(orm_field_val, datetime.date):
                    converted_orm_val_to_dict_val = fields.Date.from_string(orm_field_val)
                if converted_orm_val_to_dict_val != field_dict_val:
                    is_write = True
                    break
        else:
            is_write = True
        if is_write:
            searched_object.write(write_dict)
            if this_model_noti_dict !=None:
                this_model_noti_dict['update'] = this_model_noti_dict.get('update',0) + 1
        else:#'not update'
            if this_model_noti_dict !=None:
                this_model_noti_dict['skipupdate'] = this_model_noti_dict.get('skipupdate',0) + 1
        return_obj = searched_object
    return return_obj
    
EMPTY_CHAR = [u'',u' ',u'\xa0']


def empty_string_to_False(readed_xl_value):
    if  isinstance(readed_xl_value,unicode) or isinstance(readed_xl_value,str) :
        if readed_xl_value  in EMPTY_CHAR:
            return False
        rs = re.search('\S',readed_xl_value)
        if not rs:
            return False
    return readed_xl_value





# def active_function(val):
#     return False if val ==u'na' else True

def read_merge_cell(sheet,row,col,merge_tuple_list):
    for crange in merge_tuple_list:
        rlo, rhi, clo, chi = crange
        if row>=rlo and row < rhi and col >=clo and col < chi:
            row = rlo
            col = clo
            break
    val = sheet.cell_value(row,col)
    return val
def read_excel_cho_field(sheet, row, col_index,merge_tuple_list):
    print 'row','col',row, col_index,sheet
    val = read_merge_cell(sheet, row ,col_index,merge_tuple_list)
    print 'val',val
    val = empty_string_to_False(val)
    return val
            
### Xong khai bao
def recursive_read_field_attr(self,MODEL_DICT):
    model_name = MODEL_DICT['model']
    fields= self.env[model_name]._fields
    for field_tuple in MODEL_DICT.get('fields',[]):
        f_name = field_tuple[0]
        field_attr = field_tuple[1]
        if not field_attr.get('for_excel_readonly'):
            field = fields[f_name]
#             if field.type =='many2many' or field.type == 'one2many':
            field_attr['field_type'] = field.type
            if field.comodel_name:
                field_attr['model'] = field.comodel_name
#                 field_attr['field_type'] = field.type
                recursive_read_field_attr(self,field_attr)
def loop_through_fields_to_add_col_index_match_xl_title(MODEL_DICT, value_may_be_title, row, col):
    print 'value_may_be_title',value_may_be_title
    is_map_xl_title = False
    is_map_xl_title_foreinkey = False
    for field,field_attr in MODEL_DICT.get('fields',[]):
        if field_attr.get('set_val',None) != None:
            continue
        if field_attr.get('xl_title') ==None and field_attr.get('col_index') !=None:
            continue# cos col_index
        elif field_attr.get('xl_title'):
            if isinstance(field_attr['xl_title'],unicode) or  isinstance(field_attr['xl_title'],str):
                xl_title_s = [field_attr['xl_title']]
            else:
                xl_title_s =  field_attr['xl_title']
            for xl_title in xl_title_s:
                if xl_title == value_may_be_title:
                    field_attr['col_index'] = col
                    is_map_xl_title = True        
                    break
        elif field_attr.get('fields'):
            is_map_xl_title_foreinkey = loop_through_fields_to_add_col_index_match_xl_title(field_attr, value_may_be_title, row, col)
    return is_map_xl_title or is_map_xl_title_foreinkey


def create_instace (self, MODEL_DICT, sheet, row, merge_tuple_list, needdata, noti_dict, main_call_create_instace = None):
    key_search_dict = {}
    update_dict = {}
    value_fields_of_instance_dicts = {}
    model_name = MODEL_DICT['model']
    
    if main_call_create_instace == model_name:
        needdata['value_fields_of_instance_dicts'] = value_fields_of_instance_dicts
    xl_val = None
    required_valid = True
    field_type_of_this_model = MODEL_DICT.get('field_type')
   
        
    
    
    for count, field_field_attr in enumerate(MODEL_DICT['fields']):
        field_name = field_field_attr[0]
        field_attr = field_field_attr[1]
        col_index = field_attr.get('col_index')
        func =  field_attr.get('func')
        x2m_key = []
        if field_attr.get('x2m_list'):
                x2m_key.append(field_name)
        if field_attr.get('set_val'):
            xl_val = field_attr.get('set_val')
        elif not field_attr.get('fields') and col_index =='skip_field_if_not_found_column_in_some_sheet':
            xl_val = False
#             continue #field nay khong effect toi search va update neu khong tim thay
        elif not field_attr.get('fields') and col_index !=None:
            xl_val = read_excel_cho_field(sheet, row, col_index, merge_tuple_list)
            if xl_val   != False and field_type_of_this_model != None and '2many' in field_type_of_this_model and field_attr.get('x2m_list'):
                xl_val = xl_val.split(',')
                xl_val = map(lambda i: i.strip(),xl_val)
        elif field_attr.get('fields'):#and field_attr.get('field_type')=='many2one':
            xl_val, value_fields_of_instance_dicts_childrend, required_valid_childrend  = create_instace (self, field_attr, sheet, row, merge_tuple_list, needdata, noti_dict)
            a_field_val_dict = value_fields_of_instance_dicts.setdefault(field_name,{})
            a_field_val_dict['fields'] = value_fields_of_instance_dicts_childrend
        
#             pass
#             unicode_m2m_list = val.split(',')
#             unicode_m2m_list = map(lambda i: i.strip(),unicode_m2m_list)
#             unicode_m2m_list = filter(check_variable_is_not_empty_string, unicode_m2m_list)
#             def create_or_get_one_in_m2m_value(val):
#                 val = val.strip()
#                 if val:
#                     return get_or_create_object_sosanh(self,field_attr['model'], {key_name:val},noti_dict=noti_dict,model_effect_noti_dict='tvcv')
#             object_m2m_list = map(create_or_get_one_in_m2m_value, unicode_m2m_list)
#             m2m_ids = map(lambda x:x.id, object_m2m_list)
#             val = [(6, False, m2m_ids)]
            
        elif func:
            pass
        else:
            raise ValueError('thế đéo gì...')
        xl_val = func(xl_val, needdata) if func else xl_val
        a_field_val_dict = value_fields_of_instance_dicts.setdefault(field_name,{})
        a_field_val_dict['val'] = xl_val
        required = field_attr.get('required',False)
        if required and xl_val==False:
            required_valid = False
            obj_id = False
        if not required_valid:
            return obj_id , value_fields_of_instance_dicts, required_valid
        if not field_attr.get('for_excel_readonly'):
            key_or_not = field_attr.get('key')
            if key_or_not==True:
                key_search_dict [field_name] = xl_val
            elif key_or_not == 'Both':
                key_search_dict [field_name] = xl_val
                update_dict [field_name] = xl_val
            else:
                update_dict [field_name] = xl_val
       
    inactive_include_search = MODEL_DICT.get('inactive_include_search',False)
    print '**key_search_dict',key_search_dict
    print '**update_dict',update_dict
    obj_id = get_or_create_object_has_x2m(self, model_name, key_search_dict, update_dict,
                                is_must_update=True,noti_dict=noti_dict,
                                inactive_include_search  = inactive_include_search, x2m_key = x2m_key)
    return obj_id,value_fields_of_instance_dicts, required_valid
def convert_integer(val,needdata):
    try:
        return int(val)
    except:
        return 0
    
def chon_location_id(val,needdata):
    location_id = \
    needdata['value_fields_of_instance_dicts']['location_id3']['val'] or \
    needdata['value_fields_of_instance_dicts']['location_id2']['val'] or \
    needdata['value_fields_of_instance_dicts']['location_id1']['val'] or \
    needdata['value_fields_of_instance_dicts']['location_id_goc']['val']
    return location_id
def importthuvien(odoo_or_self_of_wizard):
    self = odoo_or_self_of_wizard
    for r in self:
           
#             if r.type_choose =='stock.inventory.line':
            recordlist = base64.decodestring(r.file)
            xl_workbook = xlrd.open_workbook(file_contents = recordlist)
            loop_dict = {
                u'stock.inventory.line': {
                'title_rows':[4,5],
                'begin_data_row_offset_with_title_row' :3,
                'sheet_names':[u'IP (VN2, VNP)'],
                'model':'stock.inventory.line',
                'fields' : [
                    
('inventory_id', {'func': lambda val,needdata:get_or_create_object_sosanh(self,'stock.inventory', {'name':needdata['sheet_name']}, {}).id,'key':False}),
('location_id_goc', {'func':lambda val,needdata: self.env['stock.location'].search([('name','=','LTK Dự Phòng')]).id,'key':False, 'for_excel_readonly' :True}),                       
('location_id1',{'model':'stock.location', 'for_excel_readonly':True,
                                       'fields':[
                                                ('name',{'func':None,'xl_title':u'Phòng', 'key':True,'required': True}),
                                                ('location_id',{'func':lambda val,needdata: needdata['value_fields_of_instance_dicts']['location_id_goc']['val'], 'key':True})
                                                ]
                                       }), 
('location_id2',{'model':'stock.location', 'for_excel_readonly':True,
                                       'fields':[
                                                ('name',{'func':None,'xl_title':u'Tủ/Kệ', 'key':True,'required': True}),
                                                ('location_id',{'func':lambda val,needdata: needdata['value_fields_of_instance_dicts']['location_id1']['val'], 'key':True})
                                                ]
                                       }),                                           
('location_id3',{'model':'stock.location', 'for_excel_readonly':True,
                                       'fields':[
                                                ('name',{'func':None,'xl_title':u'Ngăn', 'key':True,'required': True}),
                                                ('location_id',{'func':lambda val,needdata: needdata['value_fields_of_instance_dicts']['location_id2']['val'], 'key':True})
                                                ]
                                       }),                                          

('location_id', {'func':chon_location_id, 'key':False}),

('product_id',{'key':True,'required':True,
               'fields':[
                        ('name',{'func':None,'xl_title':u'TÊN VẬT TƯ','key':True,'required':True}),
                        ]
               }),  
('prod_lot_id', {'key':True,
                  'fields':[
                    ('name',{'func':lambda val,needdata: int(val) if isinstance(val,float) else val,'xl_title':u'Seri Number','key':True,'required':True}),
                    ('product_id',{'func':lambda v,n:n['value_fields_of_instance_dicts']['product_id']['val'] }),
                      ]
                  }),
     

 
                         ]
                },#End stock.inventory.line'
                         
                u'Thư viện công việc': {
                'inactive_include_search':True,
                'title_rows' : range(1,4), 
                'begin_data_row_offset_with_title_row' :1,
                'sheet_names':xl_workbook.sheet_names(),
                'model':'tvcv',
                'fields' : [
                        ('name', {'func':None,'xl_title':u'Công việc','key':'Both' , 'required':True } ),#'func_de_tranh_empty':lambda r:  len(r) > 2
                        ( 'loai_record',{'func':None,'set_val':u'Công Việc', 'key':False }),
                        ( 'cong_viec_cate_id',{'func':lambda val,needdata:get_or_create_object_sosanh(self, 'tvcvcate', {'name':needdata['sheet_name']}, {} ).id , 'key':False }),
                        ( 'code',{'func':None,'xl_title':u'Mã CV','key':False }),
                        ('do_phuc_tap',{'func':convert_integer,'xl_title':u'Độ phức tạp','key':False}),
                        ('don_vi',{'fields':[
                                                ('name',{'key':True, 'required':True, 'xl_title':u'Đơn vị' }),
                                                ],'key' : False, 'required' : False}),
                         ('thoi_gian_hoan_thanh',{'func':convert_integer, 'xl_title':u'Thời gian hoàn thành','key':False}),
                         ('dot_xuat_hay_dinh_ky',{'fields':[
                                                ('name',{'key':True, 'required':True,'col_index':7}),
                                                ],'key' : False,'required' : False}),  
                         ('ghi_chu',{'func':None,'xl_title':u'Ghi chú','key':False}),
                         
#                           ('children_ids',{'model':'tvcv',
#                         'xl_title':u'Các công việc con',
#                         'key':False,'col_index':'skip_field_if_not_found_column_in_some_sheet','m2m':True,'dung_ham_de_tao_val_rieng':ham_tao_tv_con
#                                                                                                     }),
#                         )
                        ('children_ids',{'key':False,'required':False,
                                       'fields':[
                                                ('name',{'xl_title':u'Các công việc con',  'key':True, 'required':True, 'x2m_list':True, 'col_index':'skip_field_if_not_found_column_in_some_sheet'}),
                                                ]
                                       }),  
                         
                         ('active',{'func':lambda val, needdata: False if val ==u'na' else True,'xl_title':u'active','key':False,'col_index':'skip_field_if_not_found_column_in_some_sheet','use_fnc_even_cell_is_False':True}),
                   
                      
                      
                      ]
                },#End stock.inventory.line'
                                  
                
                u'User': {
                'title_rows' : [1], 
                'begin_data_row_offset_with_title_row' :1,
                'sheet_names': ['Sheet1'],
                'model':'res.users',
                'fields' : [
                        ('name', {'func':None,'xl_title':u'Họ và Tên','key':False,'required':True}),
                         ( 'login',{'func':None,'xl_title':u'Địa chỉ email','key':True ,'required':True}),
                         ('phone',{'func':None,'xl_title':u'Số điện thoại','key':False}),
#                         ('cac_sep_ids',{'func':None,'xl_title':u'Cấp trên','key':False,'key_name':'login','m2m':True}),
                         
                         ('cac_sep_ids',{'key':False,'required':False,
               'fields':[
                        ('login',{'xl_title':u'Cấp trên',  'key':True, 'required':True, 'x2m_list':True}),

                        ]
               }),  
                         ('job_id',{'key':False,'required':False,
               'fields':[
                        ('name',{'xl_title':u'Chức vụ',  'key':True, 'required':True, 'func':lambda v,n: u'Nhân Viên' if v==False else v }),
                        ]
               }),  
                                
                    ('department_id',{'key':False,'required':False,
               'fields':[
                        ('name',{'xl_title':u'Bộ Phận',  'key':True, 'required': True}),
                        ]
               }),  
                                
#                         ('department_id',{'model':'hr.department','func':None,'xl_title':u'Bộ Phận','key':False}),
                      ]
                },#End stock.inventory.line'
                         
                }#end tag loop_dict
                
                
                
                
            noti_dict = {}
            
                
            choose_dict = loop_dict[r.type_choose]
#             choose_dict = choose_dict
            recursive_read_field_attr(self,choose_dict)
            for loop_instance in choose_dict.get('loop_list',['main']):
                for sheet_name in choose_dict['sheet_names']:
                    print 'sheet_name',sheet_name
                    MODEL_DICT = deepcopy(choose_dict)
                    needdata = {}
                    needdata['sheet_name'] = sheet_name
                    sheet = xl_workbook.sheet_by_name(sheet_name)
                    row_title_index =None
                    for row in choose_dict['title_rows']:
                        for col in range(0,sheet.ncols):
                            value_may_be_title = unicode(sheet.cell_value(row,col))
                            is_map_xl_title = loop_through_fields_to_add_col_index_match_xl_title( MODEL_DICT, value_may_be_title, row, col)
                            if is_map_xl_title:
                                row_title_index = row
                    merge_tuple_list =  sheet.merged_cells
                    for c,row in enumerate(range(row_title_index + choose_dict.get('begin_data_row_offset_with_title_row',1), sheet.nrows)):
                        print 'row',row
                        obj_id, value_fields_of_instance_dicts,required = create_instace( self, MODEL_DICT, sheet, row, merge_tuple_list, needdata, noti_dict,main_call_create_instace=choose_dict['model'])
           
            r.create_number = noti_dict.get('create')
            r.update_number = noti_dict.get('update')
            r.skipupdate_number = noti_dict.get('skipupdate')
            r.log= noti_dict
            

            
            
