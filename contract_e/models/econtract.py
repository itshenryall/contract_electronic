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
            ('vp', 'Vice President'),
            ('gm', 'General Manager'),
            ('sales', 'Sales')
            ], string='Position', help="Choose position VP, GM, Delegation or Sales", required=True)
    xcontract_phone_number_one = fields.Char(string="Phone Number 1", size=15, readonly=False, required=True)
    xcontract_phone_number_two = fields.Char(string="Phone Number 2", size=15, readonly=False)    
    xcontract_address = fields.Text(string='Address',default='Telkomsel Smart Office, Jl. Gatot Subroto No.Kav. 52, RT.6/RW.1, Kuningan Bar., Mampang Prpt., Kota Jakarta Selatan, Daerah Khusus Ibukota Jakarta 12710')
    xcontract_department = fields.Char(string='Department', required=True)  
    # GM
    xcontract_vp_id = fields.Many2one('res.users',string='VP', select=True)
    xcontract_vp_parent_id = fields.Many2one('res.users',string='Parent VP', select=True)
    xcontract_vp_child_ids = fields.One2many('res.users', 'xcontract_vp_parent_id',string='Child VP')
    # SALES
    xcontract_vp_sales_id = fields.Many2one('res.users',string='VP', select=True)
    xcontract_vp_sales_name = fields.Char(related='xcontract_vp_sales_id.name')
    xcontract_vp_sales_email = fields.Char(related='xcontract_vp_sales_id.email')
    xcontract_vp_sales_department = fields.Char(related='xcontract_vp_sales_id.xcontract_department')
    xcontract_vp_sales_signature = fields.Binary(related='xcontract_vp_sales_id.xcontract_signature')    
    xcontract_vp_sales_position = fields.Selection(related='xcontract_vp_sales_id.xcontract_posisiton')
    xcontract_gm_sales_id = fields.Many2one('res.users',string='GM', select=True)
    xcontract_gm_sales_name = fields.Char(related='xcontract_gm_sales_id.name')
    xcontract_gm_sales_email = fields.Char(related='xcontract_gm_sales_id.email')
    xcontract_gm_sales_department = fields.Char(related='xcontract_gm_sales_id.xcontract_department')
    xcontract_gm_sales_signature = fields.Binary(related='xcontract_gm_sales_id.xcontract_signature')       
    xcontract_gm_sales_position = fields.Selection(related='xcontract_gm_sales_id.xcontract_posisiton')
    xcontract_vp_sales_parent_id = fields.Many2one('res.users',string='Parent VP', select=True)
    xcontract_vp_sales_child_ids = fields.One2many('res.users', 'xcontract_vp_sales_parent_id',string='Child VP')
    xcontract_signature = fields.Binary('Signature')

    def _get_default_image(self, cr, uid, context=None):
        image_path = get_module_resource('contract_e', 'static/src/img', 'avatar.png')
        return tools.image_resize_image_big(open(image_path, 'rb').read().encode('base64'))

    defaults = {
        'xcontract_signature': _get_default_image,
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


                 ###########################
                ### TELKOMSEL INFORMATION ###
                 ###########################
#USER Telkomsel
class telkomsel_delegation_user(models.Model):
    _name = "telkomsel.delegation.user"
    _rec_name = 'xuser_tseldelegation_name'
    _order = "xuser_tseldelegation_name desc"

    #Public Information
    # contact
    xuser_tseldelegation_name = fields.Char(string="Full Name", required=True) 
    xuser_tseldelegation_email = fields.Char(string="Email", size=50, required=True)
    xuser_tseldelegation_phone = fields.Char(string="Phone Number 1", size=15, readonly=False, required=True)
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
        image_path = get_module_resource('contract_e', 'static/src/img', 'avatar.png')        
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
    xmerch_delegation_id = fields.Many2one('merch.delegation.contract',string='Parent Company', select=True, ondelete='set null',)
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
        image_path = get_module_resource('contract_e', 'static/src/img', 'avatar.png')
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
    xuser_merchdelegation_password = fields.Char(string="Password")
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
        image_path = get_module_resource('contract_e', 'static/src/img', 'avatar.png')
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

    @api.onchange('xuser_merchdelegation_password')
    def generatepass(self):
        if self.xuser_merchdelegation_email == True :
           self.write({'xuser_merchdelegation_password': ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(randint(9,15)))})




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
    _order = "xtelkomsel_transaction_number desc" 
    
    status_contract = fields.Selection([
            ('aktif', 'Aktif')
            ], default='aktif')
    xtransaction_parent_id = fields.Many2one('transaction.econtract.telkomsel',string='Parent contract', select=True, track_visibility='onchange', ondelete='set null')
    xtransaction_child_ids = fields.One2many('transaction.econtract.telkomsel', 'xtransaction_parent_id',string='Child contract', ondelete='set null')
    xtransaction_sales_id = fields.Many2one('res.users','Sales', default=lambda self: self.env.user)
    xtransaction_sales_name = fields.Char(related='xtransaction_sales_id.name')
    xtransaction_sales_phone = fields.Char(related='xtransaction_sales_id.xcontract_phone_number_one')
    xtransaction_sales_email = fields.Char(related='xtransaction_sales_id.email')
    xtransaction_sales_position = fields.Selection(related='xtransaction_sales_id.xcontract_posisiton')
    xtransaction_sales_department = fields.Char(related='xtransaction_sales_id.xcontract_department')
    # VP 
    xtransaction_vp_name = fields.Char(related='xtransaction_sales_id.xcontract_vp_sales_name')
    xtransaction_vp_email = fields.Char(related='xtransaction_sales_id.xcontract_vp_sales_email')
    xtransaction_vp_sign = fields.Binary(related='xtransaction_sales_id.xcontract_vp_sales_signature')
    xtransaction_vp_position = fields.Selection(related='xtransaction_sales_id.xcontract_vp_sales_position')
    xtransaction_vp_department = fields.Char(related='xtransaction_sales_id.xcontract_vp_sales_department')
    # GM
    xtransaction_gm_name = fields.Char(related='xtransaction_sales_id.xcontract_gm_sales_name')
    xtransaction_gm_email = fields.Char(related='xtransaction_sales_id.xcontract_gm_sales_email')
    xtransaction_gm_sign = fields.Binary(related='xtransaction_sales_id.xcontract_gm_sales_signature')
    xtransaction_gm_position = fields.Selection(related='xtransaction_sales_id.xcontract_gm_sales_position')
    xtransaction_gm_department = fields.Char(related='xtransaction_sales_id.xcontract_gm_sales_department')
    # Contract
    xtransaction_date = fields.Date("Contract Date", default=datetime.today())
    state = fields.Selection([
            ('draft', 'Draft'),
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('final', 'Final')
            ], default='draft')
    sent = fields.Boolean(readonly=True, default=False, copy=False,
        help="It indicates that the invoice has been sent.")
    #telkomsel delegation
    xtransaction_tseldelegation_id = fields.Many2one('telkomsel.delegation.user',string='Telkomsel Delegation', track_visibility='onchange', required=True)
    xtransaction_tseldelegation_name = fields.Char(string="Name")
    xtransaction_tseldelegation_position = fields.Char(string="Position") 
    xtransaction_tseldelegation_phone = fields.Char(string="Phone Number", size=15, readonly=False)
    xtransaction_tseldelegation_email = fields.Char(string="Email", size=240)
    #Client name
    xtransaction_merchdelegation_id = fields.Many2one('merch.delegation.contract',string='Company', track_visibility='onchange', required=True)
    xtransaction_merchdelegation_name = fields.Char(string="Name")
    xtransaction_merchdelegation_alamat = fields.Text(string='Address')
    xtransaction_merchdelegation_npwp = fields.Text(string='NPWP')
    #Client delegation
    xtransaction_merchdelegation_user_id = fields.Many2one('merch.delegation.user',string='Client Delegation Name', track_visibility='onchange', required=True)
    xtransaction_merchdelegation_name_user = fields.Char(string="Name")
    xtransaction_merchdelegation_jabatan = fields.Char(string="Position", size=50)
    xtransaction_merchdelegation_email = fields.Char(string="Email", size=240)
    xtransaction_merchdelegation_phone = fields.Char(string="Phone Number", size=15, readonly=False)
    xtransaction_merchdelegation_signature = fields.Binary('Signature')
    # Transaction
    xtransaction_date_begin = fields.Date("Start", default=datetime.today())
    xtransaction_end_date = fields.Date("End", default=datetime.today())
    # Contract
    xtelkomsel_transaction_number = fields.Char(string="Contract Number", size=50, required=True)
    # DATA BANK
    xtransaction_tseldelegation_bank_id = fields.Many2one('telkomsel.bank.account',string='Telkomsel Account', track_visibility='onchange', required=True)
    xtransaction_tseldelegation_account_bank_name = fields.Char(string="Nama Pemilik Rekening") 
    xtransaction_tseldelegation_bank_name = fields.Char(string="Nama Bank") 
    xtransaction_tseldelegation_referencelink = fields.Text(string="Reference link", size=240)
    xtransaction_tseldelegation_alamat_bank = fields.Text(string="Alamat Cabang Bank", size=240)
    xtransaction_tseldelegation_norek = fields.Char(string="No Rekening", size=30)    
    xtransaction_delegationtsel_id = fields.Many2one('telkomsel.delegation.user',string='PIC Telkomsel', track_visibility='onchange', required=True)
    xtransaction_delegationtsel_id_name = fields.Char(string="Name")
    xtransaction_delegationtsel_id_phone = fields.Char(string="Phone Number", size=15, readonly=False)
    xtransaction_delegationmerch_id = fields.Many2one('merch.delegation.user',string='PIC Client', track_visibility='onchange', required=True)
    xtransaction_merchdelegation_name_user_hidden = fields.Char(string="Name")
    xtransaction_merchdelegation_email_hidden = fields.Char(string="Email", size=240)
    xtransaction_merchdelegation_phone_hidden = fields.Char(string="Phone Number", size=15)
    xtransaction_reject_contract = fields.Text(string="Detail Reject Contract", size=30)  
    #CONVERT DATE TO STRING
    xday = fields.Char(string="day")
    xmonth = fields.Char(string="month")
    xyears = fields.Char(string="years")
    xtaa = fields.Char(string="month")  
    xdate = fields.Char(string="month")


    xday_date_start = fields.Char(string="day")
    xmonth_date_start = fields.Char(string="month")
    xyears_date_start = fields.Char(string="years")
    xtaa_date_start = fields.Char(string="month")
    xdate_start = fields.Char(string="month")


    xday_date_end = fields.Char(string="day")
    xmonth_date_end = fields.Char(string="month")
    xyears_date_end = fields.Char(string="years")
    xtaa_date_end = fields.Char(string="month")
    xdate_end = fields.Char(string="month")

    #CONVERT DATE TO STRING ENG
    xdayx = fields.Char(string="day")
    xmonthx = fields.Char(string="month")
    xyearsx = fields.Char(string="years")
    xtaax = fields.Char(string="month")  
    xdatex = fields.Char(string="month")


    xday_date_startx = fields.Char(string="day")
    xmonth_date_startx = fields.Char(string="month")
    xyears_date_startx = fields.Char(string="years")
    xtaa_date_startx = fields.Char(string="month")
    xdate_startx = fields.Char(string="month")


    xday_date_endx = fields.Char(string="day")
    xmonth_date_endx = fields.Char(string="month")
    xyears_date_endx = fields.Char(string="years")
    xtaa_date_endx = fields.Char(string="month")
    xdate_endx = fields.Char(string="month")

    # RATE CARD
    xtransaction_ratecard_main_id = fields.Many2one('rate.card.main',string='Rate Card Name', track_visibility='onchange')
    xtransaction_ratecard_main_name = fields.Char(string="Rate Card Name")
    # DATA TELKOMSEL
    xtransaction_tseldelegation_alamat_telkomsel_id = fields.Many2one('telkomsel.location',string='Alamat Telkomsel', track_visibility='onchange', required=True)
    xtransaction_tseldelegation_alamat_name = fields.Char(string="Nama Perusahaan") 
    xtransaction_tseldelegation_alamat = fields.Text(string="Alamat", size=240) 
    xtransaction_tseldelegation_lantai = fields.Char(string="lantai")
    xtransaction_tseldelegation_no_telp = fields.Char(string="No Telepon", size=15)
    xtransaction_tseldelegation_facsimile = fields.Char(string="Facsimile", size=30)
    xtransaction_tseldelegation_attention = fields.Text(string="U.p./Attention", size=30)
    xtransaction_tseldelegation_otp = fields.Char(string="Kode OTP", required=True, default='Click on OTP')
    xtransaction_tseldelegation_otp_confirmation = fields.Char(string="Kode OTP")
    xtransaction_status_contract = fields.Selection([
            ('tidak', 'Not Active'),
            ('aktif', 'Active')
            ],string="Contract State",default="aktif")
    company_id = fields.Many2one('res.company', string='Company', change_default=True,
        required=True, readonly=True, default=lambda self: self.env['res.company']._company_default_get('transaction.econtract.telkomsel'))
    user_id = fields.Many2one('res.users', string='Salesperson', track_visibility='onchange',
        readonly=True, default=lambda self: self.env.user)
    color = fields.Integer(string='Color Index')


    def _get_default_image(self, cr, uid, context=None):
        image_path = get_module_resource('contract_e', 'static/src/img', 'avatar.png')
        return tools.image_resize_image_big(open(image_path, 'rb').read().encode('base64'))

    @api.model
    def create(self, vals):
        tools.image_resize_images(vals)
        return super(transaction_econtract_telkomsel, self).create(vals)

    @api.multi
    def write(self, vals):
        tools.image_resize_images(vals)
        return super(transaction_econtract_telkomsel, self).write(vals)

    defaults = {
        'color': 0,
        'xtransaction_sales_id':lambda self, cr, uid, ctx=None: uid,
        'xtransaction_merchdelegation_signature': _get_default_image,
    }

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
            return {'value': {'xtransaction_tseldelegation_account_bank_name': service.xbank_tseldelegation_name,'xtransaction_tseldelegation_bank_name': service.xbank_tseldelegation_bank_name,'xtransaction_tseldelegation_alamat_bank': service.xuser_tseldelegation_alamat_bank,'xtransaction_tseldelegation_norek': service.xbank_tseldelegation_norek}}
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


    def onchange_xtransaction_sales_id(self, cr, uid, ids, xtransaction_sales_id, context=None):
        value = {'xtransaction_parent_id': False}
        if xtransaction_sales_id:
            department = self.pool.get('merch.delegation.contract').browse(cr, uid, xtransaction_sales_id)
            value['xtransaction_parent_id'] = department.xtelkomsel_transaction_number.id
        return {'value': value}
    
        
    # @api.model
    # def create(self, vals):
    #     x = self.env['ir.sequence'].next_by_code('transaction.econtract.telkomsel') or '/'
    #     vals['xtelkomsel_transaction_number'] = x
    #     return super(transaction_econtract_telkomsel, self).create(vals)

    @api.multi
    def status_dari_contract(self):
        self.ensure_one()
        self.status_contract ='aktif'

    @api.multi
    def pending_contract(self):
        if self.xtransaction_tseldelegation_email == False :
           raise ValidationError('Delegation email Cannot ne null!')
        if self.xtransaction_merchdelegation_email == False :
           raise ValidationError('Merchant email Cannot be null!')
        if self.xtelkomsel_transaction_number == False :
           raise ValidationError('Number contract Cannot be null!')
        if self.xtransaction_date == False :
           raise ValidationError('Contract Date Cannot be null!')
        if self.xtransaction_tseldelegation_id == False :
           raise ValidationError('Tsel Delegation Cannot be null!')
        if self.xtransaction_merchdelegation_id == False :
           raise ValidationError('Company from client & delegation Cannot be null!')
        if self.xtransaction_merchdelegation_user_id == False :
           raise ValidationError('Client Delegation name Cannot be null!')
        if self.xtransaction_tseldelegation_alamat_telkomsel_id == False :
           raise ValidationError('Alamat Telkomsel Cannot be null!')
        if self.xtransaction_tseldelegation_bank_id == False :
           raise ValidationError('Telkomsel Account Cannot be null!')
        if self.xtransaction_delegationtsel_id == False :
           raise ValidationError('PIC Telkomsel Cannot be null!')
        if self.xtransaction_delegationmerch_id == False :
           raise ValidationError('PIC Client Cannot be null!')
        self.ensure_one()
        self.state ='pending'
        template = self.env.ref('contract_e.new_contract_mail_template', False)
        mail = self.env['mail.template'].browse(template.id)
        mail.send_mail(self.id, force_send=True)
 
    @api.multi
    def approved_contract_merchant(self):
        self.write({'xtransaction_tseldelegation_otp': ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(randint(9,15)))})
        self.ensure_one()
        self.state ='approved'
        template = self.env.ref('contract_e.approve_contract_merchant_mail_template', False)
        mail = self.env['mail.template'].browse(template.id)
        mail.send_mail(self.id, force_send=True)
        self.ensure_one()
        template = self.env.ref('contract_e.approve_contract_sales_mail_template', False)
        mail = self.env['mail.template'].browse(template.id)
        mail.send_mail(self.id, force_send=True)


    @api.multi
    def rejected_contract(self):
        if self.xtransaction_reject_contract == False :
           raise ValidationError('The comment rejected contract must be inserted before!')
        self.ensure_one()
        self.state ='rejected'
        # template = self.env.ref('contract_e.reject_contract_sales_mail_template', False)
        # mail = self.env['mail.template'].browse(template.id)
        # mail.send_mail(self.id, force_send=True)

    @api.multi
    def final_contract(self):
        # if self.xtransaction_tseldelegation_otp_confirmation != self.xtransaction_tseldelegation_otp :
        #    raise ValidationError('Please fill in the OTP before Proceeding!')
        self.ensure_one()
        self.state ='final'
        template = self.env.ref('contract_e.final_contract_sales_mail_template', False)
        mail = self.env['mail.template'].browse(template.id)
        mail.send_mail(self.id, force_send=True)


    #BAHASA INDONESIA
    @api.onchange('xtransaction_date','xday','xmonth','xyears')
    @api.one
    def convertostringa(self):
        self.xtransaction_date
        do_date = datetime.strptime(self.xtransaction_date, "%Y-%m-%d")
        self.xday = do_date.day
        self.xmonth = str(do_date.month)
        self.xyears = do_date.year


    @api.onchange('xtransaction_date_begin','xday_date_start','xmonth_date_start','xyears_date_start')
    @api.one
    def convertostringaa(self):
        self.xtransaction_date_begin
        do_date_begin = datetime.strptime(self.xtransaction_date_begin, "%Y-%m-%d")
        self.xday_date_start = do_date_begin.day
        self.xmonth_date_start = str(do_date_begin.month)
        self.xyears_date_start = do_date_begin.year


    @api.onchange('xtransaction_end_date','xday_date_end','xmonth_date_end','xyears_date_end')
    @api.one
    def convertostringaaa(self):
        self.xtransaction_end_date
        do_date_end = datetime.strptime(self.xtransaction_end_date, "%Y-%m-%d")
        self.xday_date_end = do_date_end.day
        self.xmonth_date_end = str(do_date_end.month)
        self.xyears_date_end = do_date_end.year
        
    #BAHASA INGGRIS
    @api.onchange('xtransaction_date','xdayx','xmonthx','xyearsx')
    @api.one
    def convertostringb(self):
        self.xtransaction_date
        do_datex = datetime.strptime(self.xtransaction_date, "%Y-%m-%d")
        self.xdayx = do_datex.day
        self.xmonthx = str(do_datex.month)
        self.xyearsx = do_datex.year


    @api.onchange('xtransaction_date_begin','xday_date_startx','xmonth_date_startx','xyears_date_startx')
    @api.one
    def convertostringbb(self):
        self.xtransaction_date_begin
        do_date_begin_eng = datetime.strptime(self.xtransaction_date_begin, "%Y-%m-%d")
        self.xday_date_startx = do_date_begin_eng.day
        self.xmonth_date_startx = str(do_date_begin_eng.month)
        self.xyears_date_startx = do_date_begin_eng.year



    @api.onchange('xtransaction_end_date','xday_date_endx','xmonth_date_endx','xyears_date_endx')
    @api.one
    def convertostringbbb(self):
        self.xtransaction_end_date
        do_date_end_eng = datetime.strptime(self.xtransaction_end_date, "%Y-%m-%d")
        self.xday_date_endx = do_date_end_eng.day
        self.xmonth_date_endx = str(do_date_end_eng.month)
        self.xyears_date_endx = do_date_end_eng.year
        

    #indonesian translate

    @api.onchange('xmonth','xtaa')
    @api.one
    def one(self):
        if self.xmonth == "1":
           self.xtaa = 'Januari'
        if self.xmonth == "2":
           self.xtaa = 'Febuary'
        if self.xmonth == "3":
           self.xtaa = 'Maret'
        if self.xmonth == "4":
           self.xtaa = 'April'
        if self.xmonth == "5":
           self.xtaa = 'Mei'
        if self.xmonth == "6":
           self.xtaa = 'Juni'
        if self.xmonth == "7":
           self.xtaa = 'July'
        if self.xmonth == "8":
           self.xtaa = 'Agustus'
        if self.xmonth == "9":
           self.xtaa = 'September'
        if self.xmonth == "10":
           self.xtaa = 'Oktober'
        if self.xmonth == "11":
           self.xtaa = 'November'
        if self.xmonth == "12":
           self.xtaa = 'Desember'


    @api.onchange('xmonth_date_start','xtaa_date_start')
    @api.one
    def two(self):
        if self.xmonth_date_start == "1":
           self.xtaa_date_start = 'Januari'
        if self.xmonth_date_start == "2":
           self.xtaa_date_start = 'Febuary'
        if self.xmonth_date_start == "3":
           self.xtaa_date_start = 'Maret'
        if self.xmonth_date_start == "4":
           self.xtaa_date_start = 'April'
        if self.xmonth_date_start == "5":
           self.xtaa_date_start = 'Mei'
        if self.xmonth_date_start == "6":
           self.xtaa_date_start = 'Juni'
        if self.xmonth_date_start == "7":
           self.xtaa_date_start = 'July'
        if self.xmonth_date_start == "8":
           self.xtaa_date_start = 'Agustus'
        if self.xmonth_date_start == "9":
           self.xtaa_date_start = 'September'
        if self.xmonth_date_start == "10":
           self.xtaa_date_start = 'Oktober'
        if self.xmonth_date_start == "11":
           self.xtaa_date_start = 'November'
        if self.xmonth_date_start == "12":
           self.xtaa_date_start = 'Desember'


    @api.onchange('xmonth_date_end','xtaa_date_end')
    @api.one
    def three(self):
        if self.xmonth_date_end == "1":
           self.xtaa_date_end = 'Januari'
        if self.xmonth_date_end == "2":
           self.xtaa_date_end = 'Febuary'
        if self.xmonth_date_end == "3":
           self.xtaa_date_end = 'Maret'
        if self.xmonth_date_end == "4":
           self.xtaa_date_end = 'April'
        if self.xmonth_date_end == "5":
           self.xtaa_date_end = 'Mei'
        if self.xmonth_date_end == "6":
           self.xtaa_date_end = 'Juni'
        if self.xmonth_date_end == "7":
           self.xtaa_date_end = 'July'
        if self.xmonth_date_end == "8":
           self.xtaa_date_end = 'Agustus'
        if self.xmonth_date_end == "9":
           self.xtaa_date_end = 'September'
        if self.xmonth_date_end == "10":
           self.xtaa_date_end = 'Oktober'
        if self.xmonth_date_end == "11":
           self.xtaa_date_end = 'November'
        if self.xmonth_date_end == "12":
           self.xtaa_date_end = 'Desember'

 


    #english translate

    @api.onchange('xmonthx','xtaax')
    @api.one
    def onex(self):
        if self.xmonthx == "1":
           self.xtaax = 'January'
        if self.xmonthx == "2":
           self.xtaax = 'February'
        if self.xmonthx == "3":
           self.xtaax = 'March'
        if self.xmonthx == "4":
           self.xtaax = 'April'
        if self.xmonthx == "5":
           self.xtaax = 'May'
        if self.xmonthx == "6":
           self.xtaax = 'June'
        if self.xmonthx == "7":
           self.xtaax= 'July'
        if self.xmonthx == "8":
           self.xtaax = 'August'
        if self.xmonthx == "9":
           self.xtaax = 'September'
        if self.xmonthx == "10":
           self.xtaax= 'October'
        if self.xmonthx == "11":
           self.xtaax = 'November'
        if self.xmonthx == "12":
           self.xtaax = 'December'


    @api.onchange('xmonth_date_startx','xtaa_date_startx')
    @api.one
    def twox(self):
        if self.xmonth_date_startx == "1":
           self.xtaa_date_startx = 'January'
        if self.xmonth_date_startx == "2":
           self.xtaa_date_startx = 'February'
        if self.xmonth_date_startx == "3":
           self.xtaa_date_startx = 'March'
        if self.xmonth_date_startx == "4":
           self.xtaa_date_startx = 'April'
        if self.xmonth_date_startx == "5":
           self.xtaa_date_startx = 'May'
        if self.xmonth_date_startx == "6":
           self.xtaa_date_startx = 'June'
        if self.xmonth_date_startx == "7":
           self.xtaa_date_startx = 'July'
        if self.xmonth_date_startx == "8":
           self.xtaa_date_startx = 'August'
        if self.xmonth_date_startx == "9":
           self.xtaa_date_startx = 'September'
        if self.xmonth_date_startx == "10":
           self.xtaa_date_startx = 'October'
        if self.xmonth_date_startx == "11":
           self.xtaa_date_startx = 'November'
        if self.xmonth_date_startx == "12":
           self.xtaa_date_startx = 'December'


    @api.onchange('xmonth_date_endx','xtaa_date_endx')
    @api.one
    def threex(self):
        if self.xmonth_date_endx == "1":
           self.xtaa_date_endx = 'January'
        if self.xmonth_date_endx == "2":
           self.xtaa_date_endx = 'February'
        if self.xmonth_date_endx == "3":
           self.xtaa_date_endx = 'March'
        if self.xmonth_date_endx == "4":
           self.xtaa_date_endx = 'April'
        if self.xmonth_date_endx == "5":
           self.xtaa_date_endx = 'May'
        if self.xmonth_date_endx == "6":
           self.xtaa_date_endx = 'June'
        if self.xmonth_date_endx == "7":
           self.xtaa_date_endx = 'July'
        if self.xmonth_date_endx == "8":
           self.xtaa_date_endx = 'August'
        if self.xmonth_date_endx == "9":
           self.xtaa_date_endx = 'September'
        if self.xmonth_date_endx == "10":
           self.xtaa_date_endx = 'October'
        if self.xmonth_date_endx == "11":
           self.xtaa_date_endx = 'November'
        if self.xmonth_date_endx == "12":
           self.xtaa_date_endx = 'December'
  

    #BAHASA INDONESIA
    @api.onchange('xday','xyears','xtaa','xdate')
    @api.one
    def final_one(self):
        a = self.xday
        b = self.xtaa
        c = self.xyears
        self.xdate = str(a)+" "+str(b)+" "+str(c)


    @api.onchange('xday_date_start','xyears_date_start','xtaa_date_start','xdate_start')
    @api.one
    def final_one_one(self):
        a = self.xday_date_start
        b = self.xtaa_date_start
        c = self.xyears_date_start
        self.xdate_start = str(a)+" "+str(b)+" "+str(c)


    @api.onchange('xday_date_end','xyears_date_end','xtaa_date_end','xdate_end')
    @api.one
    def final_one_two(self):
        a = self.xday_date_end
        b = self.xtaa_date_end
        c = self.xyears_date_end
        self.xdate_end = str(a)+" "+str(b)+" "+str(c)

    #BAHASA INGGRIS
    @api.onchange('xdayx','xyearsx','xtaax','xdatex')
    @api.one
    def final_two(self):
        d = self.xdayx
        e = self.xtaax
        f = self.xyearsx
        self.xdatex = str(d)+" "+str(e)+" "+str(f)


    @api.onchange('xday_date_startx','xyears_date_startx','xtaa_date_startx','xdate_startx')
    @api.one
    def final_two_two(self):
        d = self.xday_date_startx
        e = self.xtaa_date_startx
        f = self.xyears_date_startx
        self.xdate_startx = str(d)+" "+str(e)+" "+str(f)


    @api.onchange('xday_date_endx','xyears_date_endx','xtaa_date_endx','xdate_endx')
    @api.one
    def final_two_three(self):
        d = self.xday_date_endx
        e = self.xtaa_date_endx
        f = self.xyears_date_endx
        self.xdate_endx = str(d)+" "+str(e)+" "+str(f)

    

    @api.multi
    def clear_record_data(self):
        self.write({
            'xtransaction_tseldelegation_otp': ''
        })

    @api.constrains('xtransaction_tseldelegation_otp_confirmation')
    def validate_otpxx(self):
            if self.xtransaction_tseldelegation_otp_confirmation != self.xtransaction_tseldelegation_otp :
                raise ValidationError('The OTP Is Not valid!')

    @api.multi
    @api.constrains('xtransaction_end_date', 'xtransaction_date_begin')
    def _check_date(self):
        for rec in self:
            if rec.xtransaction_end_date < rec.xtransaction_date_begin:
                raise ValidationError(_('Sorry, End Date Contract Must be greater Than Start Date Contract'))

                  
                 ##########################
                ######## QUOTATION #########
                 ##########################
# Quotation
class quotation_transaction_telkomsel(models.Model):
    _name = "quotation.transaction.telkomsel"
    _rec_name = 'xquotationtrans_number_quotation'
    _order = "xquotationtrans_number_quotation desc" 


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
            ], string='Status')

    state_usage = fields.Selection([
            ('draft', 'Draft'),
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('final', 'Final')
            ], string='Status')

    sent = fields.Boolean(readonly=True, default=False, copy=False,
        help="It indicates that the invoice has been sent.")
    
    xquotationtrans_usage_quotation = fields.Selection([('usage', 'Usage'), ('order', 'Order')], string="Penagihan")
    xquotationtrans_number_contract_id = fields.Many2one('transaction.econtract.telkomsel',string='Contract Number', track_visibility='onchange', select=True)
    xquotationtrans_number_quotation = fields.Char(string='quotation number', size=50, required=True)
    # xquotationtrans_number_usage = fields.Char(string='SOA')
    # SALES
    xquotationtrans_sales_contract_id = fields.Many2one('res.users','Sales', default=lambda self: self.env.user)
    xquotationtrans_sales_name = fields.Char(related='xquotationtrans_sales_contract_id.name')
    xquotationtrans_sales_phone = fields.Char(related='xquotationtrans_sales_contract_id.xcontract_phone_number_one')
    xquotationtrans_sales_email = fields.Char(related='xquotationtrans_sales_contract_id.email')
    xquotationtrans_sign_sales = fields.Binary(related='xquotationtrans_sales_contract_id.xcontract_signature')
    xquotationtrans_sales_position = fields.Selection(related='xquotationtrans_sales_contract_id.xcontract_posisiton')
    xquotationtrans_sales_department = fields.Char(related='xquotationtrans_sales_contract_id.xcontract_department')
    # Data VP and GM
    xquotationtrans_name_vp = fields.Char(related='xquotationtrans_sales_contract_id.xcontract_vp_sales_name')
    xquotationtrans_name_gm = fields.Char(related='xquotationtrans_sales_contract_id.xcontract_gm_sales_name')
    xquotationtrans_email_vp = fields.Char(related='xquotationtrans_sales_contract_id.xcontract_vp_sales_email')
    xquotationtrans_email_gm = fields.Char(related='xquotationtrans_sales_contract_id.xcontract_gm_sales_email')
    xquotationtrans_sign_vp = fields.Binary(related='xquotationtrans_sales_contract_id.xcontract_vp_sales_signature')
    xquotationtrans_sign_gm = fields.Binary(related='xquotationtrans_sales_contract_id.xcontract_gm_sales_signature')
    xquotationtrans_vp_position = fields.Selection(related='xquotationtrans_sales_contract_id.xcontract_vp_sales_position')
    xquotationtrans_gm_position = fields.Selection(related='xquotationtrans_sales_contract_id.xcontract_gm_sales_position')
    xquotationtrans_vp_department = fields.Char(related='xquotationtrans_sales_contract_id.xcontract_vp_sales_department')
    xquotationtrans_gm_department = fields.Char(related='xquotationtrans_sales_contract_id.xcontract_gm_sales_department')
    # Company
    xquotationtrans_company_npwp = fields.Char(string='NPWP')
    xquotationtrans_company_contract_id = fields.Char(string='Company')
    xquotationtrans_company_alamat = fields.Text(string='Address')
    # Client Delegation
    xquotationtrans_client_delegation_signature = fields.Binary('Merchant Sign')    
    xquotationtrans_client_delegation_contract_id = fields.Char(string='Client Delegation')
    xquotationtrans_client_delegation_jabatan = fields.Char(string="Position", size=50)
    xquotationtrans_client_delegation_email = fields.Char(string="Email", size=240)
    xquotationtrans_client_delegation_phone = fields.Char(string="Phone Number", size=15, readonly=False)
    xquotationtrans_company_product = fields.Char(string='Product / Brand')
    xquotationtrans_company_brand_category = fields.Selection([
            ('agriculture','Agriculture'),
            ('automotive','Automotive'),
            ('banking','Banking'),
            ('baby','Baby Product'),
            ('consulting','Consulting'),
            ('ecommerce','E-Commerce'),
            ('edu','Education'),
            ('elctro','Electronics'),
            ('entertainmet','Entertainment'),
            ('fashio','Fashion'),
            ('finance','Finance'),
            ('govern','Government'),
            ('helath','Healthcare'),
            ('hospital','Hospitality'),
            ('insurance','Insurance'),
            ('maternity','Maternity Product'),
            ('media','Media'),
            ('pol','Politic'),
            ('pro','Properties'),
            ('rec','Recreation/ Leisure'),
            ('ret','Retail Store'),
            ('soc','Social Media'),
            ('tec','Technology & IT'),
            ('prt','Printing'),
            ('acc','Accomodation'),
            ('app','Apparel/ Personal Accessories'),
            ('bic','Bicycle Manufacturing'),
            ('com','Communication'),
            ('comp','Computer'),
            ('corp','Corporate'),
            ('Event','Event Organizer'),
            ('fo','Food'),
            ('gad','Gadget'),
            ('hou','Household Equipment & Appliances'),
            ('house','Household Products & Supplies'),
            ('inds','Industrial Products'),
            ('jewe','Jewelry'),
            ('log','Logistic & Distribution Service'),
            ('medic','Medicines/ Pharmaceutical'),
            ('musc','Music'),
            ('off','Office Equipment'),
            ('oil','Oil & Gas'),
            ('publ','Public Service'),
            ('restu','Restaurant'),
            ('reta','Retail - Clothing'),
            ('smok','Smoking & Accessories'),
            ('stati','Stationery Products'),
            ('trans','Transportation'),
            ('trav','Travel & Airline'),
            ('hairc','FMCG - Haircare'),
            ('skinc','FMCG - Skincare'),
            ('toilet','FMCG - Toiletres'),
            ('bever','Beverage'),
            ('other','Other')
            ],string="Brand Category",default="agriculture")
    xquotationtrans_company_name = fields.Char(string='Campaign Name')
    xquotationtrans_date = fields.Date("Date", default=datetime.today())
    # ATTENTION Company
    xquotationtrans_merchdelegation_name = fields.Char(string="PIC")
    xquotationtrans_merchdelegation_email = fields.Char(string="Email")
    xquotationtrans_merchdelegation_phone = fields.Char(string="No HP")
    xquotationtrans_invoices_address = fields.Text(string="Invoice Address")
    # PIC Telkomsel
    xquotationtrans_pic_telkomsel = fields.Char(string='Proposed By (PIC Telkomsel)')
    xquotationtrans_pic_telkomsel_phone = fields.Char(string="Contact Number")
    # DATA BANK
    xquotationtrans_account_bank_name = fields.Char(string="Nama Pemilik Rekening") 
    xquotationtrans_bank_name = fields.Char(string="Nama Bank") 
    xquotationtrans_alamat_bank = fields.Text(string="Alamat Cabang Bank", size=240)
    xquotationtrans_norek = fields.Char(string="No Rekening", size=30)    
    # DATA TELKOMSEL INFO
    xquotationtrans_alamat_name = fields.Char(string="Nama Perusahaan") 
    xquotationtrans_alamat = fields.Text(string="Alamat", size=240) 
    xquotationtrans_lantai = fields.Char(string="lantai")
    xquotationtrans_no_telp = fields.Char(string="No Telepon", size=15)
    xquotationtrans_facsimile = fields.Char(string="Facsimile", size=30)
    xquotationtrans_attention = fields.Text(string="U.p./Attention", size=30)     
    #RATE CARD ORDER
    xquotationtrans_list_rate_card_ids = fields.One2many(
        'quotation.total.price', 'xtotalquotation_trans_id', string="List Rate Card")
    xquotationtrans_discount   = fields.Float(string='Discount Sales')
    xquotationtrans_total_harga = fields.Float(string='Total Gross', store=True, readonly=True, compute='_get_total', track_visibility='always')
    xquotationtrans_total_hargax =  fields.Float(string='Total')
    xquotationtrans_total_harga_final =  fields.Float(string='Total')
    xquotationtrans_discount_ppnx = fields.Float(string='Ppn')
    hargappn = fields.Float(string='ppn 10%')
    xquotationtrans_total_bayar = fields.Float(compute='_get_total_bayar', string='Total Bayar') #di hidden#
    xquotationtrans_total_bayar_fix = fields.Float(compute='_get_total_bayar_fix', string='Total Bayar(Inc.PPn 10%)') #show
    # RATE CARD USAGE
    xquotationtrans_list_rate_card_ids_usage = fields.One2many(
        'quotation.total.price', 'xtotalquotation_trans_id', string="List Rate Card")
    xquotationtrans_discount_usage = fields.Float(string='Discount Sales')
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


    def _get_default_image(self, cr, uid, context=None):
        image_path = get_module_resource('contract_e', 'static/src/img', 'avatar.png')
        return tools.image_resize_image_big(open(image_path, 'rb').read().encode('base64'))

    @api.model
    def create(self, vals):
        tools.image_resize_images(vals)
        return super(quotation_transaction_telkomsel, self).create(vals)

    @api.multi
    def write(self, vals):
        tools.image_resize_images(vals)
        return super(quotation_transaction_telkomsel, self).write(vals)

    defaults = {
        'xquotationtrans_sales_contract_id':lambda self, cr, uid, ctx=None: uid,
        'xquotationtrans_client_delegation_signature': _get_default_image,
    }

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
            return {'value': {'xquotationtrans_company_npwp': service.xtransaction_merchdelegation_npwp, 'xquotationtrans_company_contract_id': service.xtransaction_merchdelegation_name,'xquotationtrans_company_alamat': service.xtransaction_merchdelegation_alamat,'xquotationtrans_client_delegation_contract_id': service.xtransaction_merchdelegation_name_user,'xquotationtrans_client_delegation_jabatan': service.xtransaction_merchdelegation_jabatan,'xquotationtrans_client_delegation_email': service.xtransaction_merchdelegation_email,'xquotationtrans_client_delegation_phone': service.xtransaction_merchdelegation_phone,'xquotationtrans_merchdelegation_name': service.xtransaction_merchdelegation_name_user_hidden,'xquotationtrans_merchdelegation_email': service.xtransaction_merchdelegation_email_hidden,'xquotationtrans_merchdelegation_phone': service.xtransaction_merchdelegation_phone_hidden, 'xquotationtrans_pic_telkomsel': service.xtransaction_delegationtsel_id_name, 'xquotationtrans_pic_telkomsel_phone': service.xtransaction_delegationtsel_id_phone, 'xquotationtrans_account_bank_name': service.xtransaction_tseldelegation_account_bank_name, 'xquotationtrans_bank_name': service.xtransaction_tseldelegation_bank_name, 'xquotationtrans_alamat_bank': service.xtransaction_tseldelegation_alamat_bank, 'xquotationtrans_norek': service.xtransaction_tseldelegation_norek, 'xquotationtrans_alamat_name': service.xtransaction_tseldelegation_alamat_name, 'xquotationtrans_alamat': service.xtransaction_tseldelegation_alamat, 'xquotationtrans_lantai': service.xtransaction_tseldelegation_lantai, 'xquotationtrans_no_telp': service.xtransaction_tseldelegation_no_telp, 'xquotationtrans_facsimile': service.xtransaction_tseldelegation_facsimile, 'xquotationtrans_attention': service.xtransaction_tseldelegation_attention}}
        return {'value': {}}  

    def onchange_xquotationtrans_number_contract_id_id(self, cr, uid, ids, xquotationtrans_number_contract_id, context=None):
        value = {'xquotationtrans_parent_id': False}
        if xquotationtrans_number_contract_id:
            department = self.pool.get('quotation.transaction.telkomsel').browse(cr, uid, xquotationtrans_number_contract_id)
        return {'value': value}

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
    def usage_quotation(self):
        self.ensure_one()
        self.xquotationtrans_usage_quotation ='usage'

    @api.multi
    def order_quotation(self):
        self.ensure_one()
        self.xquotationtrans_usage_quotation ='order'

    # State USAGE
    @api.multi
    @api.depends('xquotationtrans_discount_usage')
    def pending_usage(self):
        if self.xquotationtrans_number_contract_id == False :
            raise ValidationError('The number contract must be inserted before!')
        if self.xquotationtrans_usage_quotation == False :
           raise ValidationError('Choose Quotation Cannot ne null!')
        if self.xquotationtrans_number_quotation == False :
           raise ValidationError('Quotation Number Cannot be null!')
        if  self.xquotationtrans_discount_usage <= 30:
            self.ensure_one()
            self.state_usage ='pending'
            template = self.env.ref('contract_e.soa_gm_mail_template', False)
            mail = self.env['mail.template'].browse(template.id)
            mail.send_mail(self.id, force_send=True)
        else:
            self.ensure_one()
            self.state_usage ='pending'
            template = self.env.ref('contract_e.soa_vp_mail_template', False)
            mail = self.env['mail.template'].browse(template.id)
            mail.send_mail(self.id, force_send=True)


    # @api.multi
    # def approved_quotation(self):
    #     if  self.xquotationtrans_discount <= 30:
    #         self.ensure_one()
    #         self.state ='approved'
    #         template = self.env.ref('contract_e.approve_quotation_merchant_mail_template', False)
    #         mail = self.env['mail.template'].browse(template.id)
    #         mail.send_mail(self.id, force_send=True)
    #         self.ensure_one()
    #         template = self.env.ref('contract_e.approve_quotation_sales_mail_template', False)
    #         mail = self.env['mail.template'].browse(template.id)
    #         mail.send_mail(self.id, force_send=True)
    #     else:
    #         self.ensure_one()      
    #         self.state ='approved'

    @api.multi
    def approved_usage(self):
        if  self.xquotationtrans_discount_usage <= 30:
            self.ensure_one()
            self.state_usage ='approved'
            template = self.env.ref('contract_e.approve_soa_merchant_mail_template', False)
            mail = self.env['mail.template'].browse(template.id)
            mail.send_mail(self.id, force_send=True)
            self.ensure_one()
            template = self.env.ref('contract_e.approve_soa_sales_mail_template', False)
            mail = self.env['mail.template'].browse(template.id)
            mail.send_mail(self.id, force_send=True)          
        else:
            self.ensure_one()      
            self.state_usage ='approved'
    
    @api.multi
    def rejected_usage(self):
        if self.xquotationtrans_reject == False :
           raise ValidationError('The comment rejected contract must be inserted before!')
        if  self.xquotationtrans_discount_usage <= 30:
            self.ensure_one()
            self.state_usage ='rejected'
            # template = self.env.ref('contract_e.reject_soa_mail_template', False)
            # mail = self.env['mail.template'].browse(template.id)
            # mail.send_mail(self.id, force_send=True)
        else:
            self.ensure_one()
            self.state_usage ='rejected'
            # template = self.env.ref('contract_e.final_soa_vp_mail_template', False)
            # mail = self.env['mail.template'].browse(template.id)
            # mail.send_mail(self.id, force_send=True)

    @api.multi
    def final_usage(self):
        # if self.xquotationtrans_tseldelegation_otp_confirmation != self.xquotationtrans_tseldelegation_otp :
        #    raise ValidationError('Please fill in the OTP before Proceeding!')
        if  self.xquotationtrans_discount_usage <= 30:
            self.ensure_one()
            self.state_usage ='final'
            template = self.env.ref('contract_e.final_soa_gm_mail_template', False)
            mail = self.env['mail.template'].browse(template.id)
            mail.send_mail(self.id, force_send=True)
        else:
            self.ensure_one()
            self.state_usage ='final'
            template = self.env.ref('contract_e.final_soa_vp_mail_template', False)
            mail = self.env['mail.template'].browse(template.id)
            mail.send_mail(self.id, force_send=True)

    # State ORDER
    @api.multi
    @api.depends('xquotationtrans_discount')
    def pending_quotation(self):
        if self.xquotationtrans_number_contract_id == False :
            raise ValidationError('The number contract must be inserted before!')
        if self.xquotationtrans_usage_quotation == False :
           raise ValidationError('Choose Quotation Cannot ne null!')
        if self.xquotationtrans_number_quotation == False :
           raise ValidationError('Quotation Number Cannot be null!')        
        if  self.xquotationtrans_discount <= 30:
            self.ensure_one()
            self.state ='pending'
            template = self.env.ref('contract_e.quotation_gm_mail_template', False)
            mail = self.env['mail.template'].browse(template.id)
            mail.send_mail(self.id, force_send=True)
        else:
            self.ensure_one()
            self.state ='pending'
            template = self.env.ref('contract_e.quotation_vp_mail_template', False)
            mail = self.env['mail.template'].browse(template.id)
            mail.send_mail(self.id, force_send=True)

    @api.multi
    def approved_quotation(self):
        if  self.xquotationtrans_discount <= 30:
            self.ensure_one()
            self.state ='approved'
            template = self.env.ref('contract_e.approve_quotation_merchant_mail_template', False)
            mail = self.env['mail.template'].browse(template.id)
            mail.send_mail(self.id, force_send=True)
            self.ensure_one()
            template = self.env.ref('contract_e.approve_quotation_sales_mail_template', False)
            mail = self.env['mail.template'].browse(template.id)
            mail.send_mail(self.id, force_send=True)
        else:
            self.ensure_one()      
            self.state ='approved'

    @api.multi
    def rejected_quotation(self):
        if self.xquotationtrans_reject == False :
           raise ValidationError('The comment rejected contract must be inserted before!')
        if  self.xquotationtrans_discount <= 30:
            self.ensure_one()
            self.state ='rejected'
            # template = self.env.ref('contract_e.reject_quotation_mail_template', False)
            # mail = self.env['mail.template'].browse(template.id)
            # mail.send_mail(self.id, force_send=True)
        else:
            self.ensure_one()      
            self.state ='rejected'  

    @api.multi
    def final_quotation(self):
        # if self.xquotationtrans_tseldelegation_otp_confirmation != self.xquotationtrans_tseldelegation_otp :
        #    raise ValidationError('Please fill in the OTP before Proceeding!')
        if  self.xquotationtrans_discount <= 30:
            self.ensure_one()
            self.state ='final'
            template = self.env.ref('contract_e.final_quotation_gm_mail_template', False)
            mail = self.env['mail.template'].browse(template.id)
            mail.send_mail(self.id, force_send=True)
        else:
            self.ensure_one()
            self.state ='final'
            template = self.env.ref('contract_e.final_quotation_vp_mail_template', False)
            mail = self.env['mail.template'].browse(template.id)
            mail.send_mail(self.id, force_send=True)
   
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
    xquotationtrans_detailinventory_remark = fields.Text(string="Remark")
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