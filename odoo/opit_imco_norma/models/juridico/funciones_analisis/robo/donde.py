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


#action_delito_robo_donde_municipio
#action_delito_robo_donde_lugar

class imco_norma_delitos_jurisdiccion_entidades_requeridas(models.Model):
	_inherit = "imco.norma.delitos.jurisdiccion.entidades.requeridas"

	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	def action_delito_robo_donde_cp(self, body, session_id, channel=None, message=None):
		cp = message.check_jurisdiccion_in_message(body, tipo_analisis = "cp", estado_id = channel.estado_id.id)
		analisis = {
			"action" : "action_delito_robo_donde_cp",
			"entidades" : {}
			}
		if cp != False:
			#channel.write( { 'municipio_id' : municipio['ente']['municipio'].id} )
			channel.save_jurisdiccion(jurisdiccion=cp,message_id=message.id)
			analisis["entidades"]["cp"] = [cp["ente"]["cp"].name]
		return analisis	
		
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	def action_delito_robo_donde_municipio(self, body, session_id, channel=None, message=None):
		municipio = message.check_jurisdiccion_in_message(body, tipo_analisis = "municipio", estado_id = channel.estado_id.id)
		analisis = {
			"action" : "action_delito_robo_donde_municipio",
			"entidades" : {}
			}
		if municipio != False:
			#channel.write( { 'municipio_id' : municipio['ente']['municipio'].id} )
			channel.save_jurisdiccion(jurisdiccion=municipio,message_id=message.id)
			analisis["entidades"]["municipio"] = [municipio["ente"]["municipio"].name]
		return analisis	
		
	
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------
	def action_delito_robo_donde_lugar(self, body, session_id, channel=None, message=None):
		analisis = self.analisis_mensaje_dialogflow_manejo_unknown(text = body, session_id = session_id, message = message, context = "entidad_lugar") 
		vals = []
		if "lugar" in analisis["entidades"]:
			for x in analisis["entidades"]["lugar"]:
				r = self.search_text_in_entidades_alias( text = x, codigo = "lugar")
				if r != False and r not in vals:
					vals.append(r)
		analisis["entidades"]["lugar"] = vals
		return analisis	
		
		
	