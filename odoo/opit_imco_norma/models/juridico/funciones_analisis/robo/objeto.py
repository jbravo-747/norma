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


#action_delito_robo_objeto_objeto
#action_delito_robo_objeto_monto

class imco_norma_delitos_jurisdiccion_entidades_requeridas(models.Model):
	_inherit = "imco.norma.delitos.jurisdiccion.entidades.requeridas"

	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	def action_delito_robo_objeto_objeto(self, body, session_id, channel=None, message=None):
		analisis = self.analisis_mensaje_dialogflow_manejo_unknown(\
			text = body, session_id = session_id, message = message, context = "entidad_objeto") 
		vals = []
		if "objeto" in analisis["entidades"]:
			for x in analisis["entidades"]["objeto"]:
				r = self.search_text_in_entidades_alias( text = x, codigo = "objeto")
				if r != False and r not in vals:
					vals.append(r)
		analisis["entidades"]["objeto"] = vals
		return analisis	
		
	
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	def action_delito_robo_objeto_monto(self, body, session_id, channel=None, message=None):
		vals = []
		v = re.sub(r'[^a-zA-Z0-9\.]+', '', body) 
		#Si son valores diferentes, entonces asumimos que trae texto, por lo que mandamos a dialog flow para que intente traducirlo
		if v !=  re.sub(r'[a-zA-Z]+', '', v) :
			analisis = self.analisis_mensaje_dialogflow_manejo_unknown(\
				text = body, session_id = session_id, message = message, context = "entidad_monto") 
			if "number" in analisis["entidades"]:
				if type(analisis["entidades"]["number"][0]) in [str]:
					try:
						valor  = float(analisis["entidades"]["number"][0])
						if valor < 24189:
							analisis["entidades"] = {"monto" :  ["monto_bajo"] }
						if valor >=  24189 and valor <= 60450:
							analisis["entidades"] = { "monto" : ["monto_medio"] }
						else:
							analisis["entidades"] = { "monto" : ["monto_alto"] }
					except:
						analisis["entidades"] = {}
				elif type(analisis["entidades"]["number"][0]) in [int, float]:
					try:
						valor  = analisis["entidades"]["number"][0]
						if valor < 24189:
							analisis["entidades"] = {"monto" :  ["monto_bajo"] }
						if valor >=  24189 and valor <= 60450:
							analisis["entidades"] = { "monto" : ["monto_medio"] }
						else:
							analisis["entidades"] = { "monto" : ["monto_alto"] }
					except:
						analisis["entidades"] = {}
				else:
					analisis["entidades"] = {}
		#Si son los mismos valores, entonces el texto recibido es un numero
		else:
			analisis = {
				"action" : "",
				"entidades" : {}
				}
			try:
				valor  = float(body)
				if valor < 24189:
					analisis["entidades"] = {"monto" :  ["monto_bajo"] }
				if valor >=  24189 and valor <= 60450:
					analisis["entidades"] = { "monto" : ["monto_medio"] }
				else:
					analisis["entidades"] = { "monto" : ["monto_alto"] }
			except:
				analisis["entidades"] = {}
		return analisis	
		
		
	