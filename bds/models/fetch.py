# -*- coding: utf-8 -*-
# import urllib2
import sys
VERSION_INFO   = sys.version_info[0]
from odoo import models
# from urllib.request import urlopen
try:
    import urllib.request as url_lib
except:
    import urllib2 as url_lib


from bs4 import BeautifulSoup
import datetime
import re
from unidecode import unidecode
import xlrd
import base64
import json
from time import sleep
import pytz
import logging
from odoo import  fields
import math
_logger = logging.getLogger(__name__)
from odoo.osv import expression
# from email.MIMEMultipart import MIMEMultipart
# from email.MIMEText import MIMEText
import smtplib

# def fetch(self,note=False,is_fetch_in_cron = False):
#     #print '**** fetch ____'
#     fetch1(self,note,is_fetch_in_cron)
headers = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36' }
    


def request_html(url):
    headers = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36' }
    print ( '**VERSION_INFO**',VERSION_INFO,'url',url)
    if VERSION_INFO == 3:
        req = url_lib.Request(url, None, headers)
        rp= url_lib.urlopen(req)
        mybytes = rp.read()
        html = mybytes.decode("utf8")
    elif VERSION_INFO ==2:
        req = url_lib.Request(url, None, headers)
        html = url_lib.urlopen(req).read()
    return html


def fetch(self,note=False,is_fetch_in_cron = False):
    url_ids = self.url_ids.ids
    #print 'url_ids',url_ids
#     return 'url_ids',url_ids
#     _logger.warning('self.url_ids %s'%self.url_ids)
#     _logger.info('self.url_ids %s'%self.url_ids)
#     return True
#     url_ids_id_lists = url_ids.mapped('id')
    if not self.last_fetched_url_id:
        new_index = 0
    else:
        index_of_last_fetched_url_id = url_ids.index(self.last_fetched_url_id)
        new_index =  index_of_last_fetched_url_id+1
        if new_index > len(url_ids)-1:
            new_index = 0
    url_id = self.url_ids[new_index]
    url_id_site_leech_name = url_id.siteleech_id.name
    set_number_of_page_once_fetch = self.set_number_of_page_once_fetch
    
    end_page_number_in_once_fetch,page_lists, begin, so_page =  get_page_number_lists(self,url_id,url_id_site_leech_name,set_number_of_page_once_fetch,is_fetch_in_cron) 
    number_notice_dict = {
    'page_int':0,
    'curent_link':u'0/0',
    'link_number' : 0,
    'update_link_number' : 0,
    'create_link_number' : 0,
    'existing_link_number' : 0,
    'begin_page':begin,
    'so_page':so_page,
    'page_lists':page_lists,
    'length_link_per_curent_page':0
    }
    for page_int in page_lists:
        page_handle(self, page_int, url_id, number_notice_dict)
    self.last_fetched_url_id = url_id.id
        
    self.create_link_number=number_notice_dict['create_link_number']
    self.update_link_number =number_notice_dict["update_link_number"]
    self.link_number = number_notice_dict["link_number"]
    self.existing_link_number = number_notice_dict["existing_link_number"]
    url_id.write({'current_page':end_page_number_in_once_fetch,'web_last_page_number':self.web_last_page_number})
#     if url_id.siteleech_id.name ==  'batdongsan':
#         phuong_list = get_quan_list_in_big_page(self)
#         quan_list = get_quan_list_in_big_page(self,column_name='bds_bds.quan_id')
#         self.write({'phuong_ids':[(6,0,phuong_list)],'quan_ids':[(6,0,quan_list)]})#'quan_ids':[(6,0,quan_list)]
#         url_id.web_last_page_number= self.web_last_page_number
#         update_phuong_or_quan_for_url_id(self,quan_list,phuong_list,url_id)
#     else:
#         quan_list = get_quan_list_in_big_page(self,column_name='bds_bds.quan_id')
#         self.write({'quan_ids':[(6,0,quan_list)]})#'quan_ids':[(6,0,quan_list)]
    self.note = note
    return None
def get_page_number_lists(self,url_id,url_id_site_leech_name,set_number_of_page_once_fetch,is_fetch_in_cron):
    if url_id_site_leech_name ==  'batdongsan':
        last_page_from_website =  get_last_page_from_bdsvn_website(url_id.url)
        self.web_last_page_number = last_page_from_website
    elif url_id_site_leech_name=='chotot':
#         last_page_from_website =6000
        page_1_url = create_cho_tot_page_link(url_id.url, 1)
        html = request_html(page_1_url)
        html = json.loads(html)
        total = int(html["total"])
        last_page_from_website = int(math.ceil(total/20.0))
        self.web_last_page_number = last_page_from_website
    elif url_id_site_leech_name=='lazada':
        last_page_from_website =5
#     if is_fetch_in_cron:
#         set_page_end = False
#     else:
#         set_page_end  =self.set_page_end
#         
#     if not set_page_end:
#         end_page = last_page_from_website
#     else:
#         end_page = set_page_end if set_page_end <= last_page_from_website else last_page_from_website
    end_page = last_page_from_website
    begin = url_id.current_page + 1
    if begin > end_page:
        begin  = 1
    end = begin   + set_number_of_page_once_fetch - 1
    if end > end_page:
        end = end_page
    end_page_number_in_once_fetch = end
    page_lists = range(begin, end+1)
    so_page = end - begin + 1
    return end_page_number_in_once_fetch,page_lists, begin, so_page
def create_cho_tot_page_link(url_input,page_int):
    repl = 'o=%s'%(20*(page_int-1))
    url_input = re.sub('o=\d+',repl,url_input)
    url = url_input +  '&page=' +str(page_int)
    return url
def page_handle(self, page_int, url_id, number_notice_dict):
    number_notice_dict['page_int'] = page_int
    links_per_page = []
    url_input = url_id.url
    siteleech_id = url_id.siteleech_id
    if siteleech_id.name=='batdongsan':
        url = url_input + '/' + 'p' +str(page_int)
        html = request_html(url)
        soup = BeautifulSoup(html, 'html.parser')
        title_and_icons = soup.select('div.search-productItem')
        for title_and_icon in title_and_icons:
            topic_dict_of_page = {}
            title_soups = title_and_icon.select("div.p-title  a")
            topic_dict_of_page['list_id'] = title_soups[0]['href']
            icon_soup = title_and_icon.select('img.product-avatar-img')
            topic_dict_of_page['thumb'] = icon_soup[0]['src']
#         for a in title_soups:
#             l =a['href']
#             link = 'https://batdongsan.com.vn' + l
            links_per_page.append(topic_dict_of_page)
    elif siteleech_id.name =='chotot':
        url = create_cho_tot_page_link(url_input,page_int)
        html = request_html(url)
        html = json.loads(html)
        html = html['ads']
        links_per_page = html
#         for i in html:
#             url = 'https://gateway.chotot.com/v1/public/ad-listing/' + str(i['list_id'])
#             links_per_page.append(url)
    elif siteleech_id.name =='lazada':
        url = url_input +'?page=' +int(page_int)
    number_notice_dict['curent_page'] = page_int 
    number_notice_dict['length_link_per_previous_page']  = number_notice_dict.get('length_link_per_curent_page',0)
    number_notice_dict['length_link_per_curent_page'] = len(links_per_page)
    for link in links_per_page:
        topic_dict_of_page = {}
        if  siteleech_id.name =='chotot':
            topic_dict_of_page = link
            link  = 'https://gateway.chotot.com/v1/public/ad-listing/' + str(link['list_id'])
        elif 'batdongsan' in siteleech_id.name:
            topic_dict_of_page = link
            link  = 'https://batdongsan.com.vn' +  link['list_id']
        deal_a_link(self,link,number_notice_dict,url_id,topic_dict_of_page=topic_dict_of_page)
#         while (True):
#             try:
#                 deal_a_link(self,link,number_notice_dict,url_id,topic_dict_of_page=topic_dict_of_page)
#                 break
#             except Exception as e:
#                 raise ValueError(str(e))
#                 self.env['bds.error'].create({'code':str(e),'url':link})
#                 ##print 'url','sleep....because error'
#                 sleep(5)
def deal_a_link(self,link,number_notice_dict,url_id,topic_dict_of_page={}):
    
    search_dict = {}
    update_dict = {}
    search_dict['link'] = link
    ##print link
    #print '**link**',link
    html = request_html(link)
    siteleech_id = url_id.siteleech_id
    if siteleech_id.name =='batdongsan':
        pass
    elif siteleech_id.name =='chotot':
        html = json.loads(html)
    if siteleech_id.name =='batdongsan':    
        price = get_bds_dict_in_topic(self,update_dict,html,siteleech_id,only_return_price=True)
    elif siteleech_id.name =='chotot':
        price = get_chotot_topic_vals(self,update_dict,html,siteleech_id,only_return_price=True)
    search_link_existing= self.env['bds.bds'].search([('link','=',link)])
    if search_link_existing:
        number_notice_dict["existing_link_number"] = number_notice_dict["existing_link_number"] + 1
        if self.update_field_of_existing_recorder ==u'giá':
            search_link_and_price_existing= self.env['bds.bds'].search([('link','=',link),('gia','=',price)])
            if search_link_and_price_existing:
                update_dict.update({'url_ids':[(4,url_id.id)]})
            else:
                number_notice_dict['update_link_number'] = number_notice_dict['update_link_number'] + 1
                update_dict.update({'gia':price,'url_ids':[(4,url_id.id)]})
            search_link_existing.write(update_dict)
        elif self.update_field_of_existing_recorder ==u'all':
            if siteleech_id.name =='batdongsan':    
                get_bds_dict_in_topic(self,update_dict,html,siteleech_id)
                update_dict['thumb'] = topic_dict_of_page.get('thumb',False)
                #print "***topic_dict_of_page.get('thumb',False)***",topic_dict_of_page.get('thumb',False)
            elif siteleech_id.name =='chotot':
                get_chotot_topic_vals(self,update_dict,html,siteleech_id)
                update_dict['thumb'] = topic_dict_of_page.get('image',False)
            update_dict.update({'url_ids':[(4,url_id.id)]})
            search_link_existing.write(update_dict)
            number_notice_dict['update_link_number'] = number_notice_dict['update_link_number'] + 1
        else:
            pass
    else:
        if siteleech_id.name =='batdongsan':    
            get_bds_dict_in_topic(self,update_dict,html,siteleech_id)
            update_dict['thumb'] = topic_dict_of_page.get('thumb',False)
        elif siteleech_id.name  =='chotot':
            get_chotot_topic_vals(self,update_dict,html,siteleech_id)
            update_dict['thumb'] = topic_dict_of_page.get('image',False)
        update_dict['link'] = link
        update_dict.update({'url_ids':[(4,url_id.id)]})
        print ('**update_dict**',update_dict)
        self.env['bds.bds'].create(update_dict)
        number_notice_dict['create_link_number'] = number_notice_dict['create_link_number'] + 1    
#     update_dict.update({'url_ids':[(4,self.id)]})
    link_number = number_notice_dict.get("link_number",0) + 1
    number_notice_dict["link_number"] = link_number
    number_notice_dict["curent_link"] = u'%s/%s'%(link_number,number_notice_dict['length_link_per_curent_page']*number_notice_dict['so_page'])
    #print '***number_notice_dict***',number_notice_dict
###get data one topic of bds site
def get_images_for_bds_com_vn(soup):
    rs = soup.select('meta[property="og:image"]')
    images =  list(map(lambda i:i['content'],rs))
    return images
def get_bds_dict_in_topic(self,update_dict,html,siteleech_id,only_return_price=False):
    def create_or_get_one_in_m2m_value(val):
            val = val.strip()
            if val:
                return g_or_c_ss(self,'bds.images',{'url':val})
    update_dict['data'] = html
    
    soup = BeautifulSoup(html, 'html.parser')
    try:
        gia = get_price(soup)
    except:
        gia =0
    update_dict['gia'] = gia
    if  only_return_price:
        return gia
    
    update_dict['ngay_dang'] = get_ngay_dang(soup)
    update_dict['html'] = get_product_detail(soup)
    update_dict['siteleech_id'] = siteleech_id.id
    images = get_images_for_bds_com_vn(soup)
    if images:
        update_dict['present_image_link'] = images[0]  
        object_m2m_list = list(map(create_or_get_one_in_m2m_value, images))
        m2m_ids = list(map(lambda x:x.id, object_m2m_list))
        ##print '**m2m_ids**',m2m_ids
        if m2m_ids:
            val = [(6, False, m2m_ids)]
            update_dict['images_ids'] = val
    try:
        update_dict['area'] = get_dientich(soup)
    except:
        pass
    quan_id= g_or_c_bds_quan(self,soup)
    update_dict['quan_id'] = quan_id
    update_dict['phuong_id'] = get_phuong_xa_from_topic(self,soup,quan_id)
    #get_all_phuong_xa_of_quan_from_topic(self,soup,quan_id)
    title = soup.select('div.pm-title > h1')[0].contents[0]
    update_dict['title']=title
    ###print 'title',title
    mobile,name = get_mobile_name_for_batdongsan(soup)
    user = get_or_create_user_cho_tot_batdongsan(self,mobile,name,siteleech_id.name)
    update_dict['user_name_poster']=name
    update_dict['phone_poster']=mobile
    update_dict['poster_id'] = user.id    
def g_or_c_bds_quan(self,soup):
    sl = soup.select('div#divDistrictOptions li.current')   
    if sl:
        quan_name =  sl[0].get_text()
        name_without_quan_huyen = quan_name.replace(u'Quận ','').replace(u'Huyện','')
        quan_unidecode = unidecode(quan_name).lower().replace(' ','-')
        quan = g_or_c_ss(self,'bds.quan', {'name_without_quan':name_without_quan_huyen}, {'name':quan_name,'name_unidecode':quan_unidecode}, False)
        return quan.id
    else:
        return False
def g_or_c_chotot_quan(self,quan_name):
    name_without_quan_huyen = quan_name.replace(u'Quận ','').replace(u'Huyện','')
    quan_unidecode = unidecode(quan_name).lower().replace(' ','-')
    quan = g_or_c_ss(self,'bds.quan', {'name_without_quan':name_without_quan_huyen}, {'name':quan_name,'name_unidecode':quan_unidecode}, False)
    return quan.id
#     rs = self.env['bds.quan'].search([('name_without_quan','=',name_without_quan_huyen)])
#     if not rs:
#         name_unidecode  = unidecode(quan).lower().replace(' ','-')
#         rs = self.env['bds.quan'].create({'name':quan,'name_unidecode':name_unidecode,'name_without_quan':name_without_quan_huyen})
#     return rs     
def get_mobile_name_for_batdongsan(soup):
    mobile = get_mobile_user(soup)
    try:
        name = get_name_user(soup)
    except:
        name = 'no name bds'
    return mobile,name
def get_or_create_user_cho_tot_batdongsan(self,mobile,name,type_site):
    search_dict = {}
    update_dict = {}
    search_dict['phone'] = mobile
    search_dict['login'] = str(mobile)+'@gmail.com'
    search_dict['name'] = mobile
#     update_dict['ghi_chu'] = 'created by %s'%type_site
    user =  self.env['bds.poster'].search([('phone','=',mobile)])
    site_id = g_or_c_ss(self,'bds.siteleech', {'name':type_site}, {}, False)
    if user:
        posternamelines_id = g_or_c_ss(self,'bds.posternamelines',
                                               {'username_in_site':name,'site_id':site_id.id,'poster_id':user.id}, {}, False)
    else:
        search_dict.update({'ghi_chu':'created by %s'%type_site})
        user =  self.env['bds.poster'].create(search_dict)
        self.env['bds.posternamelines'].create( {'username_in_site':name,'site_id':site_id.id,'poster_id':user.id})
    return user 
# lặt vặt khi get topic của bds
def get_price(soup):
    kqs = soup.find_all("span", class_="gia-title")
    gia = kqs[0].find_all("strong")
    gia = gia[0].get_text()
    if u'tỷ' in gia:
        int_gia = gia.replace(u'tỷ','').rstrip()
        int_gia = float(int_gia)
    return int_gia
def get_dientich(soup):
    kqs = soup.find_all("span", class_="gia-title")
    gia = kqs[1].find_all("strong")
    gia = gia[0].get_text()
    rs = re.search(r"(\d+)", gia)
    gia = rs.group(1)
    int_gia = float(gia)
    return int_gia
def get_mobile_user(soup,id_select = 'div#LeftMainContent__productDetail_contactMobile'):
    select = soup.select(id_select)[0]
    mobile =  select.contents[3].contents[0]
    mobile =  mobile.strip()
    if not mobile:
        raise ValueError('sao khong co phone')
    return mobile
def get_name_user(soup):
    name = get_mobile_user(soup,id_select = 'div#LeftMainContent__productDetail_contactName')
    return name

def get_chotot_topic_vals(self,update_dict,html_big,siteleech_id,only_return_price=False):
    def create_or_get_one_in_m2m_value(val):
            val = val.strip()
            if val:
                return g_or_c_ss(self,'bds.images',{'url':val})
            
    html=html_big['ad']
    try:
        price = float(html['price'])/1000000000
        
    except KeyError:
        price = 0
    date = html['date']
    date_obj = get_date_cho_tot(date)
    update_dict['ngay_dang']=date_obj
    update_dict['siteleech_id'] = siteleech_id.id
    
    if only_return_price:
        return price
    images = html.get('images',[])
    if images:
        update_dict['present_image_link'] = images[0]  
        object_m2m_list = list(map(create_or_get_one_in_m2m_value, images))
        m2m_ids = list(map(lambda x:x.id, object_m2m_list))
        ##print '**m2m_ids**',m2m_ids
        if m2m_ids:
            val = [(6, False, m2m_ids)]
            update_dict['images_ids'] = val
    try:
        address = html['address']
        update_dict['address'] = address
    except KeyError:
        pass
    
    try:
        quan = html_big['ad_params']['area']['value']
        update_dict['parameters'] = quan
        
        rs = g_or_c_chotot_quan(self,quan)
        update_dict['quan_id'] = rs
    except KeyError:
        pass
    
    
    update_dict['gia'] = price
    
    mobile,name = get_mobile_name_cho_tot(html)
    user = get_or_create_user_cho_tot_batdongsan(self,mobile,name ,siteleech_id.name)
    update_dict['user_name_poster']=name
    update_dict['phone_poster']=mobile
    update_dict['poster_id'] = user.id
    try:
        update_dict['html'] = html['body']
    except KeyError:
        pass
    
    update_dict['area']=html.get('size',0)
    update_dict['title']=html['subject']




def g_or_c_ss(self,class_name,search_dict,
                                create_write_dict ={},is_must_update=False,noti_dict=None,
                                not_active_include_search = False,model_effect_noti_dict=False,create_or_write_info = False):
    if not_active_include_search:
        domain_not_active = ['|',('active','=',True),('active','=',False)]
    else:
        domain_not_active = []
    domain = []
    if noti_dict =={}:
        noti_dict['create'] = 0
        noti_dict['update'] = 0
        noti_dict['skipupdate'] = 0
    for i in search_dict:
        tuple_in = (i,'=',search_dict[i])
        domain.append(tuple_in)
    domain = expression.AND([domain_not_active, domain])
    searched_object  = self.env[class_name].search(domain)
    if not searched_object:
        search_dict.update(create_write_dict)
        created_object = self.env[class_name].create(search_dict)
        if noti_dict !=None and ( model_effect_noti_dict==False or model_effect_noti_dict==class_name):
            noti_dict['create'] = noti_dict['create'] + 1
        create_or_write = 'create'
        return_obj =  created_object
    else:
        if not is_must_update:
            is_write = False
            for attr in create_write_dict:
                domain_val = create_write_dict[attr]
                exit_val = getattr(searched_object,attr)
                try:
                    exit_val = getattr(exit_val,'id',exit_val)
                    if exit_val ==None: #recorderset.id ==None when recorder sset = ()
                        exit_val=False
                except:#singelton
                    pass
                if isinstance(domain_val, datetime.date):
                    exit_val = fields.Date.from_string(exit_val)
                if exit_val !=domain_val:
                    is_write = True
                    break
            
        else:
            is_write = True
        if is_write:
            create_or_write = 'write'
            searched_object.sudo().write(create_write_dict)
            if noti_dict !=None and ( model_effect_noti_dict==False or model_effect_noti_dict==class_name):
                noti_dict['update'] = noti_dict['update'] + 1

        else:#'update'
            create_or_write = 'skip write'
            if noti_dict !=None and ( model_effect_noti_dict==False or model_effect_noti_dict==class_name):
                noti_dict['skipupdate'] = noti_dict['skipupdate'] + 1
        return_obj = searched_object
    if create_or_write_info:
        return return_obj,create_or_write
    return return_obj

def get_ngay_dang(soup):
    select = soup.select('div.prd-more-info > div:nth-of-type(3)')#[0].contents[0]
    ngay_dang_str = select[0].contents[2]
    ngay_dang_str = ngay_dang_str.replace('\r','').replace('\n','')
    ngay_dang_str = re.sub('\s*', '', ngay_dang_str)
    ngay_dang = datetime.datetime.strptime(ngay_dang_str,"%d-%m-%Y")
    return ngay_dang
def get_product_detail(soup):
#     select = soup.select('div#product-detail')[0]
    select = soup.select('div.pm-desc')[0]
    return select
def get_quan_list_in_big_page(self,column_name='bds_bds.phuong_id'):
    product_category_query = '''select  count(%s), %s from fetch_bds_relate inner join bds_bds on fetch_bds_relate.bds_id = bds_bds.id where fetch_id = %s group by %s'''%(column_name,column_name,self.id,column_name)
    self.env.cr.execute(product_category_query)
    product_category = self.env.cr.fetchall()
    phuong_list = reduce(lambda y,x:([x[1]]+y) if x[1]!=None else y,product_category,[] )
    return phuong_list
def update_phuong_or_quan_for_url_id(self,quan_list=[],phuong_list=[],url_id=None):
    if len(phuong_list) == 1:
        url_id.phuong_id = phuong_list[0]
        url_id.quan_id = False
    elif len(quan_list) ==1:
        url_id.quan_id = quan_list[0]
        url_id.phuong_id =False



def get_mobile_name_cho_tot(html):
    mobile = html['phone']
    name = html['account_name']
    return mobile,name

     
def local_a_native_time(datetime_input):
    local = pytz.timezone("Etc/GMT-7")
    local_dt = local.localize(datetime_input, is_dst=None)
    utc_dt = local_dt.astimezone (pytz.utc)
    return utc_dt#utc_dt
def get_date_cho_tot(string):  
    try:
        ##print 'ngay dang from cho tot',string
        if u'hôm nay' in string:
            new = string.replace(u'hôm nay',datetime.date.today().strftime('%d/%m/%Y'))
        elif u'hôm qua' in string:
            hom_qua_date = datetime.date.today() -  datetime.timedelta(days=1)
            new = string.replace(u'hôm qua',hom_qua_date.strftime('%d/%m/%Y'))
        else:
            new=string.replace(u'ngày ','').replace(u' tháng ','/').replace(' ','/2017 ')
        new_date =  datetime.datetime.strptime(new,'%d/%m/%Y %H:%M')     
        return local_a_native_time(new_date)
    except:
        return False


        
        


                 
def get_last_page_from_bdsvn_website(url_input):
    #print '***url_input**',url_input
    html = request_html(url_input)
    soup = BeautifulSoup(html, 'html.parser')
    range_pages = soup.select('div.background-pager-right-controls > a')
    if range_pages:
        last_page_href =  range_pages[-1]['href']
        #end_page = int(last_page_href[-1])
        kq= re.search('\d+$',last_page_href)
        last_page_from_website =  int(kq.group(0))
    else:
        last_page_from_website = 1
    return last_page_from_website



def get_link_on_one_page_laz(self,page_url):
    html = request_html(page_url)
    #print 'html a page',html
    self.html_lazada = html
    soup = BeautifulSoup(html, 'html.parser')
    links_per_page = []
    title_soups = soup.select("div.c-product-card__description  a")
    #print 'title_soups',title_soups
    for a in title_soups:
        ##print 'link hehe',a
        l =a['href']
        title = a.get_text().strip()
        ##print 'title',title
        links_per_page.append((l,title))
    
    return links_per_page
def send_mail(Subject,body):
    pass
#     body = unidecode(body)
#     Subject = unidecode(Subject)
#     fromaddr = 'nguyenductu@gmail.com'
#     toaddrs  = 'nguyenductu@gmail.com'
# #         msg = 'Why,Oh why fffffffffffform !'
#     
#     msg = MIMEMultipart()
#     msg['From'] = fromaddr
#     msg['To'] = toaddrs
#     msg['Subject'] =Subject# "SUBJECT OF THE MAIL"
#      
#     body = body#"YOUR MESSAGE HERE"
#     msg.attach(MIMEText(body, 'plain'))
#     text = msg.as_string()
# 
#     username = 'tunguyen19771@gmail.com'
#     password = 'Tu87cucgach'
#     server = smtplib.SMTP('smtp.gmail.com:587')
#     server.starttls()
#     server.login(username,password)
#     server.sendmail(fromaddr, toaddrs, text)
#     server.quit()
    ##print 'dont'

def detect_iphone_type(self,string):
    try:
        rs = re.search(r'iphone 8 plus|iphone 8|iphone X',string,re.I)
        name_cate =  rs.group(0)
        name_cate = name_cate.lower()
    except:
        name_cate = False
    try:
        rs = re.search(r'256|64',string,re.I)
        dung_luong =  rs.group(0)
    except:
        dung_luong = False
    
    try:
        rs = re.search(r'Chính Thức|Nhập Khẩu',string,re.I)
        nhap_khau_hay_chinh_thuc =  rs.group(0).lower()
    except:
        nhap_khau_hay_chinh_thuc = False
        
    ip_type = g_or_c_ss(self,'iphonetype', {'name_cate':name_cate,'dung_luong':dung_luong,'nhap_khau_hay_chinh_thuc':nhap_khau_hay_chinh_thuc})
    return ip_type

def check_bien_dong(find_last_item,compare_dict):
                list_bien_dong = []
                noi_dung_bien_dong_dict = {}
                for k,v in compare_dict.iteritems():
                    val_of_last_item = getattr(find_last_item, k)
                    if val_of_last_item != v:
                        list_bien_dong.append(k)
                        if k == 'gia':
                            delta = v - val_of_last_item
                            if delta > 0 :
                                tang_hay_giam_str = u'Tăng'
                            else:
                                tang_hay_giam_str = u'Giảm'
                            noi_dung_bien_dong_dict[k]= u'giá cũ:%s,giá mới%s,%s:%s'%(val_of_last_item,v,tang_hay_giam_str,abs(delta))
                        else:
                            noi_dung_bien_dong_dict[k]= u'%s--->%s'%(val_of_last_item,v)
                    else:
                        pass
                        ##print '**= nhau',k,val_of_last_item,val_of_last_item
                if list_bien_dong:
                    return (True,list_bien_dong,noi_dung_bien_dong_dict)
                else:
                    return (False,list_bien_dong,noi_dung_bien_dong_dict)
def trich_xuat_so_luong(so_luong):
    if u'hết' in so_luong:
        easy_so_luong = 0
    elif so_luong:
        rs =  re.search('\d+',so_luong)
        if rs:
            easy_so_luong = int(rs.group(0))
    else:
        easy_so_luong = -1
    return easy_so_luong
    
def fetch_lazada(self):
    #print 'lazada'
    page_url = self.lazada_url
#     html = request_html(page_url)
#     soup = BeautifulSoup(html, 'html.parser')
#     links_per_page = []
#     title_soups = soup.select("div.c-product-card__description  a")
#     for a in title_soups:
#         ##print 'link hehe',a
#         l =a['href']
#         links_per_page.append(l)

    links_per_page = get_link_on_one_page_laz(self,page_url)
    ##print 'links_per_page',links_per_page
    test_page = []
    noti_dict = {}
    count = 0 
    len_links_per_page = len(links_per_page)
    for thread_link,title in links_per_page:
#     for thread_link in links_per_page:
        count +=1
        #print 'fetch %s/%s'%(count,len_links_per_page)
        test_ones = []
        compare_dict = {}
        write_dict = {}
        link = 'https://www.lazada.vn' +  thread_link
        ##print '***thread_link**',link
        write_dict['title'] = title
        write_dict['link'] = link
        ##print '**tt**',title
        
        html = request_html(link)
        soup = BeautifulSoup(html, 'html.parser')
        gia = soup.select("span#special_price_box")[0].get_text()
        gia = gia.replace('.','')
        gia = float(gia)
        ##print 'gia',gia
        compare_dict['gia'] = gia
        write_dict['gia'] = gia
        test_ones.append(unicode(gia))
        so_luong = soup.select("span#product-option-stock-number")[0].get_text().strip()
        so_luong = trich_xuat_so_luong(so_luong)
        compare_dict['so_luong'] = so_luong
        write_dict['so_luong'] = so_luong
        duoc_ban_boi = soup.select(".basic-info__name")[0].get_text().strip()
        write_dict['duoc_ban_boi'] = duoc_ban_boi
        rs = re.search('(\d+)\.html',link)
        topic_id = rs.group(1)
        write_dict['topic_id'] = topic_id
        ipt_id = detect_iphone_type(self,title)
        original_item = self.env['dienthoai'].search([('topic_id','ilike',topic_id)],order = "create_date asc",limit=1)
        is_bien_dong = False
        if original_item:
            original_item = original_item[0]
            find_last_item = self.env['dienthoai'].search([('topic_id','ilike',topic_id)],order = "create_date desc",limit=1)[0]
            is_bien_dong,list_bien_dong,noi_dung_bien_dong_dict = check_bien_dong(find_last_item,compare_dict)
        if not original_item or  (original_item and  is_bien_dong) :
            object = self.env['dienthoai'].create(write_dict)
#             mail_body = u'link: %s \n gia: %s so luong: %s'%(link,gia,unidecode(so_luong))
#             send_mail(mail_body,mail_body)
            object.iphonetype_id = ipt_id
            if not original_item:
                mail_body = u'Create sp:%s, gia %s, so luong: %s, link: %s \n: '% (object.iphonetype_id.name,gia,so_luong,link)
                send_mail(mail_body,mail_body)
            if  original_item and  is_bien_dong:
#                     if 'gia' in list_bien_dong:
#                         mail_body = u' so luong: %s link: %s \n gia %s: '%(gia,unidecode(so_luong),link)
#                         send_mail(mail_body,mail_body)
                    object.write({'original_itself_id':original_item.id,'is_bien_dong_item':True,'noi_dung_bien_dong':noi_dung_bien_dong_dict})
                    original_item.gia_hien_thoi = gia
                    original_item.noi_dung_bien_dong = noi_dung_bien_dong_dict
                    if 'so_luong' in list_bien_dong:
                        original_item.so_luong_hien_thoi = so_luong
                    mail_body = u'%s,link%s'%(noi_dung_bien_dong_dict,link)
                    send_mail(mail_body,mail_body)

                        
        test_one =  u'|'.join(test_ones)
        test_page.append(test_one)
    self.html_lazada_thread_gia = u'\n'.join(test_page)
    self.test_lazada = noti_dict

    

    

    
    
    
    
    
    
quan_huyen_data = '''<ul class="advance-options" style="min-width: 218px;">
<li vl="0" class="advance-options current" style="min-width: 186px;">--Chọn Quận/Huyện--</li><li vl="72" class="advance-options" style="min-width: 186px;">Bình Chánh</li><li vl="65" class="advance-options" style="min-width: 186px;">Bình Tân</li><li vl="66" class="advance-options" style="min-width: 186px;">Bình Thạnh</li><li vl="73" class="advance-options" style="min-width: 186px;">Cần Giờ</li><li vl="74" class="advance-options" style="min-width: 186px;">Củ Chi</li><li vl="67" class="advance-options" style="min-width: 186px;">Gò Vấp</li><li vl="75" class="advance-options" style="min-width: 186px;">Hóc Môn</li><li vl="76" class="advance-options" style="min-width: 186px;">Nhà Bè</li><li vl="68" class="advance-options" style="min-width: 186px;">Phú Nhuận</li><li vl="53" class="advance-options" style="min-width: 186px;">Quận 1</li><li vl="62" class="advance-options" style="min-width: 186px;">Quận 10</li><li vl="63" class="advance-options" style="min-width: 186px;">Quận 11</li><li vl="64" class="advance-options" style="min-width: 186px;">Quận 12</li><li vl="54" class="advance-options" style="min-width: 186px;">Quận 2</li><li vl="55" class="advance-options" style="min-width: 186px;">Quận 3</li><li vl="56" class="advance-options" style="min-width: 186px;">Quận 4</li><li vl="57" class="advance-options" style="min-width: 186px;">Quận 5</li><li vl="58" class="advance-options" style="min-width: 186px;">Quận 6</li><li vl="59" class="advance-options" style="min-width: 186px;">Quận 7</li><li vl="60" class="advance-options" style="min-width: 186px;">Quận 8</li><li vl="61" class="advance-options" style="min-width: 186px;">Quận 9</li><li vl="69" class="advance-options" style="min-width: 186px;">Tân Bình</li><li vl="70" class="advance-options" style="min-width: 186px;">Tân Phú</li><li vl="71" class="advance-options" style="min-width: 186px;">Thủ Đức</li>
</ul>'''
def import_quan_data(self):
    soup = BeautifulSoup(quan_huyen_data, 'html.parser')
    lis =  soup.select('li')
    for li in lis:
        quan =  li.get_text()
        name_without_quan = quan.replace(u'Quận ','')
        quan_unidecode = unidecode(quan).lower().replace(' ','-')
        g_or_c_ss(self,'bds.quan', {'name':quan}, {'name_unidecode':quan_unidecode,'name_without_quan':name_without_quan}, True)
    return len(lis)
def request_and_write_to_disk(url):
    url = 'https://batdongsan.com.vn/ban-nha-rieng-duong-cao-thang-phuong-11-5/ket-tien-gap-hem-p-q-10-ngay-goc-dien-bien-phu-pr13372162'
    my_html = request_html(url)
    file = open('E:\mydata\python_data\my_html.html','w')
    file.write(my_html)
    file.close()
def get_soup_from_file():
    file = open('E:\mydata\python_data\my_html.html','r')
    my_html = file.read()
    soup = BeautifulSoup(my_html, 'html.parser')
    return soup
def get_phuong_xa_from_topic(self,soup,quan_id):
    sl = soup.select('div#divWard li.current')   
    if sl:
        phuong_name =  sl[0].get_text()
        phuong = g_or_c_ss(self,'bds.phuong', {'name_phuong':phuong_name,'quan_id':quan_id}, {'quan_id':quan_id}, False)
        return phuong.id
    else:
        return False
def get_all_phuong_xa_of_quan_from_topic(self,soup,quan_id):
    sls = soup.select('div#divWard li')   
    if sls:
        for sl in sls:
            phuong_name =  sl.get_text()
            if '--' in phuong_name:
                continue
            phuong = g_or_c_ss(self,'bds.phuong', {'name_phuong':phuong_name,'quan_id':quan_id}, {'quan_id':quan_id}, False)
    else:
        return False
    

def import_contact(self):
    recordlist = base64.decodestring(self.file)
    excel = xlrd.open_workbook(file_contents = recordlist)
    sheet = excel.sheet_by_index(0)
    full_name_index = 2
    phone_index = 4
    
    land_contact_saved_number = 0
    for row in range(2,sheet.nrows):
        full_name = sheet.cell_value(row,full_name_index)
        phone = sheet.cell_value(row,phone_index)
        phone = phone.replace('(Mobile)','').replace('(Home)','').replace('(Other)','').replace(' ','').replace('+84','0')
        ##print phone,full_name
        rs_mycontact  = self.env['bds.mycontact'].search([('phone','=',phone)])
        if rs_mycontact:
            if rs_mycontact.name != full_name:
                rs_mycontact.write({'name':full_name})
        else:
            rs_mycontact = self.env['bds.mycontact'].create({'name':full_name,'phone':phone})
        rs_user = self.env['bds.poster'].search([('phone','=',phone)])
        if rs_user:
            land_contact_saved_number +=1
            rs_user.write({'ten_luu_trong_danh_ba':full_name,'mycontact_id':rs_mycontact.id})
    self.land_contact_saved_number = land_contact_saved_number
            
        
if __name__== '__main__':
    url_input = 'https://nha.chotot.com/tp-ho-chi-minh/quan-10/mua-ban-nha-dat'
    url_input = 'https://nha.chotot.com/quan-10/mua-ban-nha-dat/nha-hxh-duong-ly-thuong-kiet-quan-10-38471382.htm'
    #url_input = 'https://gateway.chotot.com/v1/public/ad-listing/38471382'
    url_input = 'https://gateway.chotot.com/v1/public/ad-listing/38483113'
    html = request_html(url_input)
    ##print html

    
