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
	#Funcion de control en el flujo para deteccion de delito
	@api.multi
	def analizar_mensaje_inicial_delito(self, message, body):
		#Mandamos a analizar el mensaje que recibimos a DF:
		analisis = message.analisis_dialogflow(text=body, session_id=self.id) 						
		#Guardamos resultado de analisis de DF en ODOO.
		message.write({'analisis_entidades' : analisis, "intent_action" : analisis["action"]}) 				
		#Si es un mensaje de bienvenida, entoncesregresa mensaje predefinido de DF de bienvenida
		if analisis["action"] in ["input.welcome"]:
			message.save_contexts_odoo(contextos = [ ("general_inicio") ], session_id = self.id)
			return (analisis["dialogflow_response"].query_result.fulfillment_text)
		#Si es un mensaje de despedida, entonces finaliza la conversacion y regresa mensajes para envio de transcripcion
		elif analisis["action"] in ["input.bye"]:
			message.save_contexts_odoo(contextos = [ ("general_fin") ], session_id = self.id)
			return self.finaliza_conversacion()
		else:
			#Para cada entidad detectada en el mensaje inicial guardamos la relacion de la entidad con su valor
			entidades_ok = message.save_entities(entidades = analisis['entidades'], session_id = self.id) 	
			#Revisa si el delito viene en el mensaje
			delito_in_message = [analisis["entidades"][key] for key in analisis['entidades'] if key == 'delito' and analisis["entidades"][key] != [] ]
			#Si el delito viene en el mensaje, entonces analizamos el delito
			if delito_in_message:																
				#Revisamos si el codigo del delito esta especiificado en los delitos que se atenderan
				delito = self.env["imco.norma.delitos"].search([('codigo', 'in', delito_in_message[0])], limit=1)	 
				#En caso de que el delito este definido en el sistema
				if delito.id not in [False, None]: 													
					#Asociamos el delito a la conversacion
					self.write({"delito_id" : delito.id})												
					message.save_context_delito(llave = delito.codigo, session_id = self.id)
					#Revisamos si el delito es del fuero comun
					if delito.fuero_delito == "federal":												
						j = self.env['imco.norma.jurisdiccion'].search([('tipo_jurisdiccion', '=','federal')], limit=1)
						#Asociamos la jurisdiccion a la conversacion
						self.write({"jurisdiccion_id" : j.id})											
					#Revisa si se brinda asesoria para el delito asociado
					if delito.asesoria == True:													
						#Verifica sl la jurisdiccion (Estado) esta definida en la conversacion
						if self.check_jurisdiccion_in_channel() == True:
							#Revisa si esta definido el delito y la jurisdiccion para el delito
							if self.check_jurisdiccion_definida_en_delito() == True:
								return (self.analizar_conversacion_siguiente_mensaje(message))
							else:
								message.save_contexts_odoo(contextos = [ ("general_fin") ], session_id = self.id)
								self.write({ 'status'  : 'delito_jurisdiccion_no_definida' })
								return self.finaliza_conversacion(finaliza_prematuro = False)
						else:
							#Verifica sl la jurisdiccion (Estado) viene en el mensaje
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
					#Si no se brinda asesoria 
					else:																	
						message.save_contexts_odoo(contextos = [ ("general_fin") ], session_id = self.id)
						#Si se canaliza
						if delito.canalizacion == True:
							self.write({ 'status'  : 'delito_canalizacion' })
						else:
							self.write({ 'status'  : 'delito_no_asesoria' })
						return self.finaliza_conversacion(finaliza_prematuro = False)
				#Si el delito no esta definido en ODOO -> Regresamos mensaje fijo avisando que no tenemos conocimiento sobre el delito
				else:																		
					message.save_contexts_odoo(contextos = [ ("general_fin") ], session_id = self.id)
					self.write({ 'status'  : 'delito_no_definido' })
					return self.finaliza_conversacion(finaliza_prematuro = False)
			#Si el delito no viene en el mensaje -> Regresamos pregunta fija para obtener el delito
			else:																			
				#Verifica sl la jurisdiccion (CP o Estado) esta definida en la conversacion, para guardarla de una vez 
				#y asi eliminar la necesidad de un mensjae en la conversacion
				if self.check_jurisdiccion_in_channel() == False:
					#Verifica sl la jurisdiccion (CP o Estado) viene en el mensaje
					jurisdiccion_in_message = message.check_jurisdiccion_in_message(body, tipo_analisis = "estado")
					#Si la jurisdiccion viene en el mensaje
					if jurisdiccion_in_message != False: 											
						self.save_jurisdiccion(jurisdiccion=jurisdiccion_in_message,message_id=message.id)
				return (u'¿Cuál fue el delito? (¿te robaron el celular?, ¿te asaltaron en el transporte público?)')


	