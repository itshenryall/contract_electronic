# -*- coding: utf-8 -*-
from openerp import http

# class ContractE(http.Controller):
#     @http.route('/contract_e/contract_e/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/contract_e/contract_e/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('contract_e.listing', {
#             'root': '/contract_e/contract_e',
#             'objects': http.request.env['contract_e.contract_e'].search([]),
#         })

#     @http.route('/contract_e/contract_e/objects/<model("contract_e.contract_e"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('contract_e.object', {
#             'object': obj
#         })