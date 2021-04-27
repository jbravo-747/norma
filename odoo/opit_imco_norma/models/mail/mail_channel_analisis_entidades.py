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
	#Funcion de control en el flujo para deteccion de entidades requeridas del delito - jurisdiccion
	@api.multi
	def analizar_mensaje_inicial_entidades_requeridas(self, message, body):
		contextos_entidades = self.messages_analisis_contextos_ids.filtered(lambda a: a.valor.startswith('entidad_')).sorted(key="date")
		#Revisamos si tenemos contextos de la forma "entidad_xxx":
		if(len(contextos_entidades) > 0):
			#Obtenemos el contexto "entidad_xxx" mas reciente (ultima pregunta realizada)
			ultimo_contexto = contextos_entidades[-1].valor.split("_")[1]
			#Obtenemos la entidad asociada al ultimo contexto existente (el tipo de la entidad no puede ser previo - delito y jurisdiccion)
			sql = " SELECT d.id FROM  imco_norma_nltk_entidades e, imco_norma_delitos_jurisdiccion_entidades_requeridas d "
			sql += " WHERE e.codigo = %s AND e.id = d.entidad_id AND d.tipo_analisis != 'previo' LIMIT 1;"
			self.env.cr.execute(sql, (ultimo_contexto,))
			entidad_recibida_id = self.env.cr.fetchone()[0]
			entidad_recibida = self.env['imco.norma.delitos.jurisdiccion.entidades.requeridas'].browse([entidad_recibida_id])
			analisis_func = getattr(entidad_recibida, entidad_recibida.funcion_analisis_interno)
			analisis = analisis_func(body = body, session_id = self.id, channel=self, message = message)
			message.write({'analisis_entidades' : analisis, "intent_action" : analisis["action"]})
			#Antes requeriamos de etender la respuesta, ahora ya no (para no trabar la conversacion)
			entidad_in_message = [analisis["entidades"][key] for key in analisis['entidades'] if key == ultimo_contexto and analisis["entidades"][key] != [] ]
			#Para cada entidad detectada en el mensaje guardamos la relacion de la entidad con su valor
			entidades_ok = message.save_entities(entidades = analisis['entidades'], session_id = self.id) 				
			#Obtenemos la siguiente pregunta
			return self.analizar_conversacion_siguiente_mensaje(message)										
		#En caso negativo obtenemos el siguiente mensaje
		else:
			return self.analizar_conversacion_siguiente_mensaje(message)

	