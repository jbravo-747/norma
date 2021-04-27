# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, date
from pytz import timezone
from openerp import SUPERUSER_ID
from openerp import api, fields, models, _
import openerp.addons.decimal_precision as dp
from openerp.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import except_orm, Warning, RedirectWarning, UserError
from dateutil.parser import parse as parse_date
import random
import sys, traceback
import logging
import pprint

_logger = logging.getLogger(__name__)

class MailChannel(models.Model):
	_inherit = ['mail.channel']

	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	@api.multi
	def check_channel_solicita_finalizacion(self, message, body): 
		return (True if "fin" in body else False) 

		
	@api.multi
	def finaliza_conversacion(self, finaliza_prematuro = False):  
		recomendacion = self.obtiene_recomendacion_conversacion()
		recomendacion += "\nPuedes consultar tu recomendación personalizada aqui: " + self.url_recomendacion
		#print (recomendacion)
		if finaliza_prematuro == True:
			self.write( {"status":"finalizado_prematuro", "finalizado_prematuro" : True} )
		return (";;;fin;;;" + recomendacion)
