# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.modules.module import get_resource_path
import dialogflow
import json
import os
import sys, traceback
import logging
import re
import pprint

_logger = logging.getLogger(__name__)
relative_location = '/opit_imco_norma/google_auth/service-account.json'
key_path = (segment for segment in relative_location.split('/') if segment)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] =  get_resource_path(*key_path)
PROJECT_ID = 'norma-203517'


def clean_text(text):
	cleanr = re.compile('<.*?>')
	cleantext = re.sub(cleanr, '', text)
	return cleantext.strip()

class mail_message(models.Model):
	_inherit = ['mail.message']


	#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
	#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
	#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	#Analisis de mensaje en DialogFlow
	@api.multi
	def analisis_dialogflow(self, text, session_id, context = None):
		"""
		Manda a dialog flow el texto para detectar las entidades en el mensaje y regresa las entidades  y la accion  encontradas con el siguiente formato
			 res = [
				"action": [accion],
				"entidades": [(key,value)]
				"dialogflow_response":[string]
			]
		"""
		session_client = dialogflow.SessionsClient()
		# crea una sesion en dialog flow si no existe para identificar la conversacion --------------------------------------------------------------------------------
		session = session_client.session_path(PROJECT_ID, session_id)
		# genera los parametros necesarios para el analisis ------------------------------------------------------------------------------------------------------------------------
		text_input = dialogflow.types.TextInput(text=text, language_code='es-MX')
		query_input = dialogflow.types.QueryInput(text=text_input)
		# envia el contexto a dialogflow si el contexto esta definido ------------------------------------------------------------------------------------------
		if context != None:
			if context.startswith("entidad_"):
				contexts_client = dialogflow.ContextsClient()
				context_name = contexts_client.context_path(PROJECT_ID, session_id, context )
				c = dialogflow.types.Context(name = context_name, lifespan_count=1)
				response_ctx = contexts_client.create_context(session, c)
		# analiza el mensaje del usuario -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
		response = session_client.detect_intent(session=session ,  query_input=query_input)
		res = {}
		res['action'] = response.query_result.action
		res['entidades'] = {}
		x = response.query_result.parameters.items()
		print(x)
		for key, value in x:
			if value != "" or type(value) in [int, float]:
				k = re.sub(r'[0-9]+', '', key.lower())
				print (k)
				if k not in res["entidades"]:
					res["entidades"][k]  = []
				#Guarda
				if type(value) == str:
					res['entidades'][k].append( value.lower()  )
				elif type(value) in (int, float):
					res['entidades'][k].append( str(value)  )
				else:
					for v2 in value.items():
						print(v2)
						res['entidades'][k].append( v2.lower()  )
		#res['entidades'] =  response.query_result.parameters.items()
		res['dialogflow_response']=response
		return res

	#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
	#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
	#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	#Guarda en la conversacion las entidades detectadas (incluye la entidad y su valor)
	@api.multi
	def save_entities(self, entidades, session_id):
		print("Entra a save entities .....")
		print(entidades)
		#Guarda las entidades encontradas en el mensaje (delito,lugar, fecha, etc)
		entities_ok = []
		for key in entidades:
			for value in entidades[key]:
				if value != '':
					entidad = self.env['imco.norma.nltk.entidades'].sudo().search([('codigo', '=', key.lower() )], limit=1)
					#Verifica si el valor recibido esta definido en los alias de las entidades
					if entidad.id not in [False, None]:
						if entidad.codigo == "delito":
							r = value.lower()
						else:
							r = value.lower()
							###Revisa si es un numero, en cuyo caso lo guarda sin buscar en los alias
							##number = False
							##try:
							##	temp = float(value)
							##	number = True
							##except:
							##	pass
							##if number == True:
							##	r = value
							##else:
							##	r = self.env['imco.norma.delitos.jurisdiccion.entidades.requeridas'].sudo().\
							##		search_text_in_entidades_alias(value.lower(), key.lower() )
						##if r != False:
							vals = {'channel_id': session_id, 'message_id': self.id, 'entidad_id': entidad.id, 'valor': value.lower() }
							print (vals)
							analisis_entidad = self.env['imco.norma.mail.analisis.nltk.entidades'].create(vals)
							#self.env.cr.commit()
							entities_ok.append(( key.lower(), r))
		return entities_ok


	#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
	#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
	#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	#Guarda en la conversacion y en dialogflow los contextos asociados a las entidades recibidas
	@api.multi
	def save_context_delito(self, llave, session_id):
		self.env['imco.norma.mail.analisis.nltk.contextos'].sudo().create({
			'channel_id': session_id,
			'message_id': self.id,
			'valor': ("delito_" + llave.lower() )})
		session_client = dialogflow.SessionsClient()
		# crea una sesion en dialog flow si no existe para identificar la conversacion
		session = session_client.session_path(PROJECT_ID, session_id)
		#Inicializa el objeto de dialogflow para contextos
		contexts_client = dialogflow.ContextsClient()
		context_name = contexts_client.context_path(PROJECT_ID, session_id, ("delito_" + llave.lower() ) )
		context = dialogflow.types.Context(name = context_name, lifespan_count = 100)
		response_ctx = contexts_client.create_context(session, context)

	#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
	#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
	#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	#Guarda en la conversacion y en dialogflow los contextos asociados a las entidades recibidas
	@api.multi
	def save_contexts_odoo(self, contextos, session_id):
		for context in contextos:
			self.env['imco.norma.mail.analisis.nltk.contextos'].sudo().create({
				'channel_id': session_id,
				'message_id': self.id,
				'valor': context})


	#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
	#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
	#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	#Revisa si la jurisdiccion viene en el mensaje a analizar
	@api.multi
	def check_jurisdiccion_in_message(self, text, tipo_analisis= "estado", estado_id = False):
		res = False
		if tipo_analisis in ["cp", "municipio", "estado"]:
			# quitar espacios al inicio y al final del texto
			text = clean_text(text)
			if tipo_analisis == "cp":
				if text.isdigit():
					# darle formato de 5 digitos
					cp = text
					if len(cp) ==2:
						cp = "000" + cp
					elif len(cp) ==3:
						cp = "00" + cp
					elif len(cp) ==4:
						cp = "0" + cp
					print(cp)
					# buscarlo en la base de datos
					domain = [('cp','=',cp), ('estado_id','=',estado_id)]
					print(domain)
					localidad = self.env['imco.general.entes.sepomex.localidades'].search(domain,limit=1)
					print(localidad)
					if localidad.id not in [False, None]:
						res = {
							"tipo_ente" : "cp",
							"ente" : {
								"cp" : localidad,
								"municipio" : localidad.municipio_id,
								"estado" : localidad.estado_id,
								}
							}
			else:				
				#obtiene todos los entes geograficos cuyo nombre o acronimo esten contenidos en el mensaje buscado (aunque no sean palabras completas)
				sql = "SELECT distinct(e.id), e.tipo_ente, "
				sql += " array_to_string( ARRAY( "
				sql += " SELECT lower(regexp_replace(regexp_replace(unaccent(name),'[^a-zA-Z0-9\s;;;]','','g'),'\s+',' ','g') )"
				sql += " FROM imco_general_entes_geograficos_alias a WHERE a.ente_id= af.ente_id)"
				sql += " , ';;;') AS terminos,"
				sql += " lower(regexp_replace(regexp_replace(unaccent( %s ),'[^a-zA-Z0-9\s]','','g'),'\s+',' ','g') ) as texto_pedido"
				sql += " FROM ("
				sql += " SELECT ente_id "
				sql += " FROM imco_general_entes_geograficos_alias"
				sql += " WHERE "
				sql += " regexp_replace(regexp_replace(unaccent( %s ),'[^a-zA-Z0-9\s]','','g'),'\s+',' ','g')"
				sql += " ilike '%%' || regexp_replace(regexp_replace(unaccent(name),'[^a-zA-Z0-9\s]','','g'),'\s+',' ','g') || '%%' "
				sql += " ) as af,"
				sql += " imco_general_entes_geograficos e"
				sql += " WHERE e.id = af.ente_id "
				if tipo_analisis == 'estado': 
					sql += " AND tipo_ente = 'estado' "
				elif tipo_analisis == 'municipio':
					sql += " AND padre_id = " + str(estado_id) + " AND tipo_ente = 'municipio' "
				sql += " ORDER BY e.id"
				print (tipo_analisis, estado_id, text)
				print (sql)
				self.env.cr.execute(sql, (text , text))
				ubicaciones = self.env.cr.dictfetchall()
				ubicaciones_exitosas = {}
				i = 0
				for u in ubicaciones:
					#Obtiene un listado de las palabras contenidas en el mensaje recibido (previamente procesado en postgres para remover acentuaciones)
					if i == 0:
						palabras_buscadas = u["texto_pedido"] .split(" ")
						i += 1
					#Separa los terminos (todos los alias)
					terminos = u["terminos"].split(";;;")
					#Verifica si tenemos coincidencias en todas las palabras de la entidad (acronimo o nombre) en el mensaje recibido
					res_local = False
					for t in terminos:
						if res_local == False:
							res_local = True
							for termino_alias in t.split(" "):
								if termino_alias not in palabras_buscadas:
									res_local = False
					# Si fue encontrado todas las palabras del ente (acronimo o nombre) en el mensaje recibido, entonces lo guarda respetando el tipo de ente
					if res_local == True:
						if u["tipo_ente"] not in ubicaciones_exitosas:
							ubicaciones_exitosas[u["tipo_ente"]] = []
						ubicaciones_exitosas[u["tipo_ente"]].append(u["id"])
				#  Procesa los resultados si son estados
				if tipo_analisis == "estado":
					if "estado" in ubicaciones_exitosas:
						if len(ubicaciones_exitosas["estado"]) > 1:
							pass
						else:
							res = {
								"tipo_ente" : "estado",
								"ente" : {
									"estado" : self.env['imco.general.entes.geograficos'].search([('id','=',ubicaciones_exitosas["estado"][0])], limit=1)
									}
								}
				elif tipo_analisis == 'municipio':
					if "municipio" in ubicaciones_exitosas:
						if len(ubicaciones_exitosas["municipio"]) > 1:
							pass
						else:
							municipio = self.env['imco.general.entes.geograficos'].search([('id','=',ubicaciones_exitosas["municipio"][0])], limit=1)
							res = {
								"tipo_ente" : "municipio",
								"ente" : {
									"municipio" : municipio,
									"estado" : municipio.padre_id,
									}
								}
		return res
