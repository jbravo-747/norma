# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.http import controllers_per_module
from odoo.addons.mail.controllers.bus import MailChatController
import nexmo
from quiubas import Quiubas


import re
import unicodedata

NEXMO_API_KEY = 'f9408e47'
NEXMO_API_SECRET = 'GrVeqmTPprlr7AGP'
QUIUBAS_API_KEY = '2d21e6bd5826177acd2ffbb434bdf3e475d79102'
QUIUBAS_API_SECRET = '75b8940e7ab913e3136f770406e8eba748a9090a'
# from clickatell.http import Http


class imco_norma_sms_user(models.Model):
	_name = "imco.norma.sms.user"

	name = fields.Char(string="Usuario")
	
	messages_ids = fields.One2many('imco.norma.sms.channel', 'user_id', string="Mensajes del usuario")
	channel_ids = fields.One2many('mail.channel', 'user_sms_id', string="Chats del usuario")

	@api.model
	def get_sms_user(self, tel):
		user = self.env['imco.norma.sms.user'].sudo().search( [ ('name','=', tel) ],limit=1)
		if len(user) == 0:
			user= self.env['imco.norma.sms.user'].sudo().create( { 'name' : tel } )
		return user

class imco_norma_sms_channel(models.Model):
	_name = "imco.norma.sms.channel"

	gateway = fields.Char(string="Gateway")
	date = fields.Date(string="Fecha", default=fields.datetime.now())
	messageId = fields.Text(string="Id del mensaje")
	message = fields.Text(string="Mensaje del usuario")
	reply_messsage = fields.Text(string="Respuesta de norma")
	accepted = fields.Boolean(string="Mensaje aceptado")
	
	mail_channel_id = fields.Many2one('mail.channel', string="Chat asociado al mensaje")
	user_id = fields.Many2one('imco.norma.sms.user', string="Usuario")

	@api.multi
	def check_channel_open(self):
		# Busca el chat
		domain = [ ('user_sms_id', '=', self.user_id.id), ('status', 'in', ["proceso"]) ]
		mail_channel = self.env['mail.channel'].sudo().search(domain, limit=1)
		print(mail_channel, len(mail_channel))
		if len(mail_channel) == 0:
			liveChat = None
			for name, instance in controllers_per_module.get('opit_imco_norma_chat'):
				if name.endswith('LivechatController'):
					liveChat = instance
					break
			if liveChat is not None:
				# Busca la session del chat creada anteriormente o crea una nueva
				new_ch = liveChat().get_session(metodo_contacto='sms',channel_id=2, anonymous_name=self.user_id.name)
				mail_channel = self.env['mail.channel'].browse([new_ch['id']])
				mail_channel.write({'user_sms_id': self.user_id.id})
		else:
			mail_channel = mail_channel[0]
		self.sudo().write( { 'mail_channel_id' : mail_channel.id } )
		return mail_channel
	
	@api.multi
	def message_analysis(self, mail_channel):
		for msg in self:
			reply_id = None
			reply_id = MailChatController().mail_chat_post( uuid=mail_channel['uuid'], message_content = msg.message)
			if reply_id is not None:
				reply = self.env['mail.message'].browse([reply_id])
				#Revisa si es un mensaje de finalizacion para cerrar la sesion y mandar toda la informacion
				respuesta = reply.body 
				print (len(self.mail_channel_id.channel_message_ids) )
				if ";;;fin;;;" in respuesta:
					self.mail_channel_id.sudo().write( { "sesion_cerrada" : True } )
					web_path = self.env["ir.config_parameter"].sudo().search([("key","=", "web.base.url")], limit=1).value
					respuesta = respuesta.replace(";;;fin;;;", "")
					respuesta += "\n Revisa los documentos que hemos preparado para ti: "
					respuesta += web_path + "/mail/norma/transcripcion/" + self.mail_channel_id.uuid 
					respuesta += " " + self.mail_channel_id.url_recomendacion
					respuesta += "\nTu ID de asesoria es " + self.mail_channel_id.uuid 
				elif len(self.mail_channel_id.channel_message_ids) == 2:
					if "Hola" in respuesta or "en que te puedo ayudar" in respuesta: 
						respuesta = "Hola, soy Norma y te quiero ayudar!!!. Necesitaré realizarte algunas preguntas para poder darte una recomendación.\n ¿Qué te sucedió?"
					else:
						respuesta = "Hola, soy Norma y te quiero ayudar!!!. Necesitaré realizarte algunas preguntas para poder darte una recomendación.\n  " + respuesta
				cleanr = re.compile('<.*?>')
				cleantext = re.sub(cleanr, '', respuesta)
				cleantext = ''.join((c for c in unicodedata.normalize( 'NFD', str(cleantext)) if unicodedata.category(c) != 'Mn'))
				msg.write({'reply_messsage': cleantext}) 
		return cleantext
	
	
	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	@api.multi
	def message_send(self, message):
		for msg in self:
			response = None
			if msg.gateway == 'quiubas':
				quiubas = Quiubas()
				quiubas.setAuth(QUIUBAS_API_KEY, QUIUBAS_API_SECRET)
				response = quiubas.sms.send({
					'sender': '9993191926',
					'to_number':  msg.user_id.name,
					'message': message,
				})
			if msg.gateway == 'nexmo':
				client = nexmo.Client(
					key=NEXMO_API_KEY, secret=NEXMO_API_SECRET)
				response = client.send_message({
					'from': '525549998942',
					'to': msg.user_id.name,
					'text': message,
				})
			print(response)  # Returns the headers with all the messages
		return response