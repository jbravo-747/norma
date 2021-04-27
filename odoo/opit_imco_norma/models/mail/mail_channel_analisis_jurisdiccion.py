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
	#Funcion de control en el flujo para deteccion de la jurisdiccion dada que se tiene el delito
	@api.multi
	def analizar_mensaje_inicial_jurisdiccion(self, message, body):
		#Verifica sl la jurisdiccion (CP o Estado) viene en el mensaje
		jurisdiccion_in_message = message.check_jurisdiccion_in_message(body, tipo_analisis = "estado")
		#Si la jurisdiccion viene en el mensaje
		if jurisdiccion_in_message != False:
			self.save_jurisdiccion(jurisdiccion=jurisdiccion_in_message,message_id=message.id)
			#Revisa si esta definido el delito y la jurisdiccion para el delito
			if self.check_jurisdiccion_definida_en_delito() == True:
				return (self.analizar_conversacion_siguiente_mensaje(message))
			else:
				message.save_contexts_odoo(contextos = [ ("general_fin") ], session_id = self.id)
				self.write({ 'status'  : 'delito_jurisdiccion_no_definida' })
				return self.finaliza_conversacion(finaliza_prematuro = False)
		#Obtenemos la siguiente pregunta (definiendo el contexto asociado a dicha entidad)
		else: 			
			return ("¿En qué estado ocurrió? (Ciudad de Mexico, CDMX, otro)")

	
	
	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	@api.multi
	def save_jurisdiccion(self, jurisdiccion, message_id):
		entidad_ubicacion_id = 	self.env['imco.norma.nltk.entidades'].search([('codigo', '=', 'ubicacion')], limit=1).id
		entidades_vals = []
		pprint.pprint(jurisdiccion)
		if jurisdiccion['tipo_ente']=='cp':
			#Asocia el municipio a las caracteristicas generales de la conversacion
			self.write( { 'cp_id' : jurisdiccion['ente']['cp'].id, 'municipio_id' : jurisdiccion['ente']['municipio'].id } )
			#self.write( { 'municipio_id' : jurisdiccion['ente']['municipio'].id, 'estado_id' : jurisdiccion['ente']['estado'].id } )
			#Asocia las entidades especificas requeridas a la conversacion
			entidad_cp_id = self.env['imco.norma.nltk.entidades'].search([('codigo', '=', 'cp')], limit=1).id
			entidad_municipio_id = self.env['imco.norma.nltk.entidades'].search([('codigo', '=', 'municipio')], limit=1).id
			entidades_vals.append({'channel_id': self.id, 'message_id': message_id, 'entidad_id': entidad_cp_id, 'valor': jurisdiccion['ente']['cp'].name})
			entidades_vals.append({'channel_id': self.id, 'message_id': message_id, 'entidad_id': entidad_municipio_id, 'valor': jurisdiccion['ente']['municipio'].name})
			entidades_vals.append({'channel_id': self.id, 'message_id': message_id, 'entidad_id': entidad_ubicacion_id, 'valor': 'cp:'+str(jurisdiccion['ente']['cp'].cp)})
			entidades_vals.append({'channel_id': self.id, 'message_id': message_id, 'entidad_id': entidad_ubicacion_id, 'valor': 'municipio:'+jurisdiccion['ente']['municipio'].name})
			entidades_vals.append({'channel_id': self.id, 'message_id': message_id, 'entidad_id': entidad_ubicacion_id, 'valor': 'estado:'+jurisdiccion['ente']['estado'].name})
			#Asocia la entidad especifica del municipio a la conversacion
		elif jurisdiccion['tipo_ente']=='municipio':
			#Asocia el municipio a las caracteristicas generales de la conversacion
			self.write( { 'municipio_id' : jurisdiccion['ente']['municipio'].id } )
			#self.write( { 'municipio_id' : jurisdiccion['ente']['municipio'].id, 'estado_id' : jurisdiccion['ente']['estado'].id } )
			#Asocia las entidades especificas requeridas a la conversacion
			entidad_municipio_id = self.env['imco.norma.nltk.entidades'].search([('codigo', '=', 'municipio')], limit=1).id
			entidades_vals.append({'channel_id': self.id, 'message_id': message_id, 'entidad_id': entidad_municipio_id, 'valor': jurisdiccion['ente']['municipio'].name})
			entidades_vals.append({'channel_id': self.id, 'message_id': message_id, 'entidad_id': entidad_ubicacion_id, 'valor': 'municipio:'+jurisdiccion['ente']['municipio'].name})
			entidades_vals.append({'channel_id': self.id, 'message_id': message_id, 'entidad_id': entidad_ubicacion_id, 'valor': 'estado:'+jurisdiccion['ente']['estado'].name})
		elif jurisdiccion['tipo_ente']=='estado':
			#Asocia el estado a las caracteristicas generales de la conversacion
			self.write( { 'estado_id' : jurisdiccion['ente']['estado'].id } )
			#Revisa el estado del delito para saber si no es del fuero federal
			federal = True
			if self.delito_id.id in [False, None]:
				federal = False
			elif self.delito_id.fuero_delito != "federal":
				federal = False
			#Si no es del fuero federal asocia el estado a la conversacion
			if federal == False:
				j = self.env['imco.norma.jurisdiccion'].search([('tipo_jurisdiccion', '=','estatal'),('estado_id','=', jurisdiccion['ente']['estado'].id)], limit=1)
				if j.id not in [False, None]:
					self.write({'jurisdiccion_id' : j.id})
				else:
					j = self.env['imco.norma.jurisdiccion'].search([('tipo_jurisdiccion', '=','sin_definir')], limit=1)
					self.write({'jurisdiccion_id' : j.id})
			#Asocia las entidades especificas requeridas a la conversacion
			entidades_vals.append({'channel_id': self.id, 'message_id': message_id, 'entidad_id': entidad_ubicacion_id, 'valor': 'estado:'+jurisdiccion['ente']['estado'].name})
		#Asocia las entidades requeridas en la conversacion
		for vals in entidades_vals:
			analisis_entidad = self.env['imco.norma.mail.analisis.nltk.entidades'].create(vals)
		

