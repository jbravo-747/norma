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
import re
from bottle import SimpleTemplate
import sys, traceback
import requests
import base64
import werkzeug



#Account:rs520543
def render_template(html_file, datos):
	template = open(html_file, "r")
	tpl = SimpleTemplate(template)
	return tpl.render(datos)
	

_logger = logging.getLogger(__name__)

class MailChannel(models.Model):
	_inherit = ['mail.channel']

	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	@api.multi
	def analizar_envio_informacion(self, message, body):
		#Si recibe un mensaje despues de haber finalizado la conversacion (prematuramente o por fin del flujo),
		#Entonces verifica si recibe un correo para envio de informacion o una negativa
		if re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", body):
			#Procedimeinto para envio de mail
			self.write( { "sesion_cerrada" : True, "email_envio" : body } )
			res = self.action_envio_informacion(email = body)
			return (";;;calificacion;;;Tu ID de asesoria es " + self.uuid + "por si quieres contactarnos." )
		elif "no" in body:
			self.write( { "sesion_cerrada" : True } )
			return (";;;calificacion;;;Tu ID de asesoria es " + self.uuid + "por si quieres contactarnos." )
		else:
			return (";;;fin;;;No hemos entendido tu correo electronico o si no queires recibir la informacion" )
			
		
	
	@api.multi
	def action_envio_informacion(self, email = None):
		destinatarios = []
		#destinatarios.append("gilberto@opit.mx")
		if email != None :
			destinatarios.append(email)
		recomendacion = self.obtiene_recomendacion_conversacion()
		print (recomendacion)
		module_path = self.env["ir.config_parameter"].search([("key","=", "custom.modules.path")], limit=1).value
		mailgun_api = self.env["ir.config_parameter"].search([("key","=", "custom.mailgun.api")], limit=1).value
		mailgun_key = self.env["ir.config_parameter"].search([("key","=", "custom.mailgun.key")], limit=1).value
		web_path = self.env["ir.config_parameter"].sudo().search([("key","=", "web.base.url")], limit=1).value
		file = module_path + "opit_imco_norma/others/envio_informacion.html"
		url_transcripcion = web_path + "/mail/norma/transcripcion/" + self.uuid
		parameters = {
			'titulo' : "Envío de Información de Norma, la abogada de las víctimas",
			'estado' : "" if self.estado_id.id in [False, None] else self.estado_id.name,
			'municipio' : "" if self.municipio_id.id in [False, None] else self.municipio_id.name,
			'cp' : "" if self.cp_id.id in [False, None] else ( "(" + self.cp_id.cp + ") " + self.cp_id.name),
			'delito' : "" if self.delito_id.id in [False, None] else self.delito_id.name,
			'jurisdiccion' : "" if self.jurisdiccion_id.id in [False, None] else self.jurisdiccion_id.name,
			'variante' : "" if self.variante_id.id in [False, None] else self.variante_id.name,
			"recomendacion" : recomendacion,
			"url_recomendacion" : self.url_recomendacion,
			"url_transcripcion" : url_transcripcion,
			'mensajes' : [ {
				"remitente" : "Norma: La abogada de las víctimas",
				"mensaje" : "Hola, ¿cómo te puedo ayudar?"
				} ]
			}
		for m in self.message_ids.sorted(key=lambda r: r.id):
			parameters["mensajes"].append({
				'remitente' : m.author_id.name if m.author_id.id not in [False, None, ''] else "Tú",
				'mensaje' : m.body if ";;;" not in m.body else m.body.split(";;;")[-1],
				})
		print(file)
		pprint.pprint(parameters)
		html = render_template(file, parameters)
		try:
			#print (html)
			for e in destinatarios:
				print ("Envio de correo a " + e)
				p = requests.post(
					mailgun_api,
					auth=("api", mailgun_key),
					data={
						"from": "Norma, La abogada de las victimas <postmaster@mail.imco.org.mx>",
						"to": e,
						"subject": "Envio de informacion de Norma, La abogada de las victimas",
						"html": html
						}
					)
				print (p)
			res =  "Todo bien"
		except: 
			traceback.print_exc(file=sys.stdout)
			res =  "Todo mal"
		response = werkzeug.wrappers.Response()
		response.data = html
		response.mimetype = 'text/html'
		headers = werkzeug.wrappers.Headers()
		headers.set('Content-Disposition', 'inline', filename=parameters["titulo"].encode('latin-1'))
		response.headers = headers
		return response
		
		
		
		
		
		
		
		
		
		