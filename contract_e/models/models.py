# -*- coding: utf-8 -*-

from openerp import models, fields, api

# class contract_e(models.Model):
#     _name = 'contract_e.contract_e'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100

import openerp
from openerp import SUPERUSER_ID
from openerp import tools
from openerp.modules.module import get_module_resource
from openerp import models, fields, api, exceptions, _
from openerp.tools.translate import _
from datetime import timedelta
from datetime import date,datetime
from dateutil.relativedelta import relativedelta
from openerp.tools import openerp,image_colorize, image_resize_image_big
from openerp.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import UserError, ValidationError, Warning
import dateutil.parser
import openerp.addons.decimal_precision as dp
import base64
import urllib
import os
import re
import random 
from random import randint
import string
# import logging

                 ##########################
                ### USER ACCESS CONTRACT ###
                 ##########################
class res_users(models.Model):
    _inherit= 'res.users'
    _order = "xcontract_posisiton desc"

    xcontract_posisiton = fields.Selection([
            ('admin', 'Admin'),
            ('vp', 'VP'),
            ('gm', 'GM'),
            ('sales', 'Sales')
            ], string='Position', help="Choose position VP, GM, Delegation or Sales", required=True)
    xcontract_phone_number_one = fields.Char(string="Phone Number 1", size=15, readonly=False, required=True)
    xcontract_phone_number_two = fields.Char(string="Phone Number 2", size=15, readonly=False)    
    xcontract_address = fields.Text(string='Address',default='Telkomsel Smart Office, Jl. Gatot Subroto No.Kav. 52, RT.6/RW.1, Kuningan Bar., Mampang Prpt., Kota Jakarta Selatan, Daerah Khusus Ibukota Jakarta 12710')
    # GM
    xcontract_vp_id = fields.Many2one('res.users',string='VP', select=True, required=True)
    xcontract_vp_parent_id = fields.Many2one('res.users',string='Parent VP', select=True)
    xcontract_vp_child_ids = fields.One2many('res.users', 'xcontract_vp_parent_id',string='Child VP')
    # SALES
    xcontract_vp_sales_id = fields.Many2one('res.users',string='VP', select=True, required=True)
    xcontract_vp_sales_email = fields.Char(related='xcontract_vp_sales_id.email')
    xcontract_gm_sales_id = fields.Many2one('res.users',string='GM', select=True, required=True)
    xcontract_gm_sales_email = fields.Char(related='xcontract_gm_sales_id.email')
    xcontract_vp_sales_parent_id = fields.Many2one('res.users',string='Parent VP', select=True)
    xcontract_vp_sales_child_ids = fields.One2many('res.users', 'xcontract_vp_sales_parent_id',string='Child VP')
    xcontract_signature 

    image = openerp.fields.Binary("Photo", attachment=True,
        help="This field holds the image used as photo for the test, limited to 1024x1024px.")
    image_medium = openerp.fields.Binary("Medium-sized photo", attachment=True,
        help="Medium-sized photo of the test. It is automatically "\
             "resized as a 128x128px image, with aspect ratio preserved. "\
             "Use this field in form views or some kanban views.")
    image_small = openerp.fields.Binary("Small-sized photo", attachment=True,
        help="Small-sized photo of the test. It is automatically "\
             "resized as a 64x64px image, with aspect ratio preserved. "\
             "Use this field anywhere a small image is required.")

    def _get_default_image(self, cr, uid, context=None):
        image_path = get_module_resource('contrac', 'static/src/img', 'default_image.png')
        return tools.image_resize_image_big(open(image_path, 'rb').read().encode('base64'))

    defaults = {
        'active': 1,
        'image': _get_default_image,
        'color': 0,
    }

    @api.model
    def create(self, vals):
        tools.image_resize_images(vals)
        return super(res_users, self).create(vals)

    @api.multi
    def write(self, vals):
        tools.image_resize_images(vals)
        return super(res_users, self).write(vals)

    def onchange_xcontract_vp_id(self, cr, uid, ids, xcontract_vp_id, context=None):
        value = {'xcontract_vp_parent_id': False}
        if xcontract_vp_id:
            department = self.pool.get('res.users').browse(cr, uid, xcontract_vp_id)
            value['xcontract_vp_parent_id'] = department.xcontract_vp_id.id
        return {'value': value}


    def onchange_xcontract_vp_sales_id(self, cr, uid, ids, xcontract_vp_sales_id, context=None):
        value = {'xcontract_vp_sales_parent_id': False}
        if xcontract_vp_sales_id:
            department = self.pool.get('res.users').browse(cr, uid, xcontract_vp_sales_id)
            value['xcontract_vp_sales_parent_id'] = department.xcontract_vp_sales_id.id
        return {'value': value}

    @api.model
    def create(self, values):
        return super(res_users, self).create(values)

                 ###########################
                ### TELKOMSEL INFORMATION ###
                 ###########################
#USER Telkomsel
class telkomsel_delegation_user(models.Model):
    _name = "telkomsel.delegation.user"
    _rec_name = 'xuser_tseldelegation_name'

    #Public Information
    # contact
    xuser_tseldelegation_name = fields.Char(string="Full Name", required=True) 
    xuser_tseldelegation_email = fields.Char(string="Email", size=50)
    xuser_tseldelegation_phone = fields.Char(string="Phone Number 1", size=15, readonly=False)
    xuser_tseldelegation_phonee = fields.Char(string="Phone Number 2", size=15, readonly=False)
    # position
    xuser_tseldelegation_position = fields.Char(string='Position', required=True)
    xuser_tseldelegation_department_id = fields.Char(string='Department')
    color = fields.Integer(string='Color Index')
    # image: all image fields are base64 encoded and PIL-supported
    image = openerp.fields.Binary("Photo", attachment=True,
        help="This field holds the image used as photo for the test, limited to 1024x1024px.")
    image_medium = openerp.fields.Binary("Medium-sized photo", attachment=True,
        help="Medium-sized photo of the test. It is automatically "\
             "resized as a 128x128px image, with aspect ratio preserved. "\
             "Use this field in form views or some kanban views.")
    image_small = openerp.fields.Binary("Small-sized photo", attachment=True,
        help="Small-sized photo of the test. It is automatically "\
             "resized as a 64x64px image, with aspect ratio preserved. "\
             "Use this field anywhere a small image is required.")

    def _get_default_image(self, cr, uid, context=None):
        image_path = get_module_resource('econtract_hr', 'static/src/img', 'default_image.png')
        return tools.image_resize_image_big(open(image_path, 'rb').read().encode('base64'))

    defaults = {
        'active': 1,
        'image': _get_default_image,
        'color': 0,
    }

    @api.model
    def create(self, vals):
        tools.image_resize_images(vals)
        return super(telkomsel_delegation_user, self).create(vals)

    @api.multi
    def write(self, vals):
        tools.image_resize_images(vals)
        return super(telkomsel_delegation_user, self).write(vals)

#Alamat Telkomsel
class telkomsel_location(models.Model):
    _name = "telkomsel.location"
    _rec_name = 'xtseloc_name'
    _order = "xtseloc_name desc"

    xtseloc_name = fields.Char(string="Nama Perusahaan", default="Telkomsel", required=True) 
    xtseloc_alamat = fields.Text(string="Alamat",default='Telkomsel Smart Office, Jl. Gatot Subroto No.Kav. 52, RT.6/RW.1, Kuningan Bar., Mampang Prpt., Kota Jakarta Selatan, Daerah Khusus Ibukota Jakarta 12710', size=240, required=True) 
    xtseloc_lantai = fields.Char(string="lantai", required=True) 
    xtseloc_no_telp = fields.Char(string="No Telepon", size=15, required=True) 
    xtseloc_facsimile = fields.Char(string="Facsimile", size=30)
    xtseloc_attention = fields.Text(string="U.p./Attention", size=30)

    @api.model
    def create(self, vals):
        rec = super(telkomsel_location, self).create(vals)
        # ...        
        return rec

#Reference bank Telkomsel
class telkomsel_bank_account(models.Model):
    _name = "telkomsel.bank.account"
    _rec_name = 'xbank_tseldelegation_name'
    _order = "xbank_tseldelegation_name desc"

    xbank_tseldelegation_name = fields.Char(string="Nama Pemilik Rekening", default="Telkomsel", required=True) 
    xbank_tseldelegation_bank_name = fields.Char(string="Nama Bank", required=True) 
    xuser_tseldelegation_alamat_bank = fields.Text(string="Alamat Cabang Bank", size=240)
    xbank_tseldelegation_norek = fields.Char(string="No Rekening", size=30, required=True) 

    @api.model
    def create(self, vals):
        rec = super(telkomsel_bank_account, self).create(vals)
        # ...        
        return rec

                 ##########################
                ###   Company Delegation ###
                 ##########################

#Company
class merch_delegation_contract(models.Model):
    _name = 'merch.delegation.contract'
    _rec_name = 'xmerch_delegation_name'
    _order = "xmerch_delegation_name desc"

    xmerch_delegation_name = fields.Char(string="Nama Merchant", required=True) 
    xmerch_delegation_id = fields.Many2one('merch.delegation.contract',string='Parent Company', select=True)
    xmerch_delegation_child_ids = fields.One2many('merch.delegation.contract', 'xmerch_delegation_id',string='Child Company')
    xmerch_delegation_npwp = fields.Char(string="NPWP", required=True)
    xmerch_delegation_alamat = fields.Text(string="Alamat", required=True)
    xmerch_delegation_telp = fields.Char(string="No Telepon", size=15, readonly=False)
    xmerch_delegation_mobile = fields.Char(string="Mobile", size=15, readonly=False)
    xmerch_delegation_facsimile = fields.Char(string="Facsimile")
    xmerch_delegation_attention = fields.Text(string="U.p./Attention", size=30)  
    xmerch_delegation_web = fields.Char(string="Website")  
    xmerch_delegation_manager_id = fields.Many2one('merch.delegation.user',string='Manager', track_visibility='onchange')
    xmerch_delegation_desc = fields.Text(string='About Company')
    color = fields.Integer(string='Color Index')
    image = openerp.fields.Binary("Photo", attachment=True,
        help="This field holds the image used as photo for the test, limited to 1024x1024px.")
    image_medium = openerp.fields.Binary("Medium-sized photo", attachment=True,
        help="Medium-sized photo of the test. It is automatically "\
             "resized as a 128x128px image, with aspect ratio preserved. "\
             "Use this field in form views or some kanban views.")
    image_small = openerp.fields.Binary("Small-sized photo", attachment=True,
        help="Small-sized photo of the test. It is automatically "\
             "resized as a 64x64px image, with aspect ratio preserved. "\
             "Use this field anywhere a small image is required.")

    def _get_default_image(self, cr, uid, context=None):
        image_path = get_module_resource('econtract_hr', 'static/src/img', 'default_image.png')
        return tools.image_resize_image_big(open(image_path, 'rb').read().encode('base64'))

    defaults = {
        'active': 1,
        'image': _get_default_image,
        'color': 0,
    }

    @api.model
    def create(self, vals):
        tools.image_resize_images(vals)
        return super(merch_delegation_contract, self).create(vals)

    @api.multi
    def write(self, vals):
        tools.image_resize_images(vals)
        return super(merch_delegation_contract, self).write(vals)

# Delegation Merch
class merch_delegation_user(models.Model):
    _name = "merch.delegation.user"
    _rec_name = 'xuser_merchdelegation_name'
    _order = "xuser_merchdelegation_user_department_id desc"

    xuser_merchdelegation_name = fields.Char(string="Name", required=True) 
    xuser_merchdelegation_number = fields.Char(string="ID Number")
    xuser_merchdelegation_jabatan = fields.Char(string="Position", required=True)
    xuser_merchdelegation_email = fields.Char(string="Email", size=240, required=True)
    xuser_merchdelegation_phone = fields.Char(string="Phone Number 1", size=15, readonly=False)
    xuser_merchdelegation_phonee = fields.Char(string="Phone Number 2", size=15, readonly=False)
    xuser_merchdelegation_user_department_id = fields.Many2one('merch.delegation.contract',string='Company', select=True)
    xuser_merchdelegation_parent_id = fields.Many2one('merch.delegation.user',string='Company Delegation', select=True)
    xuser_merchdelegation_child_ids = fields.One2many('merch.delegation.user', 'xuser_merchdelegation_parent_id',string='Child Company Delegation')
    color = fields.Integer(string='Color Index')
    image = openerp.fields.Binary("Photo", attachment=True,
        help="This field holds the image used as photo for the test, limited to 1024x1024px.")
    image_medium = openerp.fields.Binary("Medium-sized photo", attachment=True,
        help="Medium-sized photo of the test. It is automatically "\
             "resized as a 128x128px image, with aspect ratio preserved. "\
             "Use this field in form views or some kanban views.")
    image_small = openerp.fields.Binary("Small-sized photo", attachment=True,
        help="Small-sized photo of the test. It is automatically "\
             "resized as a 64x64px image, with aspect ratio preserved. "\
             "Use this field anywhere a small image is required.")

    def _get_default_image(self, cr, uid, context=None):
        image_path = get_module_resource('econtract_hr', 'static/src/img', 'default_image.png')
        return tools.image_resize_image_big(open(image_path, 'rb').read().encode('base64'))

    defaults = {
        'active': 1,
        'image': _get_default_image,
        'color': 0,
    }

    @api.model
    def create(self, vals):
        tools.image_resize_images(vals)
        return super(merch_delegation_user, self).create(vals)

    @api.multi
    def write(self, vals):
        tools.image_resize_images(vals)
        return super(merch_delegation_user, self).write(vals)

    def onchange_xuser_merchdelegation_user_department_id(self, cr, uid, ids, xuser_merchdelegation_user_department_id, context=None):
        value = {'xuser_merchdelegation_parent_id': False}
        if xuser_merchdelegation_user_department_id:
            department = self.pool.get('merch.delegation.contract').browse(cr, uid, xuser_merchdelegation_user_department_id)
            value['xuser_merchdelegation_parent_id'] = department.xmerch_delegation_manager_id.id
        return {'value': value}


                 ##########################
                ######## RATE CARD #########
                 ##########################
#main ratecard
class rate_card_main(models.Model):
    _name = 'rate.card.main'
    _rec_name = 'xratecard_main_name'
    _order = "xratecard_main_name desc"

    xratecard_main_name = fields.Char(string="Rate Card Name", required=True)
    xratecard_main_parent_id = fields.Many2one('rate.card.main',string='Parent Rate Card', select=True)
    xratecard_main_child_ids = fields.One2many('rate.card.main', 'xratecard_main_parent_id',string='Child Rate Card')
    color = fields.Integer(string='Color Index')

    defaults = {
        'active': 1,
        'color': 0,
    }

    @api.model
    def create(self, vals):
        rec = super(rate_card_main, self).create(vals)
        # ...        
        return rec    

# Inventory Rate Card
class inventory_rate_card(models.Model):
    _name = 'inventory.rate.card'
    _rec_name = 'xinventoryrate_name'
    _order = "xinventoryrate_ratecard_id desc"

    xinventoryrate_ratecard_id = fields.Many2one('rate.card.main', string='Rate Card Name', select=True)
    xinventoryrate_name = fields.Char(string='Inventory Name', required=True)
    xinventoryrate_parent_id = fields.Many2one('inventory.rate.card',string='Parent Inventory', select=True, track_visibility='onchange')
    xinventoryrate_child_ids = fields.One2many('inventory.rate.card', 'xinventoryrate_parent_id',string='Child Inventory')
    color = fields.Integer(string='Color Index')

    defaults = {
        'active': 1,
        'color': 0,
    }

    def onchange_xinventoryrate_ratecard_id(self, cr, uid, ids, xinventoryrate_ratecard_id, context=None):
        value = {'xinventoryrate_parent_id': False}
        if xinventoryrate_ratecard_id:
            department = self.pool.get('rate.card.main').browse(cr, uid, xinventoryrate_ratecard_id)
        return {'value': value}
        value['xinventoryrate_parent_id'] = department.xinventoryrate_ratecard_id.id

    @api.model
    def create(self, vals):
        rec = super(inventory_rate_card, self).create(vals)
        # ...        
        return rec

#Detail Rate Card
class detail_rate_card(models.Model):
    _name = "detail.rate.card"
    _rec_name = 'xdetailratecard_name'
    _order = "xdetailratecard_ratecard_id desc"

    xdetailratecard_ratecard_id = fields.Many2one('rate.card.main',string='Rate Card', select=True)
    xdetailratecard_inventory_id = fields.Many2one('inventory.rate.card',string='Inventory', select=True)
    xdetailratecard_name = fields.Char(string="Detail Rate Card Name") 
    xdetailratecard_rate = fields.Integer(string="Price")
    xdetailratecard_remark = fields.Text(string="Remark", size=15, readonly=False)
    color = fields.Integer(string='Color Index')
    defaults = {
        'active': 1,
        'color': 0,
    }

    @api.model
    def create(self, vals):
        rec = super(detail_rate_card, self).create(vals)
        # ...        
        return rec


                 #############################
                ### Contract Administration ###
                 #############################

#Transaction
class transaction_econtract_telkomsel(models.Model):
    _name = "transaction.econtract.telkomsel"
    _rec_name = 'xtelkomsel_transaction_number'
    _order = "xtransaction_date desc"
    
    # Sales
    xtransaction_sales_id = fields.Many2one('res.users','Sales', default=lambda self: self.env.user)
    xtransaction_sales_name = fields.Char(related='xtransaction_sales_id.name')
    xtransaction_sales_phone = fields.Char(related='xtransaction_sales_id.xcontract_phone_number_one')
    xtransaction_sales_email = fields.Char(related='xtransaction_sales_id.email')
    # Email VP 
    xtransaction_vp_email = fields.Char(related='xtransaction_sales_id.xcontract_vp_sales_email')
    # Email GM
    xtransaction_gm_email = fields.Char(related='xtransaction_sales_id.xcontract_gm_sales_email')
    # Transaction
    xtransaction_date = fields.Date("Contract Date", default=datetime.today())
    xtransaction_date_begin = fields.Date("Start")
    xtransaction_end_date = fields.Date("End")
    state = fields.Selection([
            ('draft', 'Draft'),
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('final', 'Final')
            ], default='draft')
    sent = fields.Boolean(readonly=True, default=False, copy=False,
        help="It indicates that the invoice has been sent.")
    # Contract Number
    xtelkomsel_transaction_number = fields.Char(string='Transaction Number')    
    #telkomsel delegation
    xtransaction_tseldelegation_id = fields.Many2one('telkomsel.delegation.user',string='Telkomsel Delegation', track_visibility='onchange')
    xtransaction_tseldelegation_name = fields.Char(string="Name")
    xtransaction_tseldelegation_position = fields.Char(string="Position") 
    xtransaction_tseldelegation_phone = fields.Char(string="Phone Number", size=15, readonly=False)
    xtransaction_tseldelegation_email = fields.Char(string="Email", size=240)
    # GET Contract and Name Company
    xtransaction_contract_and_company = fields.Char(string='Combination', compute='_name_number_company_get')
    #Client name
    xtransaction_merchdelegation_id = fields.Many2one('merch.delegation.contract',string='Company', track_visibility='onchange')
    xtransaction_merchdelegation_name = fields.Char(string="Name")
    xtransaction_merchdelegation_alamat = fields.Text(string='Address')
    xtransaction_merchdelegation_npwp = fields.Char(string='NPWP')
    #Client delegation
    xtransaction_merchdelegation_user_id = fields.Many2one('merch.delegation.user',string='Client Delegation Name', track_visibility='onchange')
    xtransaction_merchdelegation_name_user = fields.Char(string="Name")
    xtransaction_merchdelegation_jabatan = fields.Char(string="Position", size=50)
    xtransaction_merchdelegation_email = fields.Char(string="Email", size=240)
    xtransaction_merchdelegation_phone = fields.Char(string="Phone Number", size=15, readonly=False)
    # DATA BANK
    xtransaction_tseldelegation_bank_id = fields.Many2one('telkomsel.bank.account',string='Telkomsel Account', track_visibility='onchange')
    xtransaction_tseldelegation_account_bank_name = fields.Char(string="Nama Pemilik Rekening") 
    xtransaction_tseldelegation_bank_name = fields.Char(string="Nama Bank") 
    xtransaction_tseldelegation_referencelink = fields.Text(string="Reference link", size=240)
    xtransaction_tseldelegation_alamat_bank = fields.Text(string="Alamat Cabang Bank", size=240)
    xtransaction_tseldelegation_norek = fields.Char(string="No Rekening", size=30)    
    # PIC Telkomsel
    xtransaction_delegationtsel_id = fields.Many2one('telkomsel.delegation.user',string='PIC Telkomsel', track_visibility='onchange')
    xtransaction_delegationtsel_id_name = fields.Char(string="Name")
    xtransaction_delegationtsel_id_phone = fields.Char(string="Phone Number", size=15, readonly=False)
    # PIC Merchant
    xtransaction_delegationmerch_id = fields.Many2one('merch.delegation.user',string='PIC Client', track_visibility='onchange')
    xtransaction_merchdelegation_name_user_hidden = fields.Char(string="Name")
    xtransaction_merchdelegation_email_hidden = fields.Char(string="Email", size=240)
    xtransaction_merchdelegation_phone_hidden = fields.Char(string="Phone Number", size=15)
    xtransaction_reject_contract = fields.Text(string="Detail Reject Contract", size=30)    
    # RATE CARD
    xtransaction_ratecard_main_id = fields.Many2one('rate.card.main',string='Rate Card Name', track_visibility='onchange')
    xtransaction_ratecard_main_name = fields.Char(string="Rate Card Name")
    # DATA TELKOMSEL
    xtransaction_tseldelegation_alamat_telkomsel_id = fields.Many2one('telkomsel.location',string='Alamat Telkomsel', track_visibility='onchange')
    xtransaction_tseldelegation_alamat_name = fields.Char(string="Nama Perusahaan") 
    xtransaction_tseldelegation_alamat = fields.Text(string="Alamat", size=240) 
    xtransaction_tseldelegation_lantai = fields.Char(string="lantai")
    xtransaction_tseldelegation_no_telp = fields.Char(string="No Telepon", size=15)
    xtransaction_tseldelegation_facsimile = fields.Char(string="Facsimile", size=30)
    xtransaction_tseldelegation_attention = fields.Text(string="U.p./Attention", size=30)
    xtransaction_tseldelegation_otp = fields.Char(string="Kode OTP", required=True, default='Click on OTP')
    xtransaction_tseldelegation_otp_confirmation = fields.Char(string="Kode OTP")
    xtransaction_tseldelegation_signature_telkomsel = fields.Binary(string="Signature Telkomsel")
    xtransaction_tseldelegation_signature_merchant = fields.Binary(string="Signature Merchant")
    xtransaction_status_contract = fields.Selection([
            ('tidak', 'Not Active'),
            ('aktif', 'Active')
            ],string="Contract State",default="aktif")
    company_id = fields.Many2one('res.company', string='Company', change_default=True,
        required=True, readonly=True, default=lambda self: self.env['res.company']._company_default_get('transaction.econtract.telkomsel'))
    user_id = fields.Many2one('res.users', string='Salesperson', track_visibility='onchange',
        readonly=True, default=lambda self: self.env.user)
    color = fields.Integer(string='Color Index')

    defaults = {
        'color': 0,
        'xtransaction_sales_id':lambda self, cr, uid, ctx=None: uid
    }

    @api.model
    def create(self, vals):
        rec = super(transaction_econtract_telkomsel, self).create(vals)
        # ...        
        return rec

    def onchange_xtransaction_ratecard_main_id(self, cr, uid, ids, service, context=None):
        if service:
            service = self.pool.get('rate.card.main').browse(cr, uid, service, context=context)
            return {'value': {'xtransaction_ratecard_main_name': service.xratecard_main_name}}
        return {'value': {}}

    def onchange_xtransaction_tseldelegation_id(self, cr, uid, ids, service, context=None):
        if service:
            service = self.pool.get('telkomsel.delegation.user').browse(cr, uid, service, context=context)
            return {'value': {'xtransaction_tseldelegation_name': service.xuser_tseldelegation_name,'xtransaction_tseldelegation_position': service.xuser_tseldelegation_position,'xtransaction_tseldelegation_phone': service.xuser_tseldelegation_phone,'xtransaction_tseldelegation_email': service.xuser_tseldelegation_email}}
        return {'value': {}}

    def onchange_xtransaction_merchdelegation_id(self, cr, uid, ids, service, context=None):
        if service:
            service = self.pool.get('merch.delegation.contract').browse(cr, uid, service, context=context)
            return {'value': {'xtransaction_merchdelegation_name': service.xmerch_delegation_name, 'xtransaction_merchdelegation_alamat': service.xmerch_delegation_alamat, 'xtransaction_merchdelegation_npwp': service.xmerch_delegation_npwp}}
        return {'value': {}}

    def onchange_xtransaction_merchdelegation_user_id(self, cr, uid, ids, service, context=None):
        if service:
            service = self.pool.get('merch.delegation.user').browse(cr, uid, service, context=context)
            return {'value': {'xtransaction_merchdelegation_name_user': service.xuser_merchdelegation_name, 'xtransaction_merchdelegation_jabatan': service.xuser_merchdelegation_jabatan, 'xtransaction_merchdelegation_email': service.xuser_merchdelegation_email, 'xtransaction_merchdelegation_phone': service.xuser_merchdelegation_phone}}
        return {'value': {}}

  
    def onchange_xtransaction_tseldelegation_bank_id(self, cr, uid, ids, service, context=None):
        if service:
            service = self.pool.get('telkomsel.bank.account').browse(cr, uid, service, context=context)
            return {'value': {'xtransaction_tseldelegation_account_bank_name': service.xbank_tseldelegation_name,'xtransaction_tseldelegation_bank_name': service.xbank_tseldelegation_bank_name,'xtransaction_tseldelegation_referencelink': service.xuser_tseldelegation_referencelink,'xtransaction_tseldelegation_alamat_bank': service.xuser_tseldelegation_alamat_bank,'xtransaction_tseldelegation_norek': service.xbank_tseldelegation_norek}}
        return {'value': {}}

    def onchange_xtransaction_delegationtsel_id(self, cr, uid, ids, service, context=None):
        if service:
            service = self.pool.get('telkomsel.delegation.user').browse(cr, uid, service, context=context)
            return {'value': {'xtransaction_delegationtsel_id_name': service.xuser_tseldelegation_name,'xtransaction_delegationtsel_id_phone': service.xuser_tseldelegation_phone}}
        return {'value': {}}

    def onchange_xtransaction_delegationmerch_id(self, cr, uid, ids, service, context=None):
        if service:
            service = self.pool.get('merch.delegation.user').browse(cr, uid, service, context=context)
            return {'value': {'xtransaction_merchdelegation_name_user_hidden': service.xuser_merchdelegation_name,'xtransaction_merchdelegation_email_hidden': service.xuser_merchdelegation_email,'xtransaction_merchdelegation_phone_hidden': service.xuser_merchdelegation_phone}}
        return {'value': {}}

    def onchange_xtransaction_tseldelegation_alamat_telkomsel_id(self, cr, uid, ids, service, context=None):
        if service:
            service = self.pool.get('telkomsel.location').browse(cr, uid, service, context=context)
            return {'value': {'xtransaction_tseldelegation_alamat_name': service.xtseloc_name,'xtransaction_tseldelegation_alamat': service.xtseloc_alamat,'xtransaction_tseldelegation_lantai': service.xtseloc_lantai,'xtransaction_tseldelegation_no_telp': service.xtseloc_no_telp,'xtransaction_tseldelegation_facsimile': service.xtseloc_facsimile,'xtransaction_tseldelegation_attention': service.xtseloc_attention}}
        return {'value': {}}
        
    # @api.model
    # def create(self, vals):
    #     x = self.env['ir.sequence'].next_by_code('transaction.econtract.telkomsel') or '/'
    #     vals['xtelkomsel_transaction_number'] = x
    #     return super(transaction_econtract_telkomsel, self).create(vals)

    @api.multi
    def pending_contract(self):
        # if self.xtransaction_tseldelegation_email == False :
        #    raise ValidationError('The delegation email must be inserted before!')
        # if self.xtransaction_merchdelegation_email == False :
        #    raise ValidationError('The merchant email must be inserted before!')
        self.ensure_one()
        self.state ='pending'
        # template = self.env.ref('contract_e.new_contract_mail_template', False)
        # mail = self.env['mail.template'].browse(template.id)
        # mail.send_mail(self.id, force_send=True)
 
    @api.multi
    def approved_contract_merchant(self):
        # self.write({'xtransaction_tseldelegation_otp': ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(randint(9,15)))})
        self.ensure_one()
        self.state ='approved'
        # template = self.env.ref('contract_e.approve_contract_merchant_mail_template', False)
        # mail = self.env['mail.template'].browse(template.id)
        # mail.send_mail(self.id, force_send=True)
        # self.ensure_one()
        # template = self.env.ref('contract_e.approve_contract_sales_mail_template', False)
        # mail = self.env['mail.template'].browse(template.id)
        # mail.send_mail(self.id, force_send=True)


    @api.multi
    def rejected_contract(self):
        # if self.xtransaction_reject_contract == False :
        #    raise ValidationError('The comment rejected contract must be inserted before!')
        self.ensure_one()
        self.state ='rejected'
        # template = self.env.ref('contract_e.reject_contract_sales_mail_template', False)
        # mail = self.env['mail.template'].browse(template.id)
        # mail.send_mail(self.id, force_send=True)

    @api.multi
    def final_contract(self):
        # if self.xtransaction_tseldelegation_otp_confirmation != self.xtransaction_tseldelegation_otp :
        #    raise ValidationError('The OTP Must Inserted before!')
        self.ensure_one()
        self.state ='final'
        # template = self.env.ref('contract_e.final_contract_sales_mail_template', False)
        # mail = self.env['mail.template'].browse(template.id)
        # mail.send_mail(self.id, force_send=True)
   
    @api.multi
    def clear_record_data(self):
        self.write({
            'xtransaction_tseldelegation_otp': ''
        })

    @api.constrains('xtransaction_tseldelegation_otp_confirmation')
    def validate_otpxx(self):
            if self.xtransaction_tseldelegation_otp_confirmation != self.xtransaction_tseldelegation_otp :
                raise ValidationError('The OTP Is Not valid!')


                 ##########################
                ######## QUOTATION #########
                 ##########################
# Quotation
class quotation_transaction_telkomsel(models.Model):
    _name = "quotation.transaction.telkomsel"
    _rec_name = 'xquotationtrans_number_quotation'
    _order = "xquotationtrans_date desc"

    @api.multi
    @api.depends('xquotationtrans_list_rate_card_ids')
    def _get_total(self):
        for transaction in self:
            transaction.xquotationtrans_total_harga = sum(
                quotation.xquotationtrans_total for quotation in transaction.xquotationtrans_list_rate_card_ids)

    state = fields.Selection([
            ('draft', 'Draft'),
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('final', 'Final')
            ], default='draft')
    sent = fields.Boolean(readonly=True, default=False, copy=False,
        help="It indicates that the invoice has been sent.")
    xquotationtrans_date = fields.Date("Quotation Date", default=datetime.today())
    xquotationtrans_usage_order = fields.Selection([('usage', 'Usage'), ('order', 'Order')], string="Penagihan", default='usage')
    xquotationtrans_number_contract_id = fields.Many2one('transaction.econtract.telkomsel',string='Contract Number', track_visibility='onchange', select=True)
    xquotationtrans_number_quotation = fields.Char(string='quotation number')
    # SALES
    xquotationtrans_sales_contract_id = fields.Char(string='Sales Name')
    xquotationtrans_sales_phone = fields.Char(string='Sales Phone')
    xquotationtrans_sales_email = fields.Char(string='Sales Email')
    # EMAIL VP AND GM
    xquotationtrans_vp_email = fields.Char(string='VP')
    xquotationtrans_gm_email = fields.Char(string='GM')
    # Company
    xquotationtrans_company_npwp = fields.Char(string='NPWP')
    xquotationtrans_company_contract_id = fields.Char(string='Company')
    xquotationtrans_company_alamat = fields.Text(string='Address')
    # Client Delegation
    xquotationtrans_client_delegation_contract_id = fields.Char(string='Client Delegation')
    xquotationtrans_client_delegation_jabatan = fields.Char(string="Position", size=50)
    xquotationtrans_client_delegation_email = fields.Char(string="Email", size=240)
    xquotationtrans_client_delegation_phone = fields.Char(string="Phone Number", size=15, readonly=False)
    xquotationtrans_company_product = fields.Char(string='Product / Brand')
    xquotationtrans_company_brand_category = fields.Char(string='Brand Category')
    xquotationtrans_company_name = fields.Char(string='Campaign Name')
    # ATTENTION Company
    xquotationtrans_merchdelegation_name = fields.Char(string="PIC")
    xquotationtrans_merchdelegation_email = fields.Char(string="Email")
    xquotationtrans_merchdelegation_phone = fields.Char(string="No HP")
    xquotationtrans_invoices_address = fields.Text(string="Invoice Address")
    # PIC Telkomsel
    xquotationtrans_pic_telkomsel = fields.Char(string='Proposed By (PIC Telkomsel)')
    xquotationtrans_pic_telkomsel_phone = fields.Char(string="Contact Number")
    #RATE CARD
    xquotationtrans_list_rate_card_ids = fields.One2many(
        'quotation.total.price', 'xtotalquotation_trans_id', string="List Rate Card")
    xquotationtrans_discount   = fields.Float(string='Discount Sales')
    xquotationtrans_total_harga = fields.Float(string='Total Gross', store=True, readonly=True, compute='_get_total', track_visibility='always')
    xquotationtrans_total_hargax =  fields.Float(string='Total')
    xquotationtrans_total_harga_final =  fields.Float(string='Total')
    xquotationtrans_discount_ppnx = fields.Float(string='Ppn')
    hargappn = fields.Float(string='ppn 10%')
    xquotationtrans_total_bayar = fields.Float(compute='_get_total_bayar', string='Total Bayar') #di hidden#
    xquotationtrans_total_bayar_fix = fields.Float(compute='_get_total_bayar_fix', string='Total Bayar(inc. PPN 10%)') #show
    xquotationtrans_parent_id = fields.Many2one('quotation.transaction.telkomsel',string='Parent Quotation', select=True, track_visibility='onchange')
    xquotationtrans_child_ids = fields.One2many('quotation.transaction.telkomsel', 'xquotationtrans_parent_id',string='Child Quotation')
    company_id = fields.Many2one('res.company', string='Company', change_default=True,
        required=True, readonly=True, default=lambda self: self.env['res.company']._company_default_get('transaction.econtract.telkomsel'))
    user_id = fields.Many2one('res.users', string='Salesperson', track_visibility='onchange',
        readonly=True, default=lambda self: self.env.user)
    xquotationtrans_tseldelegation_otp = fields.Char(string="Kode OTP", required=True, default='Click on OTP')
    xquotationtrans_tseldelegation_otp_confirmation = fields.Char(string="Kode OTP")
    xquotationtrans_reject = fields.Text(string="Detail Reject Quotation", size=30)    
    xquotationtrans_status_order = fields.Selection([
            ('tidak', 'Not Active'),
            ('aktif', 'Active')
            ],string="Quotation State",default="aktif")
    xquotationtrans_tseldelegation_signature_telkomsel = fields.Binary(string="Signature Telkomsel Delegation")
    xquotationtrans_tseldelegation_signature_merchant = fields.Binary(string="Signature Merchant")
    @api.model
    def create(self, vals):
        rec = super(quotation_transaction_telkomsel, self).create(vals)
        # ...        
        return rec

    @api.multi
    @api.depends('xquotationtrans_total_hargax')
    def _get_total_bayar(self):
        for quotation in self:
            quotation.xquotationtrans_total_bayar = (quotation.xquotationtrans_total_hargax * 10) /100

    @api.multi
    @api.depends('xquotationtrans_total_hargax', 'xquotationtrans_total_bayar_fix', 'xquotationtrans_total_bayar')
    def _get_total_bayar_fix(self):
        for quotation in self:
            quotation.xquotationtrans_total_bayar_fix = quotation.xquotationtrans_total_hargax + quotation.xquotationtrans_total_bayar
    
    def onchange_xquotationtrans_number_contract_id(self, cr, uid, ids, service, context=None):
        if service:
            service = self.pool.get('transaction.econtract.telkomsel').browse(cr, uid, service, context=context)
            return {'value': {'xquotationtrans_sales_contract_id': service.xtransaction_sales_name,'xquotationtrans_sales_phone': service.xtransaction_sales_phone,'xquotationtrans_sales_email': service.xtransaction_sales_email,'xquotationtrans_vp_email': service.xtransaction_vp_email,'xquotationtrans_gm_email': service.xtransaction_gm_email,'xquotationtrans_company_contract_id': service.xtransaction_merchdelegation_name,'xquotationtrans_company_alamat': service.xtransaction_merchdelegation_alamat,'xquotationtrans_client_delegation_contract_id': service.xtransaction_merchdelegation_name_user,'xquotationtrans_client_delegation_jabatan': service.xtransaction_merchdelegation_jabatan,'xquotationtrans_client_delegation_email': service.xtransaction_merchdelegation_email,'xquotationtrans_client_delegation_phone': service.xtransaction_merchdelegation_phone,'xquotationtrans_merchdelegation_name': service.xtransaction_merchdelegation_name_user_hidden,'xquotationtrans_merchdelegation_email': service.xtransaction_merchdelegation_email_hidden,'xquotationtrans_merchdelegation_phone': service.xtransaction_merchdelegation_phone_hidden,'xquotationtrans_pic_telkomsel': service.xtransaction_delegationtsel_id_name,'xquotationtrans_pic_telkomsel_phone': service.xtransaction_delegationtsel_id_phone}}
        return {'value': {}}  

    def onchange_xquotationtrans_number_contract_id_id(self, cr, uid, ids, xquotationtrans_number_contract_id, context=None):
        value = {'xquotationtrans_parent_id': False}
        if xquotationtrans_number_contract_id:
            department = self.pool.get('quotation.transaction.telkomsel').browse(cr, uid, xquotationtrans_number_contract_id)
        return {'value': value}

    # @api.model
    # def create(self, vals):
    #     x = self.env['ir.sequence'].next_by_code('quotation.transaction.telkomsel') or '/'
    #     vals['xquotationtrans_number_quotation'] = x
    #     return super(quotation_transaction_telkomsel, self).create(vals)

    @api.onchange('xquotationtrans_total_hargax','xquotationtrans_total_harga','xquotationtrans_discount')
    @api.one
    def update_agesm_onchange(self):
            self. xquotationtrans_total_hargax =  self.xquotationtrans_total_harga - (self.xquotationtrans_discount * self.xquotationtrans_total_harga / 100)
 
    @api.onchange('xquotationtrans_total_hargax','xquotationtrans_discount_ppnx', 'hargappn')
    def xxxx(self):
            self.xquotationtrans_discount_ppnx =  self.xquotationtrans_total_hargax * (self.hargappn / 100)

    @api.onchange('xquotationtrans_total_ppnx','xquotationtrans_total_hargax')
    @api.one
    def update_agesm_onchange_ppn(self):
            self. xquotationtrans_total_ppnx =  self.xquotationtrans_total_hargax * (10/100)

    # @api.multi
    # def new_quotation(self):
    #     self.ensure_one()
    #     self.state ='new'

    @api.multi
    @api.depends('xquotationtrans_discount')
    def pending_quotation(self):
        if self.xquotationtrans_number_contract_id == False :
            raise ValidationError('The number contract must be inserted before!')
        if  self.xquotationtrans_discount <= 30:
            self.ensure_one()
            self.state ='pending'
            # template = self.env.ref('contract_e.quotation_gm_mail_template', False)
            # mail = self.env['mail.template'].browse(template.id)
            # mail.send_mail(self.id, force_send=True)
        else:
            self.ensure_one()
            # template = self.env.ref('contract_e.quotation_vp_mail_template', False)
            # mail = self.env['mail.template'].browse(template.id)
            # mail.send_mail(self.id, force_send=True)

    @api.multi
    def approved_quotation(self):
        # self.write({'xquotationtrans_tseldelegation_otp': ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(randint(9,15)))})
        self.ensure_one()
        self.state ='approved'
        template = self.env.ref('contract_e.quotation_merchant_mail_template', False)
        mail = self.env['mail.template'].browse(template.id)
        mail.send_mail(self.id, force_send=True)
        # self.ensure_one()
        # template = self.env.ref('contract_e.approve_quotation_sales_mail_template', False)
        # mail = self.env['mail.template'].browse(template.id)
        # mail.send_mail(self.id, force_send=True)
    
    @api.multi
    def rejected_quotation(self):
        # if self.xquotationtrans_reject == False :
        #    raise ValidationError('The comment rejected contract must be inserted before!')
        self.ensure_one()
        self.state ='rejected'
        # template = self.env.ref('contract_e.reject_quotation_mail_template', False)
        # mail = self.env['mail.template'].browse(template.id)
        # mail.send_mail(self.id, force_send=True)

    @api.multi
    def final_quotation(self):
        # if self.xquotationtrans_tseldelegation_otp_confirmation != self.xquotationtrans_tseldelegation_otp :
        #    raise ValidationError('The OTP Must Inserted before!')
        self.ensure_one()
        self.state ='final'
        # template = self.env.ref('contract_e.final_quotation_sales_mail_template', False)
        # mail = self.env['mail.template'].browse(template.id)
        # mail.send_mail(self.id, force_send=True)
   
    @api.multi
    def clear_record_data(self):
        self.write({
            'xtransaction_tseldelegation_otp': ''
        })

    @api.constrains('xquotationtrans_tseldelegation_otp_confirmation')
    def validate_otpxx(self):
            if self.xquotationtrans_tseldelegation_otp_confirmation != self.xquotationtrans_tseldelegation_otp :
                raise ValidationError('The OTP Is Not valid!')

# Quotation Rate Card Price 
class quotation_total_price(models.Model):
    _name = "quotation.total.price"
    _rec_name = "xquotationtrans_main_ratecard_id"
    @api.multi
    @api.depends('xquotationtrans_qty', 'xquotationtrans_detailinventory_rate')
    def _get_total(self):
        for quotation in self:
            quotation.xquotationtrans_total = quotation.xquotationtrans_qty * quotation.xquotationtrans_detailinventory_rate

    xquotationtrans_main_ratecard_id = fields.Many2one('rate.card.main',string='Rate Card', select=True)
    xquotationtrans_inventory_ratecard_id = fields.Many2one('inventory.rate.card',string='Inventory', select=True)
    xquotationtrans_detailinventory_ratecard_id = fields.Many2one('detail.rate.card',string='Detail Inventory', select=True, track_visibility='onchange')
    xquotationtrans_detailinventory_remark = fields.Text(string="Remark", readonly=True)
    # Period Quotation
    xquotationtrans_date_begin = fields.Date("Period Start")
    xquotationtrans_end_date = fields.Date("Period End")
    xquotationtrans_qty = fields.Float(string='Total Impression')
    xquotationtrans_detailinventory_rate = fields.Integer(string='Price')
    # xquotationtrans_harga_sales = fields.Integer(string='Sales Price')        
    xquotationtrans_total = fields.Float(compute='_get_total', string='Total')
    xtotalquotation_trans_id = fields.Many2one('quotation.transaction.telkomsel',
                                ondelete='cascade', string="Total Rate Card", required=True)

    @api.model
    def create(self, vals):
        rec = super(quotation_total_price, self).create(vals)
        # ...        
        return rec

    def onchange_xquotationtrans_detailinventory_ratecard_id(self, cr, uid, ids, service, context=None):
        if service:
            service = self.pool.get('detail.rate.card').browse(cr, uid, service, context=context)
            return {'value': {'xquotationtrans_detailinventory_rate': service.xdetailratecard_rate, 'xquotationtrans_detailinventory_remark': service.xdetailratecard_remark}}
        return {'value': {}}