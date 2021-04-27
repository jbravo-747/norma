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


#action_delito_robo_perfil_genero
#action_delito_robo_perfil_edad
#action_delito_robo_perfil_repartidor
#action_delito_robo_perfil_discapacidad

class imco_norma_delitos_jurisdiccion_entidades_requeridas(models.Model):
	_inherit = "imco.norma.delitos.jurisdiccion.entidades.requeridas"

	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	def action_delito_robo_perfil_genero(self, body, session_id, channel=None, message=None):
		analisis = self.analisis_mensaje_dialogflow_manejo_unknown( \
			text = body, session_id = session_id, message = message, context = "entidad_genero") 
		vals = []
		if "genero" in analisis["entidades"]:
			for x in analisis["entidades"]["genero"]:
				r = self.search_text_in_entidades_alias( text = x, codigo = "objeto")
				if r != False and r not in vals:
					vals.append(r)
		analisis["entidades"] = {
			"genero" :  vals
			}
		return analisis

	
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	def action_delito_robo_perfil_edad(self, body, session_id, channel=None, message=None):
		vals = []
		v = re.sub(r'[^a-zA-Z0-9\.\s]+', '', body) 
		#Si son valores diferentes, entonces asumimos que trae texto, por lo que mandamos a dialog flow para que intente traducirlo
		if v !=  re.sub(r'[0-9]+', '', v) :
			analisis = self.analisis_mensaje_dialogflow_manejo_unknown( \
				text = body, session_id = session_id, message = message, context = "entidad_edad") 
			if "edad" in analisis["entidades"]:
				for a in analisis["entidades"]["edad"]:
					r = self.search_text_in_entidades_alias( text = a, codigo = "edad")
					if r != False and r not in vals:
						vals.append(r)
			if len(vals) == 0:
				v = v.split(" ")
				for vv in v:
					vv = vv.strip()
					if vv ==  re.sub(r'[^0-9]+', '', vv) :
						try:
							edad = float(vv)
							if edad < 18:
								edad_str = "menor_edad"
							elif edad >= 18 and edad <= 59:
								edad_str = "adulto"
							else:
								edad_str = "tercera_edad"		
							vals.append(edad_str)
						except:
							pass
			analisis["entidades"] = {
				"edad" :  vals
				}
		#Si son los mismos valores, entonces el texto recibido es un numero
		else:
			analisis = {
				"action" : "",
				"entidades" : {}
				}
			v = v.split(" ")[0]
			v = v.replace("años","").replace("anos","").replace("anios","")
			try:
				edad = float(v)
				if edad < 18:
					edad_str = "menor_edad"
				elif edad >= 18 and edad <= 59:
					edad_str = "adulto"
				else:
					edad_str = "tercera_edad"		
				analisis["entidades"]["edad"] = [edad_str]
			except:
				pass
		return analisis	
		

	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	def action_delito_robo_perfil_repartidor(self, body, session_id, channel=None, message=None):
		analisis = self.analisis_mensaje_dialogflow_manejo_unknown(\
			text = body, session_id = session_id, message = message, context = "entidad_repartidor") 
		vals = []
		if "binario" in analisis["entidades"]:
			#Al ser binario asume el primer valor unicamente
			if analisis["entidades"]["binario"][0] == "si":
				vals = ["si"]
			elif analisis["entidades"]["binario"][0] == "no":
				vals = ["no" ]
			analisis["entidades"].pop('binario', None)
		elif "repartidor" in analisis["entidades"]:
			vals = ["si" ]
		elif "ambito" in analisis["entidades"]:
			for a in analisis["entidades"]["ambito"]:
				r = self.search_text_in_entidades_alias( text = a, codigo = "ambito")
				if r == "trabajo":
					vals = ["si" ]
					break
		if len(vals) > 0:
			analisis["entidades"] = {
				"repartidor" : vals
				}
		else:
			analisis["entidades"] = {}
		return analisis	

	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	def action_delito_robo_perfil_discapacidad(self, body, session_id, channel=None, message=None):
		analisis = self.analisis_mensaje_dialogflow_manejo_unknown(\
			text = body, session_id = session_id, message = message, context = "entidad_discapacidad") 
		vals = []
		if "binario" in analisis["entidades"]:
			#Al ser binario asume el primer valor unicamente
			if analisis["entidades"]["binario"][0] == "si":
				vals = ["si"]
			elif analisis["entidades"]["binario"][0] == "no":
				vals = ["no" ]
			analisis["entidades"].pop('binario', None)
		elif "discapacidad" in analisis["entidades"]:
			vals = ["si" ]
		else:
			vals = ["no" ]
		if len(vals) > 0:
			analisis["entidades"] = {
				"discapacidad" : vals
				}
		else:
			analisis["entidades"] = {}
		return analisis

		