# -*- coding: utf-8 -*-
import pytz
import logging
from datetime import datetime, timedelta
from openerp import SUPERUSER_ID
from openerp import api, fields, models, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import UserError
from openerp.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT


class res_users(models.Model):
	_inherit = 'res.users'
	
	codigo_chat = fields.Char(string='Codigo para chat')
	
