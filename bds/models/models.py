# -*- coding: utf-8 -*-

from odoo import models, fields, api,sql_db
from . import fetch 
from odoo.addons.bds.models.fetch import fetch, fetch_lazada
from odoo.addons.bds.models.fetch import get_quan_list_in_big_page
from odoo.addons.bds.models.fetch import update_phuong_or_quan_for_url_id,import_contact
import logging
from odoo.addons.bds.models.fetch import request_html
from bs4 import BeautifulSoup
_logger = logging.getLogger(__name__)
import smtplib

import logging
import threading
import time
from threading import current_thread
from odoo.addons.bds.models.fetch import g_or_c_ss
import re
import datetime
from odoo.osv import expression
# from email.MIMEMultipart import MIMEMultipart
# from email.MIMEText import MIMEText
# from odoo.addons.bds.models.fetch import page_handle_for_thread

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )


class URL(models.Model):
    _name = 'bds.url'
    _sql_constraints = [
        ('name_unique',
         'UNIQUE(url)',
         "The url must be unique"),
    ]
    name = fields.Char(compute='name_',store = True)
    url = fields.Char()
    description = fields.Char()    
    siteleech_id = fields.Many2one('bds.siteleech',compute='siteleech_id_',store=True)
    web_last_page_number = fields.Integer()
    quan_id = fields.Many2one('bds.quan',ondelete='restrict')
    phuong_id = fields.Many2one('bds.phuong')
    current_page = fields.Integer()
    current_page_for_first = fields.Integer()
    post_ids = fields.Many2many('bds.bds','url_post_relate','url_id','post_id')
    
    phuong_ids =  fields.Many2many('bds.phuong',compute='phuong_ids_',store=True)
    quan_ids =  fields.Many2many('bds.quan',compute='quan_ids_',store=True)
    
    @api.depends('post_ids')
    def quan_ids_(self):
        for r in self:
            r.quan_ids = r.post_ids.mapped('quan_id')
    @api.depends('post_ids')
    def phuong_ids_(self):
        for r in self:
            r.phuong_ids = r.post_ids.mapped('phuong_id')
    @api.depends('url')
    def siteleech_id_(self):
        for r in self:
            if r.url:
                if 'chotot' in r.url:
                    name = 'chotot'
                elif 'batdongsan' in r.url:
                    name = 'batdongsan'
                else:
                    name = re.search('\.(.*?)\.', r.url).group(1)
                chottot_site = g_or_c_ss(self,'bds.siteleech', {'name':name})
                r.siteleech_id = chottot_site.id
            
    @api.depends('url','quan_id','phuong_id')
    def name_(self):
        for r in self:
            surfix =  r.phuong_id.name or  r.quan_id.name  
            url = r.url
            r.name = (url if url else '') + ((' ' +  surfix ) if surfix else '')
    @api.multi
    def name_get(self):
        res = []
        for r in self:
            surfix =  r.quan_id.name or r.phuong_id.name
            new_name = r.url + ((' ' +  surfix ) if surfix else '' )+' current_page: %s'%r. current_page
            res.append((r.id,new_name))
        return res
    
class SiteDuocLeech(models.Model):
    _name = 'bds.siteleech'
    name = fields.Char()   
    

class Images(models.Model):
    _name = 'bds.images'
    url = fields.Char()
    bds_id = fields.Many2one('bds.bds')
    


  
class QuanHuyen(models.Model):
    _name = 'bds.quan'
    name = fields.Char()
    name_unidecode = fields.Char()
    name_without_quan = fields.Char()
    post_ids = fields.One2many('bds.bds','quan_id')
    muc_gia_quan = fields.Float(digit=(6,2),compute='muc_gia_quan_',store=True,string=u'Mức Đơn Giá(triệu/m2)')
    
    @api.depends('post_ids')
    def muc_gia_quan_(self):
        for r in self:
            sql_cmd = "select AVG(don_gia),count(id) from bds_bds where  quan_id = %s and  don_gia >= 40 and don_gia <300"%r.id
            self.env.cr.execute(sql_cmd)
            rsul = self.env.cr.fetchall()
            r.muc_gia_quan = rsul[0][0]
            
class Phuong(models.Model):
    _name = 'bds.phuong'
    name = fields.Char(compute='name_',store=True)
    name_phuong = fields.Char()
    quan_id = fields.Many2one('bds.quan')
    name_unidecode = fields.Char()
    @api.depends('name_phuong','quan_id')
    def name_(self):
        self.name = ( self.name_phuong if self.name_phuong else '' )+ ('-' + self.quan_id.name) if self.quan_id.name else ''
    @api.multi
    def name_get(self):
        res = []
        for r in self:
            new_name = u'phường ' + r.name
            res.append((r.id,new_name))
        return res  
class PosterNameLines(models.Model):
    _name = 'bds.posternamelines'
    username_in_site = fields.Char()
    site_id = fields.Many2one('bds.siteleech')
    poster_id = fields.Many2one('bds.poster')
class Poster(models.Model):
    _name = 'bds.poster'
    getphoneposter_ids = fields.Many2many('bds.getphoneposter','getphone_poster_relate','poster_id','getphone_id')
    phone = fields.Char()
    login = fields.Char()
    contact_address = fields.Char()
    name = fields.Char()
    sms_ids = fields.Many2many('bds.sms','sms_poster_relate','poster_id','sms_id')
    post_ids = fields.One2many('bds.bds','poster_id')
    mycontact_id = fields.Many2one('bds.mycontact',compute='mycontact_id_',store=True)
    cong_ty = fields.Char()
    ghi_chu = fields.Char()
    site_count_of_poster = fields.Integer(compute='site_count_of_poster_',store=True)
    count_chotot_post_of_poster = fields.Integer(compute='count_post_of_poster_',store=True,string=u'chotot count')
    count_bds_post_of_poster = fields.Integer(compute='count_post_of_poster_',store=True)
    count_post_all_site = fields.Integer(compute='count_post_of_poster_',store=True)
    nhan_xet = fields.Char()
    nha_mang = fields.Selection([('vina','vina'),('mobi','mobi'),('viettel','viettel'),('khac','khac')],compute='nha_mang_',store=True)
    log_text = fields.Char()
    username_in_site_ids = fields.One2many('bds.posternamelines','poster_id')
    username_in_site_ids_show = fields.Char(compute='username_in_site_ids_show_')
    quanofposter_ids = fields.One2many('bds.quanofposter','poster_id',compute='quanofposter_ids_',store = True)#,compute='quanofposter_ids_',store = True
    quan_id_for_search = fields.Many2one('bds.quan',related = 'quanofposter_ids.quan_id')
    quanofposter_ids_show = fields.Char(compute='quanofposter_ids_show_')
    trang_thai_lien_lac = fields.Selection([(u'chờ request zalo',u'chờ request zalo'),(u'request zalo',u'request zalo'),(u'added zalo',u'added zalo'),
                                            (u'Đã gửi sổ',u'Đã gửi sổ'),(u'Đã xem nhà',u'Đã xem nhà'),(u'Đã dẫn khách',u'Đã Dẫn khách')])
    da_goi_dien_hay_chua = fields.Selection([(u'Chưa gọi điện',u'Chưa gọi điện'),(u'Đã liên lạc',u'Đã liên lạc'),(u'Không bắt máy',u'Không đổ chuông')],
                                            default = u'Chưa gọi điện')
    is_recent = fields.Boolean(compute=  'is_recent_')
    exclude_sms_ids = fields.Many2many('bds.sms','poster_sms_relate','poster_id','sms_id')
    log_text = fields.Char()
    
    @api.depends('username_in_site_ids')
    def username_in_site_ids_show_(self):
        for r in self:
            username_in_site_ids_shows = map(lambda r : r.username_in_site + '(' + r.site_id.name +   ')',r.username_in_site_ids)
            r.username_in_site_ids_show = ','.join(username_in_site_ids_shows)
                
    @api.multi
    def is_recent_(self):
        for r in self:
            #print fields.Date.from_string(r.create_date)
            #print datetime.date.today() - datetime.timedelta(days=1)
            try:
                if fields.Date.from_string(r.create_date) >=  (datetime.date.today() - datetime.timedelta(days=1)):
                    r.is_recent = True
            except TypeError:
                pass

    

    
    @api.depends('phone')
    def nha_mang_(self):
        for r in self:
            patterns = {'vina':'(^091|^094|^0123|^0124|^0125|^0127|^0129|^088)',
                        'mobi':'(^090|^093|^089|^0120|^0121|^0122|^0126|^0128)',
                       'viettel': '(^098|^097|^096|^0169|^0168|^0167|^0166|^0165|^0164|^0163|^0162|^086)'}
            if r.phone:
                for nha_mang,pattern in patterns.items():
                    rs = re.search(pattern, r.phone)
                    if rs:
                        r.nha_mang = nha_mang
                        break
                if not rs:
                    r.nha_mang = 'khac'
                    
    @api.depends('post_ids','post_ids.gia')
    def quanofposter_ids_tanbinh(self):
        self.quanofposter_ids_common(u'Tân Bình')
    def quanofposter_ids_common(self,quan_name):
        for r in self:
            product_category_query =\
             '''select count(quan_id),quan_id,min(gia),avg(gia),max(gia) from bds_bds where poster_id = %s group by quan_id'''%r.id
            self.env.cr.execute(product_category_query)
            product_category = self.env.cr.fetchall()
            #print product_category
            for  tuple_count_quan in product_category:
                quan_id = int(tuple_count_quan[1])
                quan = self.env['bds.quan'].browse(quan_id)
                if quan.name in [quan_name]:#u'Quận 1',u'Quận 3',u'Quận 5',u'Quận 10',u'Tân Bình'
                    for key1 in ['count','avg']:
                        if key1 =='count':
                            value = tuple_count_quan[0]
                        elif key1 =='avg':
                            value = tuple_count_quan[3]
                        name = quan.name_unidecode.replace('-','_')
                        name = key1+'_'+name
                        setattr(r, name, value)
#                         #print 'set attr',name,value

    
    @api.depends('post_ids','post_ids.gia')
    def quanofposter_ids_(self):
        for r in self:
            quanofposter_ids_lists= []
            product_category_query_siteleech =\
             '''select count(quan_id),quan_id,min(gia),avg(gia),max(gia),siteleech_id from bds_bds where poster_id = %s group by quan_id,siteleech_id'''%r.id
            product_category_query_no_siteleech = \
            '''select count(quan_id),quan_id,min(gia),avg(gia),max(gia) from bds_bds where poster_id = %s group by quan_id'''%r.id
            a = {'product_category_query_siteleech':product_category_query_siteleech,
                 'product_category_query_no_siteleech':product_category_query_no_siteleech
                 }
            for k,product_category_query in a.items():
                self.env.cr.execute(product_category_query)
                quan_va_gia_fetchall = self.env.cr.fetchall()
#                 #print 'count(quan_id) %s,quan_id %s,min(gia) %s ,avg(gia) %s,max(gia) %s,siteleech_id %s' %*quan_va_gia_fetchall
#                 #print 'count(quan_id) %s,quan_id %s,min(gia) %s ,avg(gia) %s,max(gia) %s,siteleech_id %s' %*quan_va_gia_fetchall
#                 #print 'quan_va_gia_fetchall',quan_va_gia_fetchall
                for  tuple_count_quan in quan_va_gia_fetchall:
                    quan_id = int(tuple_count_quan[1])
                    if k =='product_category_query_no_siteleech':
                        siteleech_id =False
                    else:
                        siteleech_id = int(tuple_count_quan[5])
                        
                    quanofposter = g_or_c_ss(self,'bds.quanofposter', {'quan_id':quan_id,
                                                                 'poster_id':r.id,'siteleech_id':siteleech_id}, {'quantity':tuple_count_quan[0],
                                                                                    'min_price':tuple_count_quan[2],
                                                                                    'avg_price':tuple_count_quan[3],
                                                                                    'max_price':tuple_count_quan[4],
                                                                                     }, True)
                    quanofposter_ids_lists.append(quanofposter.id)#why????
                    if siteleech_id ==False:
                        r.min_price = tuple_count_quan[2]
                        r.avg_price = tuple_count_quan[3]
                        r.max_price = tuple_count_quan[4]
            r.quanofposter_ids = quanofposter_ids_lists
                    
    
    @api.depends('quanofposter_ids')
    def quanofposter_ids_show_(self):
        for r in self:
            value =','.join(r.quanofposter_ids.mapped('name'))
            r.quanofposter_ids_show = value
  
    
    @api.depends('post_ids')
    def count_post_of_poster_(self):
        for r in self:
            count_chotot_post_of_poster = self.env['bds.bds'].search([('poster_id','=',r.id),('link','like','chotot')])
            r.count_chotot_post_of_poster = len(count_chotot_post_of_poster)
            count_bds_post_of_poster = self.env['bds.bds'].search([('poster_id','=',r.id),('link','like','batdongsan')])
            r.count_bds_post_of_poster = len(count_bds_post_of_poster)
            r.count_post_all_site = len(r.post_ids)
    
    
    @api.depends('username_in_site_ids')
    def  site_count_of_poster_(self):
        for r in self:
            r.site_count_of_poster = len(r.username_in_site_ids)
    @api.depends('phone')
    def mycontact_id_(self):
        for r in self:
            r.mycontact_id = self.env['bds.mycontact'].search([('phone','=',r.phone)])
            
   

    def avg(self):
        product_category_query = '''select min(gia),avg(gia),max(gia) from bds_bds  where poster_id = %s and gia > 0'''%self.id
        self.env.cr.execute(product_category_query)
        product_category = self.env.cr.fetchall()
        #print product_category
        self.log_text = product_category

    
class QuanOfPoster(models.Model):
    _name = 'bds.quanofposter'
    name = fields.Char(compute='name_',store=True)
    quan_id = fields.Many2one('bds.quan')
    siteleech_id = fields.Many2one('bds.siteleech')
    quantity = fields.Integer()
    min_price = fields.Float(digits=(32,1))
    avg_price = fields.Float(digits=(32,1))
    max_price = fields.Float(digits=(32,1))
    poster_id = fields.Many2one('bds.poster')
    @api.depends('quan_id','quantity') 
    def name_(self):
        for r in self:
            r.name = (( r.siteleech_id.name + ' ' ) if r.siteleech_id.name else '') +  r.quan_id.name + ':' + str(r.quantity)
            

    
class SMS(models.Model):
    _name= 'bds.sms'
    name=  fields.Char()
    noi_dung = fields.Text()
    getphoneposter_ids = fields.One2many('bds.getphoneposter','sms_id')
    poster_ids = fields.Many2many('bds.poster','sms_poster_relate','sms_id','poster_id',compute='poster_ids_',store=True)
    len_poster_ids  =fields.Integer(compute='poster_ids_',store=True)
    @api.depends('getphoneposter_ids','name','noi_dung')
    def poster_ids_(self):
        for r in self:
            poster_ids = self.env['bds.poster'].search([('getphoneposter_ids','in',r.getphoneposter_ids.ids)])
            r.poster_ids = poster_ids
            r.len_poster_ids = len(poster_ids)
    @api.depends('getphoneposter_ids','getphoneposter_ids.poster_ids')
    def last_name_of_that_model_(self):
        for r in self:
            pass
   
class GetPhonePoster(models.Model):
    _name = 'bds.getphoneposter'
    name = fields.Char(compute='name_',store=True)
    is_repost_for_poster = fields.Boolean()
    filter_sms_or_filter_sql = fields.Selection([('sms_ids','sms_ids'),('by_sql','by_sql')],default='sms_ids')
#     name = fields.Char()
    sms_id = fields.Many2one('bds.sms',required=True)
    nha_mang = fields.Selection([('vina','vina'),('mobi','mobi'),('viettel','viettel'),('khac','khac')],default='vina')
    post_count_min = fields.Integer(default=10)
    len_poster = fields.Integer()
    exclude_poster_ids = fields.Many2many('bds.poster')#,inverse="exclude_poster_inverse_")
#     len_posters_of_sms = fields.Integer()
    phuong_loc_ids = fields.Many2many('bds.phuong')
    quan_ids = fields.Many2many('bds.quan')#,default = lambda self:self.default_quan())
    phone_list = fields.Text(compute='phone_list_',store=True)
    poster_ids = fields.Many2many('bds.poster','getphone_poster_relate','getphone_id','poster_id')#,compute='poster_ids_',store=True)
    loc_gian_tiep_quan_bds_topic = fields.Selection([(u'Qua Thống Kê Quận Object',u'Qua Thống Kê Quận Object'),(u'Qua BDS Object',u'Qua BDS Object'),(u'Qua BDS SQL',u'Qua BDS SQL')],default = u'Qua BDS SQL')
    gia_be_hon = fields.Float(digits=(6,2))
    bds_ids = fields.Many2many('bds.bds',compute='poster_ids_',store=True)
    poster_da_gui_cua_sms_nay_ids = fields.Many2many('bds.poster',compute='poster_ids_',store=True)
#     @api.onchange('poster_ids')
#     def danh_sach_doi_tac_(self):
#         for r in self:
#             r.danh_sach_doi_tac = '\r\n'.join(r.poster_ids.mapped('name'))
            
    @api.depends('sms_id','nha_mang')
    def name_(self):
        for r in self:
                r.name = u'get phone,id %s- nhà mạng %s' %(r.id,r.nha_mang)
#     def default_quan(self):
#         quan_10 = self.env['bds.quan'].search([('name','=',u'Quận 10')])
#         return [quan_10.id]
    
 
    @api.depends('poster_ids')
    def phone_list_(self):
        for r in self:
            phone_lists = filter(lambda l: not isinstance(l,bool),r.poster_ids.mapped('phone'))
            r.phone_list = ','.join(phone_lists)
   
    @api.onchange('gia_be_hon','loc_gian_tiep_quan_bds_topic','quan_ids','post_count_min','nha_mang','sms_id','exclude_poster_ids','poster_ids.exclude_sms_ids','phuong_loc_ids','is_repost_for_poster')
    def poster_ids_(self):
        
        def filter_for_poster(poster):
            if poster.id in r.exclude_poster_ids.ids:
                return False
            if r.sms_id.id in poster.exclude_sms_ids.ids:
                return False
            if r.is_repost_for_poster or r.filter_sms_or_filter_sql =='sms_ids':
                return True
            elif r.filter_sms_or_filter_sql =='by_sql':
                product_category_query =\
                         '''select distinct u.id,c.sms_id from bds_poster as u
            inner join getphone_poster_relate as r
            on u.id  = r.poster_id
            inner join bds_getphoneposter as c
            on  r.getphone_id= c.id
            where  u.id = %(r_id)s
            and c.sms_id =  %(sms_id)s
            '''%{'r_id':poster.id,
                 'sms_id':r.sms_id.id
                 }
                self.env.cr.execute(product_category_query)
                product_category = self.env.cr.fetchall()
                if product_category:
                    return False
                else:
                    return True  
                
        for r in self:
            if r.loc_gian_tiep_quan_bds_topic ==u'Qua Thống Kê Quận Object':
                if not r.sms_id:
                    pass
                else:
                    domain_tong = []
                    if r.nha_mang:
                        nha_mang_domain = ('nha_mang','=',r.nha_mang)
                        domain_tong.append(nha_mang_domain)
    
                    if r.quan_ids and r.post_count_min:
                        domain_tong = expression.AND([[( 'quanofposter_ids.quan_id','in',r.quan_ids.ids),('quanofposter_ids.quantity','>=',r.post_count_min)], domain_tong])
                    if r.phuong_loc_ids:
                        domain_tong = expression.AND([('phuong_id' ,'in',r.phuong_loc_ids.mapped('id')),domain_tong])
                        
                    if r.filter_sms_or_filter_sql =='sms_ids' and not r.is_repost_for_poster:
                        domain_tong.append(('sms_ids','!=',r.sms_id.id))
                    poster_quan10_greater_10 = self.env['bds.poster'].search(domain_tong)
                    poster_quan10_greater_10 = poster_quan10_greater_10.filtered(filter_for_poster )
                    r.poster_ids =poster_quan10_greater_10
                    r.len_poster = len(poster_quan10_greater_10)
            elif r.loc_gian_tiep_quan_bds_topic == u'Qua BDS SQL':
                slq_cmd = '''select distinct p.id from bds_bds as b inner join bds_poster as p on b.poster_id = p.id'''
                where_list = []
                if r.quan_ids:
#                     domain = expression.AND([[( 'quan_id','in',r.quan_ids.ids)],domain])
                    where_list.append(("b.quan_id in %s"%(tuple(r.quan_ids.ids),)).replace(',)',')'))
                if r.post_count_min:
#                     domain = expression.AND([[('count_post_all_site','>=',r.post_count_min)],domain])
                    where_list.append("b.count_post_all_site >= %s"%r.post_count_min)
                if r.gia_be_hon:
#                     domain = expression.AND([[('gia','<=',r.gia_be_hon)],domain])
                    where_list.append("b.gia <= %s"%r.gia_be_hon)
                if r.nha_mang:
                    where_list.append("p.nha_mang ='%s'"%r.nha_mang)
#                     post_ids = post_ids.filtered(lambda i: i.nha_mang == r.nha_mang)
                where_clause = u' and '.join(where_list)
                if where_list:
                    slq_cmd = slq_cmd + ' where ' + where_clause
                self.env.cr.execute(slq_cmd)
                rsul = self.env.cr.fetchall()
                poster_ids = map(lambda i:i[0],rsul)
                r.poster_ids = poster_ids
                r.len_poster = len(poster_ids)
                
                #print '*******rsul*******',rsul
            else:#if r.loc_gian_tiep_quan_bds_topic ==u'Qua BDS Object':
                domain = []
                if r.quan_ids:
                    domain = expression.AND([[( 'quan_id','in',r.quan_ids.ids)],domain])
                if  r.post_count_min:
                    domain = expression.AND([[('count_post_all_site','>=',r.post_count_min)],domain])
                if r.gia_be_hon:
                    domain = expression.AND([[('gia','<=',r.gia_be_hon)],domain])
                bds = self.env['bds.bds'].search(domain)
                post_ids = bds.mapped('poster_id')
                if r.nha_mang:
                    post_ids = post_ids.filtered(lambda i: i.nha_mang == r.nha_mang)
                    
                
                if not r.is_repost_for_poster:
                    post_ids_da_gui_cua_sms_nay_ids = r.sms_id.poster_ids
                    #print '***post_ids_da_gui_cua_sms_nay**',post_ids_da_gui_cua_sms_nay_ids
                    post_ids = post_ids.filtered(lambda r: r.id not in post_ids_da_gui_cua_sms_nay_ids.ids )
                    r.poster_da_gui_cua_sms_nay_ids = post_ids_da_gui_cua_sms_nay_ids
                r.poster_ids = post_ids
                r.len_poster = len(post_ids)
                r.bds_ids = bds
                
                                

        
class Importcontact(models.Model):
    _name = 'bds.importcontact'
    file = fields.Binary()
    land_contact_saved_number = fields.Integer()
    trigger_fields = fields.Selection([('bds.bds','bds.bds')])
    
    @api.multi
    def trigger(self):
        #print 'hihihihiihih trigger'
        self.env[self.trigger_fields].search([]).write({'is_triger':True})
    @api.multi
    def import_contact(self):
        import_contact(self)
        
  
    @api.multi
    def count_post_of_poster(self):
        for r in self.env['bds.poster'].search([]):
            post_of_poster_cho_tot = self.env['bds.bds'].search([('poster_id','=',r.id),('link','like','chotot')])
            count_bds_post_of_poster = self.env['bds.bds'].search([('poster_id','=',r.id),('link','like','batdongsan')])
            r.count_chotot_post_of_poster = len(post_of_poster_cho_tot)
            r.count_bds_post_of_poster = len(count_bds_post_of_poster)
            count_bds_post_of_poster = self.env['bds.bds'].search([('poster_id','=',r.id)])
            r.count_post_all_site = len(count_bds_post_of_poster)
            
    @api.multi
    def insert_count_by_sql(self):
        product_category_query = '''UPDATE bds_poster 
SET count_post_all_site = i.count
FROM (
    SELECT count(id),poster_id
    FROM bds_bds group by poster_id)  i
WHERE 
    i.poster_id = bds_poster.ID

'''    
        
        #self.env.cr.execute(product_category_query)
        
        bds_site = self.env['bds.siteleech'].search([('name','like','batdongsan')]).id
        chotot_site = self.env['bds.siteleech'].search([('name','like','chotot')]).id
        for x in [bds_site,chotot_site]:
            if x ==bds_site:
                name = 'bds'
            else:
                name ='chotot'
            product_category_query = '''UPDATE bds_poster 
    SET count_post_of_poster_%s = i.count
    FROM (
        SELECT count(id),poster_id,siteleech_id
        FROM bds_bds group by poster_id,siteleech_id)  i
    WHERE 
        i.poster_id = bds_poster.ID and i.siteleech_id=%s'''%(name,x)
        
            self.env.cr.execute(product_category_query) 
        #product_category = self.env.cr.fetchall()
        ##print product_category
    @api.multi
    def add_nha_mang(self):
        for r in self.env['bds.poster'].search([]):
            #print 'handling...',r.name
            patterns = {'vina':'(^091|^094|^0123|^0124|^0125|^0127|^0129|^088)',
                        'mobi':'(^090|^093|^089|^0120|^0121|^0122|^0126|^0128)',
                       'viettel': '(^098|^097|^096|^0169|^0168|^0167|^0166|^0165|^0164|^0163|^0162|^086)'}
            if r.phone:
                for nha_mang,pattern in patterns.items():
                    rs = re.search(pattern, r.phone)
                    if rs:
                        r.nha_mang = nha_mang
                        break
                if not rs:
                    r.nha_mang = 'khac'
    
    @api.multi
    def add_site_leech_tobds(self):
        chotot_site = self.env['bds.siteleech'].search([('name','ilike','chotot')])
        ctbds = self.env['bds.bds'].search([('link','ilike','chotot')])
        ctbds.write({'siteleech_id':chotot_site.id})
        
        chotot_site = self.env['bds.siteleech'].search([('name','ilike','batdongsan')])
        ctbds = self.env['bds.bds'].search([('link','ilike','batdongsan')])
        ctbds.write({'siteleech_id':chotot_site.id})
        
    
  
    @api.multi
    def add_min_max_avg_for_user(self):
        for c,r in enumerate(self.env['bds.poster'].search([])):
            #print 'hadling...one usee' ,c
            product_category_query = '''select min(gia),avg(gia),max(gia) from bds_bds  where poster_id = %s and gia > 0'''%r.id
            self.env.cr.execute(product_category_query)
            product_category = self.env.cr.fetchall()
            r.min_price = product_category[0][0]
            r.avg_price = product_category[0][1]
            r.max_price = product_category[0][2]
            #print' min,avg,max', product_category
            
    @api.multi
    def add_quan_lines_ids_to_poster(self):
        for c,r in enumerate(self.env['bds.poster'].search([])):
            #print 'hadling...one usee' ,c
            product_category_query =\
             '''select count(quan_id),quan_id,min(gia),avg(gia),max(gia) from bds_bds where poster_id = %s group by quan_id'''%r.id
            self.env.cr.execute(product_category_query)
            product_category = self.env.cr.fetchall()
            #print product_category
            for  tuple_count_quan in product_category:
                quan_id = int(tuple_count_quan[1])
                #quantity = int(tuple_count_quan[0].replace('L',''))
                quan = self.env['bds.quan'].browse(quan_id)
                if quan.name in [u'Quận 1',u'Quận 3',u'Quận 5',u'Quận 10',u'Tân Bình']:
                    for key1 in ['count','avg']:
                        if key1 =='count':
                            value = tuple_count_quan[0]
                        elif key1 =='avg':
                            value = tuple_count_quan[3]
                        name = quan.name_unidecode.replace('-','_')
                        name = key1+'_'+name
                        setattr(r, name, value)
                        #print 'set attr',name,value
                g_or_c_ss(self,'bds.quanofposter', {'quan_id':quan_id,
                                                             'poster_id':r.id}, {'quantity':tuple_count_quan[0],
                                                                                'min_price':tuple_count_quan[2],
                                                                                'avg_price':tuple_count_quan[3],
                                                                                'max_price':tuple_count_quan[4],
                                                                                 }, True)
                
                
    @api.multi
    def add_quan_lines_ids_to_poster_theo_siteleech_id(self):
        for c,r in enumerate(self.env['bds.poster'].search([])):
            
            product_category_query_siteleech =\
             '''select count(quan_id),quan_id,min(gia),avg(gia),max(gia),siteleech_id from bds_bds where poster_id = %s group by quan_id,siteleech_id'''%r.id
            product_category_query_no_siteleech = \
            '''select count(quan_id),quan_id,min(gia),avg(gia),max(gia) from bds_bds where poster_id = %s group by quan_id'''%r.id
            a = {'product_category_query_siteleech':product_category_query_siteleech,
                 'product_category_query_no_siteleech':product_category_query_no_siteleech
                 }
            for k,product_category_query in a.items():
                self.env.cr.execute(product_category_query)
                product_category = self.env.cr.fetchall()
                #print product_category
                for  tuple_count_quan in product_category:
                    quan_id = int(tuple_count_quan[1])
                    if k =='product_category_query_no_siteleech':
                        siteleech_id =False
                    else:
                        siteleech_id = int(tuple_count_quan[5])
                    g_or_c_ss(self,'bds.quanofposter', {'quan_id':quan_id,
                                                                 'poster_id':r.id,'siteleech_id':siteleech_id}, {'quantity':tuple_count_quan[0],
                                                                                    'min_price':tuple_count_quan[2],
                                                                                    'avg_price':tuple_count_quan[3],
                                                                                    'max_price':tuple_count_quan[4],
                                                                                     }, True)
                
            
    @api.multi
    def add_site_leech_to_url(self):
        for r in self.env['bds.url'].search([]):
            r.url = r.url
            
        
                          
class Errors(models.Model):
    _name = 'bds.error'
    url = fields.Char()
    code = fields.Char()
class Luong(models.Model):
    _name = 'bds.luong'
    threadname = fields.Char()
    url_id = fields.Many2one('bds.url')
    current_page = fields.Integer()

    
class Cron(models.Model):
 
    _inherit = "ir.cron"
    _logger = logging.getLogger(_inherit)
    @api.model
    def worker(self,thread_index,url_id,thread_number):
        new_cr = sql_db.db_connect(self.env.cr.dbname).cursor()
        uid, context = self.env.uid, self.env.context
        with api.Environment.manage():
            self.env = api.Environment(new_cr, uid, context)
            luong = g_or_c_ss(self,'bds.luong', {'threadname':str(1),'url_id':url_id})
            if luong[0].current_page==0:
                current_page = thread_index
            else:
                current_page = luong[0].current_page + thread_number
            luong[0].write({'current_page':current_page})
            new_cr.commit()
            self.env.cr.close()
def name_compute(r,adict=None,join_char = u' - '):
    names = []
    for fname,attr_dict in adict:
        val = getattr(r,fname)
        fnc = attr_dict.get('fnc',None)
        if fnc:
            val = fnc(val)
        if  not val:# Cho có trường hợp New ID
            if attr_dict.get('skip_if_False',True):
                continue
            if  fname=='id' :
                val ='New'
            else:
                val ='_'
        if attr_dict.get('pr',None):
            item =  attr_dict['pr'] + u': ' + unicode(val)
        else:
            item = unicode (val)
        names.append(item)
    if names:
        name = join_char.join(names)
    else:
        name = False
    return name
class IphoneType(models.Model):
    _name = 'iphonetype'
    name = fields.Char(compute='name_',store=True)
    name_cate = fields.Char()
    dung_luong = fields.Integer()
    nhap_khau_hay_chinh_thuc = fields.Selection([(u'nhập khẩu',u'Nhập Khẩu'),(u'chính thức',u'chính Thức')])
    @api.depends('name_cate','dung_luong','nhap_khau_hay_chinh_thuc')
    def name_(self):
        for r in self:
            r.name = \
            name_compute(r,[('name_cate',{}),
                            ('dung_luong',{}),
                            ('nhap_khau_hay_chinh_thuc',{})
                            ]
            )
class DienThoai(models.Model):
    _name = 'dienthoai'
    iphonetype_id = fields.Many2one('iphonetype')
    title = fields.Char()
    link = fields.Char()
    gia = fields.Float(digit=(6,2))
    so_luong = fields.Integer()
    duoc_ban_boi = fields.Char()
    is_bien_dong_item = fields.Boolean()
    original_itself_id = fields.Many2one('dienthoai')
    bien_dong_ids = fields.One2many('dienthoai','original_itself_id')
    topic_id  =  fields.Char()
    gia_hien_thoi = fields.Float(digit=(6,2))
    noi_dung_bien_dong = fields.Char()
    so_luong_hien_thoi = fields.Char()

class Fetch(models.Model):
    _name = 'bds.fetch'
    name = fields.Char(compute='name_',store=True)
    url_id = fields.Many2one('bds.url')
    url_ids = fields.Many2many('bds.url')
    last_fetched_url_id = fields.Integer()#>0
    web_last_page_number = fields.Integer()
    max_page = fields.Integer()
    is_for_first = fields.Selection([('1','1'),('2','2')])
#     page_begin = fields.Integer()
#     set_page_end = fields.Integer()
    set_number_of_page_once_fetch = fields.Integer(default=5)
    link_number = fields.Integer()
    update_link_number = fields.Integer()
    create_link_number = fields.Integer()
    existing_link_number = fields.Integer()
#     bds_ids_quantity = fields.Integer()
    
#     phuong_ids =  fields.Many2many('bds.phuong')
#     quan_ids =  fields.Many2many('bds.quan')
#     bds_ids = fields.Many2many('bds.bds','fetch_bds_relate','fetch_id','bds_id')
    note = fields.Char()
    update_field_of_existing_recorder = fields.Selection([(u'giá',u'giá'),(u'all',u'all')],default = u'all')
    lazada_url = fields.Char()
    test_url = fields.Char()
    test_html = fields.Text()
    invisible_or_show_html_lazada =  fields.Boolean(store=False)
    
    test_lazada = fields.Text()
    html_lazada = fields.Text()
    html_lazada_thread = fields.Text()
    html_lazada_thread_gia = fields.Text()
    
    @api.depends('set_number_of_page_once_fetch')
    def name_(self):
        for r in self:
            r.name = 'Fetch, id:%s-url_ids:%s-set_number_of_page_once_fetch: %s'%(r.id,u','.join(r.url_ids.mapped('name')),r.set_number_of_page_once_fetch)
    @api.multi
    def test_something(self):
        html = request_html(self.test_url)
#         soup = BeautifulSoup(html, 'html.parser')
#         soup.select('a[href^="http://example.com/"]')
#         rs = soup.select('meta[property="og:image"]')
#         log = u''
#         log +=u'%s'%rs
#         log +=u'%s'%map(lambda i:i['content'],rs)
        self.test_html = html

    @api.multi
    def fetch_lazada(self):
        fetch_lazada(self)
    @api.multi
    def fetch_laza_cron(self,id_fetch):
        fetch_id2 = self.browse(id_fetch)
        fetch_lazada(fetch_id2)
    
    @api.multi
    def test_mail(self):
        pass
#         fromaddr = 'nguyenductu@gmail.com'
#         toaddrs  = 'nguyenductu@gmail.com'
# #         msg = 'Why,Oh why fffffffffffform !'
#         
#         msg = MIMEMultipart()
#         msg['From'] = fromaddr
#         msg['To'] = toaddrs
#         msg['Subject'] = "SUBJECT OF THE MAIL"
#          
#         body = "YOUR MESSAGE HERE"
#         msg.attach(MIMEText(body, 'plain'))
#         text = msg.as_string()
# 
#         username = 'tunguyen19771@gmail.com'
#         password = 'Tu87cucgach'
#         server = smtplib.SMTP('smtp.gmail.com:587')
#         server.starttls()
#         server.login(username,password)
#         server.sendmail(fromaddr, toaddrs, text)
#         server.quit()
        #print 'dont'
        
        
        
    @api.multi
    def fetch(self):
#         _logger.warning(u'waring nguyến Đức tứ dep trai')
#         #print 'anh con no em'
#         _logger.info(u'info nguyến Đức tứ dep trai')
#         
#         return False
        fetch(self)
#         self.create_link_number=create_link_number
#         self.update_link_number =update_link_number
#         self.link_number = link_number
        
#         phuong_list = get_quan_list_in_big_page(self)
#         quan_list = get_quan_list_in_big_page(self,column_name='bds_bds.quan_id')
#         self.write({'phuong_ids':[(6,0,phuong_list)],'quan_ids':[(6,0,quan_list)]})#'quan_ids':[(6,0,quan_list)]
#         update_phuong_or_quan_for_url_id(self)


    

#     def fetch_cron(self,id_fetch):
#         fetch_id2 = self.browse(id_fetch)
#         fetch(fetch_id2,note=u'cập nhật lúc ' +  fields.Datetime.now(),is_fetch_in_cron = True)
    
#     @api.depends('write_date')
#     def bds_ids_quantity_(self):
#         for r in self:
#             r.bds_ids_quantity = len(r.bds_ids)
        
    @api.multi
    def group_quan(self):
#         product_category_query = '''select count(bds_bds.quan_id),bds_bds.phuong_id from odoo.addons.bds.models.fetch_bds_relate inner join bds_bds on fetch_bds_relate.bds_id = bds_bds.id where fetch_id = %s group by bds_bds.phuong_id'''%self.id
#         self.env.cr.execute(product_category_query)
#         product_category = self.env.cr.fetchall()
#         phuong_list = reduce(lambda y,x:([x[1]]+y) if x[1]!=None else y,product_category,[] )
        #self.phuong_ids = phuong_list
        phuong_list = get_quan_list_in_big_page(self)
        quan_list = get_quan_list_in_big_page(self,column_name='bds_bds.quan_id')
        self.write({'phuong_ids':[(6,0,phuong_list)],'quan_ids':[(6,0,quan_list)]})#'quan_ids':[(6,0,quan_list)]
        update_phuong_or_quan_for_url_id(self)
    
    

    def thread(self):
        thread_number = 5
        url_imput = self.url_id.url
        fetch_object = self
        for i in range(1,6):
            url_id = self.url_id.id
            w2 = threading.Thread(target=self.env['ir.cron'].worker,kwargs={'thread_index':i,'url_id':url_id,
                                                                            "thread_number" : thread_number,
                                                                            'url_imput':url_imput,
                                                                            "fetch_object":fetch_object
                                                                            })
            w2.start()
class CronFetch(models.Model):
    _name = 'cronfetch'
    fetch_ids = fields.Many2many('bds.fetch',required=True)
    fetch_current_id = fields.Many2one('bds.fetch')
    def fetch_cron(self):
        cronfetch_id =  self.search([],limit=1,order='id desc')
        if cronfetch_id:
            fetch_ids = cronfetch_id.fetch_ids
            if fetch_ids:
                if cronfetch_id.fetch_current_id:
                    try:
                        index_of_last_fetched_url_id = fetch_ids.ids.index( cronfetch_id.fetch_current_id.id)
                        new_index =  index_of_last_fetched_url_id+1
                    except ValueError:
                        new_index = 0
                else:
                    new_index =0
                if new_index > len(fetch_ids)-1:
                    new_index = 0    
                print 'new_index',new_index
                fetch_id = fetch_ids[new_index]
                fetch(fetch_id,  note=u'cập nhật lúc ' +  fields.Datetime.now(),is_fetch_in_cron = True)
                cronfetch_id.fetch_current_id = fetch_id.id
            else:
                raise ValueError('khong ton tai: fetch_ids')
        else:
            raise ValueError('khong ton tai cronfetch nao ca ')
        
        
class Mycontact(models.Model):
    _name = 'bds.mycontact'
    name = fields.Char()
    phone = fields.Char()