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
	#Funcion inicial para analisis del mensaje
	@api.multi
	def analizar_mensaje_flujo_delito(self, message=None,body=''):
		print(message)
		#Verifica si se ha cerrado la sesion previamente (ya no debe hacer nada)
		if self.sesion_cerrada != True:
			#Verifica si la conversacion ha finalizado previamente 
			if self.check_channel_finalizado() == True:
				#Manda llamar la funcion que debera determinar si manda informacion por correo
				#Tambien debe cerrar la conversacion
				#Funcion en archivo: mail_channel_envio_informacion.py
				return self.analizar_envio_informacion(message, body)
			else:
				#Verifica si el usuario quiere terminar la conversacion
				#Funcion en archivo: mail_channel_revisa_finalizacion.py
				if self.check_channel_solicita_finalizacion(message, body) == True:
					return self.finaliza_conversacion(finaliza_prematuro = True)
				else:
					# Revisas si tienes el delito guardado en la relacion de Entidades
					# En caso negativo mandamos ejecutar la deteccion del delito:
					if self.check_delito_in_channel() == False:
						return self.analizar_mensaje_inicial_delito(message, body)
					# Si ya tenemos registrado el delito, entonces revisamos si a tenemos la jurisdiccion
					#En caso negativo mandamos ejecutar la deteccion de la jurisdiccion
					elif self.check_jurisdiccion_in_channel() == False:
						return self.analizar_mensaje_inicial_jurisdiccion(message, body)
					#Si ya tenemos el delito y la jurisdiccion, entonces mandamos ejecutar el analisis de sus entidades requeridas
					else:
						return self.analizar_mensaje_inicial_entidades_requeridas(message, body)
		else:
			return ("La conversacion ha finalizado, favor de iniciar otra conversacion si requieres de mas ayuda")

	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	#Funciones generales
	@api.multi
	def check_sesion_cerrada(self):
		return (True if self.sesion_cerrada == True else False)
		
	@api.multi
	def check_channel_finalizado(self):
		#return (True if self.status in ["finalizado_exitoso", "finalizado_prematuro", "sesion_cerrada"] else False)
		states_finalizado = [ 'delito_no_definido', 'delito_no_asesoria', 'delito_canalizacion', 'delito_jurisdiccion_no_definida', 
			'variante_sin_definir', 'finalizado_prematuro', 'finalizado_exitoso', 'abandonado']
		return (True if self.status in states_finalizado else False)
	
	
	@api.multi
	def check_delito_in_channel(self):
		return (True if self.delito_id.id not in [False, None] else False)

	@api.multi
	def check_delito_asesoria_in_channel(self):
		if self.delito_id.id not in [False, None] :
			return (True if self.delito_id.asesoria not in [False, None] else False)
		else :
			return False
			
	@api.multi
	def check_delito_canalizacion_in_channel(self):
		if self.delito_id.id not in [False, None] :
			return (True if self.delito_id.canalizacion not in [False, None] else False)
		else:
			return False

	@api.multi
	def check_jurisdiccion_in_channel(self):
		return (True if self.jurisdiccion_id.id not in [False, None] else False)

	@api.multi
	def check_delito_jurisdiccion_in_channel(self):
		return (True if self.delito_jurisdiccion_id.id not in [False, None] else False)

	@api.multi
	def check_variante_in_channel(self):
		return (True if self.variante_id.id not in [False, None] else False)

	@api.multi
	def check_jurisdiccion_definida_en_delito(self):
		j = self.env['imco.norma.delitos.jurisdiccion'].search([('delito_id', '=',self.delito_id.id),('jurisdiccion_id','=', self.jurisdiccion_id.id)], limit=1)
		res = False if j.id in [False, None] else True
		return res

	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	#Funcion para obtener la recomendacion general
	@api.multi
	def obtiene_recomendacion_conversacion(self):
		#Verifica si el delito esta definido
		if self.check_delito_in_channel() == True:
			#Verifica si se le da asesoria al delito
			if self.check_delito_asesoria_in_channel() == True:
				#Verifica si la jurisdiccion esta definida
				if self.check_jurisdiccion_in_channel() == True:
					#Verifica si la jurisdiccion esta definida para el delito seleccionado
					if self.check_jurisdiccion_definida_en_delito() == True:
						#Verifica si esta definida la variante del delito
						if self.check_variante_in_channel() == True:
							return self.variante_id.recomendacion
						else:
							return self.delito_jurisdiccion_id.recomendacion_sin_variante
					#Si no esta definida la jurisdiccion para el delito de la conversacion, 
					#entonces regresa el mensaje predefinido para el delito con recomendacion generica
					else:
						return self.delito_id.mensaje_jurisdiccion_no_aplica
				#Si no esta definida la jurisdiccion en la conversacion, 
				#entonces regresa el mensaje predefinido para el delito con recomendacion generica
				else:
					return self.delito_id.mensaje_jurisdiccion_no_aplica
			#Si no se le da asesoria al delito, entonces verifica se se canaliza o no
			else:
				#Si se canaliza el delito, regresa el mensaje predefinido de canalizacion
				if self.check_delito_canalizacion_in_channel() == True:
					return self.delito_id.mensaje_canalizacion
				#Si no se canaliza, regresa el mensaje predefinido de no asesoria
				else:
					return self.delito_id.mensaje_no_asesoria
		#Si el delito no esta definido, entonces regresa un mensaje generico
		else:
			return ("Lo siento, no pudimos detectar el delito del que fuiste victima, por lo que no te puedo dar una recomendacion")
	
	