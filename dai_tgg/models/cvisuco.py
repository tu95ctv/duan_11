# -*- coding: utf-8 -*-
from odoo import models, fields, api,exceptions,tools,_
from odoo.addons.dai_tgg.mytools import convert_odoo_datetime_to_vn_str,name_compute_char_join_rieng,name_compute,convert_odoo_datetime_to_vn_datetime


class CviSuCo(models.Model):
    _name = 'cvisuco'
    _auto = False
    name = fields.Char(compute='name_',store=True)
    noi_dung = fields.Text(string=u'Nội dung') 
    
    #moi them
    cvi_id = fields.Many2one('cvi')
    giao_ca_id = fields.Many2one('ctr',string=u'Ca Trực')
    # end moi them
    file_ids = fields.Many2many('dai_tgg.file','cvi_file_relate','cvi_id','file_id',string=u'Files đính kèm')
    doitac_ids = fields.Many2many('res.partner',string=u'Đối Tác')
    department_id = fields.Many2one('hr.department',string=u'Đơn vị tạo',compute='department_id_',store=True)
    department_ids = fields.Many2many('hr.department',string=u'Đơn vị liên quan',default=lambda self:[self.env.user.department_id.id],required=True)
#     department_id = fields.Many2one('hr.department',string=u'Phòng ban tạo',compute='department_id_',store=True)
#     department_ids = fields.Many2Many('hr.department',string=u'Phòng ban liên quan',default=lambda self:[self.env.user.department_id.id])
    loai_record = fields.Selection([(u'Công Việc',u'Công Việc'),(u'Sự Cố',u'Sự Cố'),(u'Sự Vụ',u'Sự Vụ'),(u'Comment',u'Comment')], string = u'Loại Record')
    loai_record_show =  fields.Selection([(u'Công Việc',u'Công Việc'),(u'Sự Cố',u'Sự Cố'),(u'Sự Vụ',u'Sự Vụ'),(u'Comment',u'Comment')], string = u'Loại Record',compute='loai_record_show_')
    ngay_bat_dau =  fields.Date(compute='ngay_bat_dau_',store=True,string=u'Ngày')
    gio_bat_dau = fields.Datetime(string=u'Giờ bắt đầu ', default=fields.Datetime.now)
    gio_ket_thuc = fields.Datetime(string=u'Giờ Kết Thúc')
    duration = fields.Float(digits=(6, 1), help='Duration in Hours',compute = '_get_duration', store = True,string=u'Thời lượng (giờ)')
    user_id = fields.Many2one('res.users',default =  lambda self: self.env.uid, string=u'Nhân viên tạo')   
#     noi_dung_trich_dan = fields.Char(compute='noi_dung_trich_dan_',store=True)
    ctr_ids  = fields.Many2many('ctr','ctr_cvi_relate','cvi_id','ctr_id',string=u'Ca Trực')
    ctr_show = fields.Char(compute='ctr_show_',string=u'Số ca trực')
    tvcv_id = fields.Many2one('tvcv', string=u'Thư Viện Công việc/ Loại Sự Cố/ Loại Sự Vụ',ondelete='restrict')
   
    
    # sua lai comment
    #tu
#     comment_ids = fields.One2many('comment','cvi_id',string=u'Comments/Ghi Chú/Tiến Độ')
    comment_ids = fields.One2many('cvi','cvi_id',string=u'Comments/Ghi Chú/Tiến Độ')
    comments_show = fields.Char(compute='comments_show_',string=u'Comments/Ghi Chú/Tiến Độ')
    trig_field = fields.Boolean()
    
                
                
                
    @api.depends('loai_record')
    def loai_record_show_(self):
        for r in self:
            r.loai_record_show = r.loai_record
            
    @api.depends('comment_ids')
    def comments_show_(self):
        for r in self:
            comment_ids_text_lists = []
            for i in r.comment_ids:
                i_text = name_compute_char_join_rieng(i, [
                    ('create_date',{'func':convert_odoo_datetime_to_vn_str}),#,'pr_more':u'('
                    ('create_uid',{'func': lambda r: r.name ,'join_char':u'-'}),#'sf_more':u')' 
                    ('noi_dung',{'pr':u''}),
                                          ],
                                       join_char = ' ')
                comment_ids_text_lists.append(i_text)
            r.comments_show = u' | '.join(comment_ids_text_lists)
#             r.comments_show_html = u'</br>'.join(comment_ids_text_lists)
                
        


            
            
            
    @api.depends('ctr_ids')
    def ctr_show_(self):
        for r in self:
            r.ctr_show =u'%s ca trực'% len(r.ctr_ids)
 
    @api.model
    def fields_view_get(self, view_id=None, view_type=False, toolbar=False, submenu=False):
        res = super(CviSuCo, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        
       
        if view_type in ['tree','form']:
            loai_record_context = self._context.get('default_loai_record')
            if loai_record_context in [u'Sự Cố',u'Sự Vụ',u'Comment']:
                fields = res.get('fields')
                fields['tvcv_id']['string'] =u'Loại ' + loai_record_context # ['|',('ctr_ids','=','active_id'),'&',('ctr_ids','!=',False),('gio_ket_thuc','=',False)]
            elif loai_record_context == u'Công Việc':
                fields = res.get('fields')
                fields['tvcv_id']['string'] =u'Thư Viện Công Việc'
#                 fields['user_id']['string'] =u'Nhân Viên Làm'
        if view_type =='form':
            if self._context.get('you_at_gd_form'):
                context='''{'thu_vien_da_chon_list':parent.get('thu_vien_da_chon_list'), 
                         'you_at_gd_form':context.get('you_at_gd_form'),
                         'loai_record_more':context.get('loai_record_more',[]),
                         'thu_vien_id_of_gd_parent_id':parent.get('tvcv_id'),  
                         'default_loai_record':loai_record,
                         'tree_view_ref':tree_view_ref, 
                         'search_view_ref': search_view_ref ,}'''
            else:
                context='''{
                         'loai_record_more':context.get('loai_record_more',[]),
                         'default_loai_record':loai_record,
                         'tree_view_ref':tree_view_ref, 
                         'search_view_ref': search_view_ref ,}'''
                
            fields['tvcv_id']['context'] = context
        return res
    @api.depends('loai_record')
    def tree_view_ref_(self):
        for r in self:
            if r.loai_record ==u'Công Việc':
                r.tree_view_ref = 'dai_tgg.tvcv_list'
                r.search_view_ref = 'dai_tgg.tvcv_search'
            else:
                r.tree_view_ref = 'dai_tgg.loai_suco_suvu_list'
                r.search_view_ref = 'dai_tgg.loai_suco_suvu_search'
                
#     @api.depends('noi_dung')
#     def noi_dung_trich_dan_(self):
#         for r in self:
#             if r.noi_dung:
#                 if len(r.noi_dung) > 30:
#                     r.noi_dung_trich_dan = r.noi_dung[:30] + u'...'
#                 else:
#                     r.noi_dung_trich_dan = r.noi_dung
                
                    
    def get_names(self):
            adict = {u'Công Việc':u'TVCV',u'Sự Cố':u'Loại',u'Sự Vụ':u'Loại',u'Comment':u'Loại'}
            if self.loai_record :
                adict=[('id',{'pr':u'%s id'%self.loai_record}),
                                              ('tvcv_id',{'pr':adict[self.loai_record],'func':lambda val:val.name}),
                                              ('noi_dung',{'pr':u'Nội Dung','skip_if_False':False}),
                                              ]
                if self._context.get('default_loai_record') ==u'Công Việc':
                    adict.append(('user_id',{'func':lambda r:r.name,'pr':u'Người Làm','skip_if_False':False}))
                name  = name_compute(self,adict=adict)
            else:
                name = False
            return name
    @api.multi
    def name_get(self):
        return [(r.id, r.get_names()) for r in self]
    
    @api.depends('tvcv_id','loai_record','noi_dung')
    def name_(self):
        for r in self:

            name = r.get_names()
            r.name = name
            if r.id:
                r.id_for_pivot = r.id
    @api.depends('gio_bat_dau')
    def ngay_bat_dau_(self):#trong su kien
        for r in self:
            if r.gio_bat_dau:
                r.ngay_bat_dau = convert_odoo_datetime_to_vn_datetime(r.gio_bat_dau).date()
                
    
    @api.depends('gio_ket_thuc','gio_bat_dau')
    def _get_duration(self):
        for r in self:
            if r.gio_bat_dau == False or r.gio_ket_thuc==False:
                r.duration = False
            else:
                start_date = fields.Datetime.from_string(r.gio_bat_dau)
                end_date = fields.Datetime.from_string(r.gio_ket_thuc)
                duration = (end_date - start_date)
                secs = duration.total_seconds()
                hour = secs / 3600
                r.duration = hour    