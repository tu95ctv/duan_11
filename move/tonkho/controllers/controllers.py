# -*- coding: utf-8 -*-
from odoo import http

# class Tonkho(http.Controller):
#     @http.route('/tonkho/tonkho/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tonkho/tonkho/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tonkho.listing', {
#             'root': '/tonkho/tonkho',
#             'objects': http.request.env['tonkho.tonkho'].search([]),
#         })

#     @http.route('/tonkho/tonkho/objects/<model("tonkho.tonkho"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tonkho.object', {
#             'object': obj
#         })