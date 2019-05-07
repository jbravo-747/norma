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


#action_delito_robo_tiempo_hora
#action_delito_robo_tiempo_clima

class imco_norma_delitos_jurisdiccion_entidades_requeridas(models.Model):
	_inherit = "imco.norma.delitos.jurisdiccion.entidades.requeridas"

	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	def action_delito_robo_tiempo_hora(self, body, session_id, channel=None, message=None):
		vals = []
		v = re.sub(r'[^a-zA-Z0-9\s]+', '', body) 
		print(body, v, v !=  re.sub(r'[^0-9]+', '', v) )
		#Si son valores diferentes, entonces asumimos que trae texto, por lo que mandamos a dialog flow para que intente traducirlo
		if v !=  re.sub(r'[^0-9]+', '', v) :
			analisis = self.analisis_mensaje_dialogflow_manejo_unknown( \
				text = body, session_id = session_id, message = message, context = "entidad_hora") 
			print (analisis["entidades"])
			if "time" in analisis["entidades"]:
				try:
					vals = [":".join(analisis["entidades"]["time"][0].split("t")[1].split(":")[:2])]
				except:
					pass
			analisis["entidades"] = {
				"hora" :  vals
				}
		#Si son los mismos valores, entonces el texto recibido es un numero
		else:
			analisis = {
				"action" : "",
				"entidades" : {}
				}
			v = v.split(" ")[0].strip()
			try:
				if len(v) <= 2 :
					v_str = v[0] + v[1] + ":00"
				elif len(v) > 2 and len(v) <= 4:
					v_str = v[0] + v[1] + ":" + v[2] + v[3]
					v = v[0] + v[1]
				else:
					#Si son mas de 4 numeros entonces seguro no es una hora valida, por lo que se debe terminar sin asociar nada
					v_str = v
					v  = "1000"
				hora = float(v)
				if hora >= 0 and  hora <= 24:
					analisis["entidades"]["hora"] = [v_str]
			except:
				pass
		return analisis	
		
	
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	def action_delito_robo_tiempo_clima(self, body, session_id, channel=None, message=None):
		analisis = self.analisis_mensaje_dialogflow_manejo_unknown(\
			text = body, session_id = session_id, message = message, context = "entidad_clima") 
		vals = []
		if "clima" in analisis["entidades"]:
			for x in analisis["entidades"]["clima"]:
				r = self.search_text_in_entidades_alias( text = x, codigo = "clima")
				if r != False and r not in vals:
					vals.append(r)
		analisis["entidades"]["clima"] = vals
		return analisis	
		
		
	