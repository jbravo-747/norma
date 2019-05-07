# -*- coding: 850 -*-
from datetime import datetime, timedelta, date
from pytz import timezone
from openerp import SUPERUSER_ID
from openerp import api, fields, models, _
import openerp.addons.decimal_precision as dp
from openerp.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import except_orm, Warning, RedirectWarning, UserError
from dateutil.parser import parse as parse_date
import random
import re
import json
import pprint


#action_delito_robo_circunstancias_testigo
#action_delito_robo_circunstancias_camara


class imco_norma_delitos_jurisdiccion_entidades_requeridas(models.Model):
	_inherit = "imco.norma.delitos.jurisdiccion.entidades.requeridas"

	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	def action_delito_robo_circunstancias_testigo(self, body, session_id, channel=None, message=None):
		analisis = self.analisis_mensaje_dialogflow_manejo_unknown( \
			text = body, session_id = session_id, message = message, context = "entidad_testigo") 
		vals = []
		#print(analisis)
		if "binario" in analisis["entidades"]:
			for a in analisis["entidades"]["binario"]:
				if a == "no":
					analisis["entidades"] = { "testigo" : ["no"] }
					return analisis
				else:
					vals = ["si"]
		elif "number" in analisis["entidades"]:
			vals = ["si"]
		analisis["entidades"] = { "testigo" : vals }
		return analisis
		
	
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	def action_delito_robo_circunstancias_camara(self, body, session_id, channel=None, message=None):
		analisis = self.analisis_mensaje_dialogflow_manejo_unknown( \
			text = body, session_id = session_id, message = message, context = "entidad_camara") 
		vals = []
		#print(analisis)
		if "binario" in analisis["entidades"]:
			for a in analisis["entidades"]["binario"]:
				if a == "no":
					analisis["entidades"] = { "testigo" : ["no"] }
					return analisis
				else:
					vals = ["si"]
		elif "number" in analisis["entidades"]:
			vals = ["si"]
		analisis["entidades"] = { "camara" : vals }
		return analisis
		
		
	