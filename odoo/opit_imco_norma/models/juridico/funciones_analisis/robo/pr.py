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


#action_delito_robo_pr_numero
#action_delito_robo_pr_arma
#action_delito_robo_pr_violencia
#action_delito_robo_pr_pr


class imco_norma_delitos_jurisdiccion_entidades_requeridas(models.Model):
	_inherit = "imco.norma.delitos.jurisdiccion.entidades.requeridas"

	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	def action_delito_robo_pr_numero(self, body, session_id, channel=None, message=None):
		vals = []
		v = re.sub(r'[^a-zA-Z0-9\.]+', '', body) 
		#Si son valores diferentes, entonces asumimos que trae texto, por lo que mandamos a dialog flow para que intente traducirlo
		if v !=  re.sub(r'[a-zA-Z]+', '', v) :
			analisis = self.analisis_mensaje_dialogflow_manejo_unknown( \
				text = body, session_id = session_id, message = message, context = "entidad_numero-personas") 
			if "number" in analisis["entidades"]:
				if type(analisis["entidades"]["number"][0]) in [str]:
					try:
						analisis["entidades"]["numero-personas"] = [str(float(analisis["entidades"]["number"][0]))]
					except:
						analisis["entidades"] = {}
				elif type(analisis["entidades"]["number"][0]) in [int, float]:
					analisis["entidades"]["numero-personas"] = [str(analisis["entidades"]["number"][0])]
				else:
					analisis["entidades"] = {}
		#Si son los mismos valores, entonces el texto recibido es un numero
		else:
			analisis = {
				"action" : "",
				"entidades" : {
					"numero-personas" : [str(v)]
					}
				}
		return analisis	
		
	
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	def action_delito_robo_pr_arma(self, body, session_id, channel=None, message=None):
		analisis = self.analisis_mensaje_dialogflow_manejo_unknown(\
			text = body, session_id = session_id, message = message, context = "entidad_arma") 
		vals = []
		if "binario" in analisis["entidades"]:
			#Al ser binario asume el primer valor unicamente
			if analisis["entidades"]["binario"][0] == "si":
				vals = ["si"]
			elif analisis["entidades"]["binario"][0] == "no":
				vals = ["no" ]
		if "arma" in analisis["entidades"]:
			for a in analisis["entidades"]["arma"]:
				r = self.search_text_in_entidades_alias( text = a, codigo = "arma")
				if r == "no":
					vals = ['no']
					break
				if r != False and r not in vals:
					if "si" not in vals:
						vals.append("si")
					vals.append(r)
		analisis["entidades"] = { "arma" : vals }
		return analisis
		

	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	def action_delito_robo_pr_violencia(self, body, session_id, channel=None, message=None):
		analisis = self.analisis_mensaje_dialogflow_manejo_unknown( \
			text = body, session_id = session_id, message = message, context = "entidad_violencia") 
		vals = []
		#print(analisis)
		if "binario" in analisis["entidades"]:
			#Al ser binario asume el primer valor unicamente
			if analisis["entidades"]["binario"][0] == "si":
				vals = ["si"]
			elif analisis["entidades"]["binario"][0] == "no":
				vals = ["no" ]
			analisis["entidades"].pop('binario', None)
		if "violencia" in analisis["entidades"]:
			for a in analisis["entidades"]["violencia"]:
				if a == "violencia_fisica":
					analisis["entidades"] = { "violencia" : [ "si", "violencia_fisica"] }
					return analisis
				elif a == "violencia_moral":
					analisis["entidades"] = { "violencia" : [ "si", "violencia_moral"] }
					return analisis
				else:
					r = self.search_text_in_entidades_alias( text = a, codigo = "violencia")
					if r != False and r not in vals and r != "no":
						if "si" not in vals:
							vals.append("si")
						vals.append(r)
		analisis["entidades"] = { "violencia" : vals }
		return analisis
		
	
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	def action_delito_robo_pr_pr(self, body, session_id, channel=None, message=None):
		analisis = self.analisis_mensaje_dialogflow_manejo_unknown( \
			text = body, session_id = session_id, message = message, context = "entidad_identidad-pr") 
		vals = []
		#print(analisis)
		if "binario" in analisis["entidades"]:
			for a in analisis["entidades"]["binario"]:
				if a == "no":
					vals = ["no" ]
					break
				else:
					vals = ["si"]
				
		analisis["entidades"] = { "identidad-pr" : vals }
		return analisis
		
	