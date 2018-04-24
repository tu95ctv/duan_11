# -*- coding: utf-8 -*-
import re
import base64
from odoo import models, fields, api,sql_db
try:
    import urllib.request as urllib2_or_urllib_request
except:
    import urllib2 as urllib2_or_urllib_request
    

class bds(models.Model):
    _name = 'bds.bds'
    
    name = fields.Char(compute = 'name_',store = True)
    title = fields.Char()
    images_ids = fields.One2many('bds.images','bds_id')
    siteleech_id = fields.Many2one('bds.siteleech')
    thumb = fields.Char()
    thumb_view = fields.Binary(compute='thumb_view_')   
    present_image_link = fields.Char()
    present_image_link_show = fields.Binary(compute='present_image_link_show_')
    muc_gia = fields.Selection([('<1','<1'),('1-2','1-2'),('2-3','2-3'),('3-4','3-4'),('4-5','4-5'),('5-6','5-6'),('6-7','6-7'),('7-8','7-8'),('8-9','8-9'),('9-10','9-10'),('10-11','10-11'),('11-12','11-12'),('>12','>12')],
                               compute='muc_gia_',store = True,string=u'Mức Giá')
    muc_dt = fields.Selection(
        [('<10','<10'),('10-20','10-20'),('20-30','20-30'),('30-40','30-40'),('40-50','40-50'),('50-60','50-60'),('60-70','60-70'),('>70','>70')],
        compute='muc_dt_',store = True,string=u'Mức diện tích')
    don_gia = fields.Float(digit=(6,0),compute='don_gia_',store=True,string=u'Đơn giá')
    muc_don_gia = fields.Selection([('0-30','0-30'),('30-60','30-60'),('60-90','60-90'),
                                    ('90-120','90-120'),('120-150','120-150'),('150-180','150-180'),('180-210','180-210'),('>210','>210')],compute='muc_don_gia_',store=True)
    ti_le_don_gia = fields.Float(digits=(6,2),compute='ti_le_don_gia_',store=True)
    muc_ti_le_don_gia = fields.Selection([('0-0.4','0-0.4'),('0.4-0.8','0.4-0.8'),('0.8-1.2','0.8-1.2'),
                                    ('1.2-1.6','1.2-1.6'),('1.6-2.0','1.6-2.0'),('2.0-2.4','2.0-2.4'),('2.4-2.8','2.4-2.8'),('>2.8','>2.8')],compute='muc_ti_le_don_gia_',store=True)
    
    poster_id = fields.Many2one('bds.poster')
    post_ids_of_user  = fields.One2many('bds.bds','poster_id',related='poster_id.post_ids')
    html = fields.Html()
    html_show = fields.Text(compute='html_show_',store=True,string = u'Nội dung')
    gia = fields.Float()
    area = fields.Float(digits=(32,1))
    address=fields.Char()
    quan_id = fields.Many2one('bds.quan',ondelete='restrict')
    quan_tam = fields.Datetime(string=u'Quan Tâm')
    hem_truoc_nha = fields.Float(digit=(6,2))
    comment = fields.Float(digit=(6,2))
    ket_cau = fields.Selection([(u'Đất Trống',u'Đất Trống'),(u'Cấp 4',u'Cấp 4'),(u'1 Tầng',u'1 Tầng'),(u'2 Tầng',u'2 Tầng'),(u'3 Tầng',u'3 Tầng'),(u'4 Tầng',u'4 Tầng'),(u'5 Tầng',u'5 Tầng'),(u'lon hon 5 ',u'lon hon 5')])
#     quan_id_selection = fields.Selection([])

    quan_id_selection = fields.Selection('get_quan_')
    @api.multi
    def open_something(self):
        return {
                'name': 'abc',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'bds.bds',
                'view_id': self.env.ref('bds.bds_form').id,
                'type': 'ir.actions.act_window',
                'res_id': self.id,
#                 'context': context,
                'target': 'new'
            }
        
    def get_quan_(self):
        oQuans = self.env['bds.quan'].search([])
        rs = map(lambda i:(i.name,i.name),oQuans)
        return rs
    phuong_id = fields.Many2one('bds.phuong')
    link = fields.Char()
    cho_tot_link_fake = fields.Char(compute='cho_tot_link_fake_')
    ngay_dang = fields.Datetime()
    
    count_chotot_post_of_poster = fields.Integer(related= 'poster_id.count_chotot_post_of_poster',store=True,string=u'chotot post quantity')
    count_bds_post_of_poster = fields.Integer(related= 'poster_id.count_bds_post_of_poster',store=True,string=u'bds post quantity')
    count_post_all_site = fields.Integer(related= 'poster_id.count_post_all_site',store=True)
    data = fields.Text()
    url_ids = fields.Many2many('bds.url','url_post_relate','post_id','url_id')
    is_triger = fields.Boolean()
    
    @api.depends('ti_le_don_gia','is_triger')
    def muc_ti_le_don_gia_(self):
        muc_dt_list =[('0-0.4','0-0.4'),('0.4-0.8','0.4-0.8'),('0.8-1.2','0.8-1.2'),
                                    ('1.2-1.6','1.2-1.6'),('1.6-2.0','1.6-2.0'),('2.0-2.4','2.0-2.4'),('2.4-2.8','2.4-2.8'),('>2.8','>2.8')]
        for r in self:
            selection = None
            for muc_gia_can_tren in range(1,8):
                if r.ti_le_don_gia < muc_gia_can_tren*0.4:
                    selection = muc_dt_list[muc_gia_can_tren-1][0]
                    r.muc_ti_le_don_gia = selection
                    break
            if not selection:
                r.muc_ti_le_don_gia = '>2.8'
    @api.depends('don_gia','quan_id')
    def ti_le_don_gia_(self):
        for r in self:
            try:
                if r.don_gia and r.quan_id.muc_gia_quan:
                    r.ti_le_don_gia = r.don_gia/r.quan_id.muc_gia_quan
            except:
                pass
                
    @api.depends('gia','area')
    def don_gia_(self):
        for r in self:
            if r.gia:
                if r.area:
                    r.don_gia = r.gia*1000/r.area
            else:
                r.don_gia = False
    @api.depends('don_gia')
    def muc_don_gia_(self):
        muc_dt_list =[('0-30','0-30'),('30-60','30-60'),('60-90','60-90'),
                                    ('90-120','90-120'),('120-150','120-150'),('150-180','150-180'),('180-210','180-210'),('>210','>210')]
        for r in self:
            selection = None
            for muc_gia_can_tren in range(1,8):
                if r.don_gia < muc_gia_can_tren*30:
                    selection = muc_dt_list[muc_gia_can_tren-1][0]
                    r.muc_don_gia = selection
                    break
            if not selection:
                r.muc_don_gia = '>210'
    @api.depends('area')
    def muc_dt_(self):
        muc_dt_list = [('<10','<10'),('10-20','10-20'),('20-30','20-30'),('30-40','30-40'),('40-50','40-50'),('50-60','50-60'),('60-70','60-70'),('>70','>70')]
        for r in self:
            selection = None
            for muc_gia_can_tren in range(1,8):
                if r.area < muc_gia_can_tren*10:
                    selection = muc_dt_list[muc_gia_can_tren-1][0]
                    r.muc_dt = selection
                    break
            if not selection:
                r.muc_dt = '>70'
    @api.depends('gia','is_triger')
    def muc_gia_(self):
        muc_gia_list = [('<1','<1'),('1-2','1-2'),('2-3','2-3'),('3-4','3-4'),('4-5','4-5'),('5-6','5-6'),('6-7','6-7'),('7-8','7-8'),('8-9','8-9'),('9-10','9-10'),('10-11','10-11'),('11-12','11-12'),('>12','>12')]
        for r in self:
            selection = None
            for muc_gia_can_tren in range(1,len(muc_gia_list)):
                if r.gia < muc_gia_can_tren:
                    selection = muc_gia_list[muc_gia_can_tren-1][0]
                    r.muc_gia = selection
                    break
            if not selection:
                r.muc_gia = muc_gia_list[-1][0]
    @api.depends('html')
    def html_show_(self):
        for r in self:
            
            if  r.html and len(r.html) > 201:
                r.html_show = r.html[:200] + '...'
            else:
                r.html_show = r.html
    @api.multi
    def cho_tot_link_fake_(self):
        for r in self:
            if 'chotot' in r.link:
                rs = re.search('/(\d*)$',r.link)
                id_link = rs.group(1)
                r.cho_tot_link_fake = 'https://nha.chotot.com/quan-10/mua-ban-nha-dat/' + 'xxx-' + id_link+ '.htm'
    @api.depends('thumb')
    def thumb_view_(self):
        for r in self:
            if r.thumb:
                photo = base64.encodestring(urllib2_or_urllib_request.urlopen(r.thumb).read())
                r.thumb_view = photo 
    @api.depends('present_image_link')
    def present_image_link_show_(self):
        for r in self:
            if r.present_image_link:
                photo = base64.encodestring(urllib2_or_urllib_request.urlopen(r.present_image_link).read())
                r.present_image_link_show = photo 

    @api.depends('title')
    def name_(self):
        self.name = self.title