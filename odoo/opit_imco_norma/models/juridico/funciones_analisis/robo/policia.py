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


#action_delito_robo_policia_policia
#action_delito_robo_policia_tiempo
#action_delito_robo_policia_entrevista
#action_delito_robo_policia_cadena

class imco_norma_delitos_jurisdiccion_entidades_requeridas(models.Model):
	_inherit = "imco.norma.delitos.jurisdiccion.entidades.requeridas"

	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	def action_delito_robo_policia_policia(self, body, session_id, channel=None, message=None):
		analisis = self.analisis_mensaje_dialogflow_manejo_unknown( \
			text = body, session_id = session_id, message = message, context = "entidad_policia") 
		vals = []
		if "binario" in analisis["entidades"]:
			for a in analisis["entidades"]["binario"]:
				if a == "no":
					analisis["entidades"] = { 
						"policia" : ["no"],
						"tiempo-respuesta" : ["no"],
						"entrevista-testigo" : ["no"],
						"cadena-custodia" : ["no"],
						}
					return analisis
				else:
					vals = ["si"]
		elif "number" in analisis["entidades"]:
			vals = ["si"]
		analisis["entidades"] = { "policia" : vals }
		return analisis
		
		
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	def action_delito_robo_policia_tiempo(self, body, session_id, channel=None, message=None):
		vals = []
		analisis = self.analisis_mensaje_dialogflow_manejo_unknown(\
			text = body, session_id = session_id, message = message, context = "entidad_tiempo-respuesta") 
		if "binario" in analisis["entidades"]:
			for a in analisis["entidades"]["binario"]:
				if a == "no":
					analisis["entidades"] = { "tiempo-respuesta" : ["no"] }
					return analisis
			analisis["entidades"] = { "tiempo-respuesta" : ["si"] }
		if "number" in analisis["entidades"]:
			if type(analisis["entidades"]["number"][0]) in [str]:
				try:
					valor  = float(analisis["entidades"]["number"][0])
					if valor < 10:
						analisis["entidades"] = {"tiempo-respuesta" :  ["rapido"] }
					if valor >=  11 and valor <= 25:
						analisis["entidades"] = { "tiempo-respuesta" : ["medio"] }
					if valor >  25 and valor <= 60:
						analisis["entidades"] = { "tiempo-respuesta" : ["lento"] }
					else:
						analisis["entidades"] = { "tiempo-respuesta" : ["muy_lento"] }
				except:
					analisis["entidades"] = {}
			elif type(analisis["entidades"]["number"][0]) in [int, float]:
				try:
					valor  = analisis["entidades"]["number"][0]
					if valor < 10:
						analisis["entidades"] = {"tiempo-respuesta" :  ["rapido"] }
					if valor >=  11 and valor <= 25:
						analisis["entidades"] = { "tiempo-respuesta" : ["medio"] }
					if valor >  25 and valor <= 60:
						analisis["entidades"] = { "tiempo-respuesta" : ["lento"] }
					else:
						analisis["entidades"] = { "tiempo-respuesta" : ["muy_lento"] }
				except:
					analisis["entidades"] = {}
			else:
				analisis["entidades"] = {}
		return analisis	
		
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	def action_delito_robo_policia_entrevista(self, body, session_id, channel=None, message=None):
		analisis = self.analisis_mensaje_dialogflow_manejo_unknown( \
			text = body, session_id = session_id, message = message, context = "entidad_entrevista-testigo") 
		vals = []
		if "binario" in analisis["entidades"]:
			for a in analisis["entidades"]["binario"]:
				if a == "no":
					analisis["entidades"] = { "entrevista-testigo" : ["no"] }
					return analisis
				else:
					vals = ["si"]
		elif "number" in analisis["entidades"]:
			vals = ["si"]
		analisis["entidades"] = { "entrevista-testigo" : vals }
		return analisis
		
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	def action_delito_robo_policia_cadena(self, body, session_id, channel=None, message=None):
		analisis = self.analisis_mensaje_dialogflow_manejo_unknown( \
			text = body, session_id = session_id, message = message, context = "entidad_cadena-custodia") 
		vals = []
		#print(analisis)
		if "binario" in analisis["entidades"]:
			for a in analisis["entidades"]["binario"]:
				if a == "no":
					analisis["entidades"] = { "cadena-custodia" : ["no"] }
					return analisis
				else:
					vals = ["si"]
		analisis["entidades"] = { "cadena-custodia" : vals }
		return analisis	
		
	
		
	