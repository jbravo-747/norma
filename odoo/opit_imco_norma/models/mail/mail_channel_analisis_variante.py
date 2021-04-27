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
	def identifica_variante_delito_en_jurisdiccion(self):
		res = False
		#print("xxxx" * 20)
		#Itera sobre las variaciones del delito-jurisdiccion detectado en la conversacion
		for variante in self.delito_jurisdiccion_id.variantes_ids:
			#print("++++" * 20)
			print ("Variante:" , variante.name)
			res_local_variante = True
			#Itera sobre las entidades requeridas para la variante
			#Filtra aquellas entidades que tengan una variable en su formula (las otras entidades son dummies)
			for en_in_variante in variante.variantes_entidades_ids.filtered(lambda r: '$x' in r.valor ):
				#print("----" * 20)
				#print ("Entidad en variante:", en_in_variante.entidad_id.name, '[', en_in_variante.valor, ']' )
				res_local_entidad = False
				# Itera sobre las entidades detectadas en la conversacion de la misma entidad que la requerida por la variante
				for en_in_msg in self.messages_analisis_entidades_ids.filtered(lambda r :  r.entidad_id.id == en_in_variante.entidad_id.id):
					#print("---" * 5)
					#print ("Entidad en conversacion: ", en_in_msg.entidad_id.name, '[', en_in_msg.valor, ']' )
					exp = en_in_variante.valor.replace('$x', en_in_msg.valor)
					#print ("Expresion a evaluar", ";;;;;", exp)
					try:
						ev =  eval(exp)
						#print (ev)
					except:
						ev = False
						traceback.print_exc(file=sys.stdout)
					if ev == True:
						res_local_entidad = True
						#break
				print('La entidad de la conversacion aplica?:', res_local_entidad)
				if res_local_entidad == False:
					res_local_variante = False
					break
			print('La variante del delito aplica?:', res_local_variante)
			#print("++++" * 20)
			if res_local_variante == True:
				res = variante
				break
		if res != False:
			self.save_variante(v)
		return res


	#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
	#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	@api.multi
	def save_variante(self, variante):
		self.write({
			#'status' : 'finalizado_exitoso',
			'delito_id' : variante.delito_jurisdiccion_id.delito_id.id,
			'jurisdiccion_id' : variante.delito_jurisdiccion_id.jurisdiccion_id.id,
			'delito_jurisdiccion_id' : variante.delito_jurisdiccion_id.id,
			'variante_id' : variante.id,
			})
