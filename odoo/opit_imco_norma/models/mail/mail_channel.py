# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import sys, traceback
import logging

_logger = logging.getLogger(__name__)

class MailChannel(models.Model):
	_inherit = ['mail.channel']

	@api.depends("message_ids")
	def _compute_numero_mensajes(self):
		for r in self:
			r.numero_mensajes = len(r.message_ids)

	@api.depends('delito_id', 'jurisdiccion_id')
	def _compute_delito_jurisdiccion_id(self):
		for r in self:
			try:
				if r.delito_id.id in [False,None] or r.jurisdiccion_id.id in [False,None]:
					r.delito_jurisdiccion_id = False
				else:
					dj = self.env["imco.norma.delitos.jurisdiccion"].search([('delito_id', '=', r.delito_id.id), ('jurisdiccion_id', '=', r.jurisdiccion_id.id)], limit=1)
					if dj.id not in [False, None]:
						r.delito_jurisdiccion_id = dj.id
			except:
				traceback.print_exc(file=sys.stdout)

	@api.depends('uuid')
	def _compute_url_recomendacion(self): 
		for r in self:
			try:
				parameter_url = self.env["ir.config_parameter"].sudo().search([("key","=", "custom.web.reporting.path")], limit=1)
				cad = parameter_url.value + "mail/norma/informacion/" + r.uuid
				r.url_recomendacion = cad
			except:
				pass
	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	metodo_contacto = fields.Selection([
		('sin_definir', 'Sin definir'),
		('sistema_interno', 'Sistema Interno'),
		('chat', 'Chat'),
		('sms', 'SMS'),
		], string='Metodo de contacto', default="sistema_interno")
	status = fields.Selection([
		('proceso', 'En proceso'),
		('delito_no_definido', 'Delito sin definir en sistema'),
		('delito_no_asesoria', 'Delito sin asesoria'),
		('delito_canalizacion', 'Delito canalizado a otra institucion'),
		('delito_jurisdiccion_no_definida', 'Jurisdiccion no definida para delito'),
		('variante_sin_definir', 'Variante sin definir para jurisdiccion - delito'),
		('finalizado_prematuro', 'Finalizado sin toda la informacion'),
		('finalizado_exitoso', 'Finalizado exitosamente'),
		('abandonado', 'Conversacion abandonada'),
		#('sesion_cerrada', 'Sesion finalizada'),
		], string='Estatus en la comunicacion', default="proceso")
	
	email_envio = fields.Char(string="Email para envio de conversacion")
	numero_mensajes = fields.Integer(string="Numero de mensajes", compute="_compute_numero_mensajes")
	
	sesion_cerrada = fields.Boolean(string="Sesion cerrada?", default=False)
	finalizado_prematuro = fields.Boolean(string="Finalizo prematuramente la entrevista?", default=False)
	finalizado_exitoso = fields.Boolean(string="Completo la entrevista?", default=False)
	
	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	#Variables generales de localizacion
	estado_id = fields.Many2one('imco.general.entes.geograficos', string='Estado asociado')
	municipio_id = fields.Many2one('imco.general.entes.geograficos', string='Municipio asociado')
	cp_id = fields.Many2one('imco.general.entes.sepomex.localidades', string='CP asociado')
	
	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	#Variables generales del delito
	delito_id = fields.Many2one('imco.norma.delitos', string='Delito asociado')
	jurisdiccion_id = fields.Many2one('imco.norma.jurisdiccion', string='Jurisdiccion asociada')
	delito_jurisdiccion_id = fields.Many2one('imco.norma.delitos.jurisdiccion', string='Relacion Delito - Jurisdiccion',
		compute="_compute_delito_jurisdiccion_id", store = True)
	variante_id = fields.Many2one('imco.norma.delitos.jurisdiccion.variantes', string='Relacion Delito - Variante - Jurisdiccion')
	
	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	#Variables que contienen los analisis de las conversaciones (contextos y entidades reconocidas)
	messages_analisis_entidades_ids = fields.One2many('imco.norma.mail.analisis.nltk.entidades', 'channel_id',
		string='Entidades asociadas a la conversacion')
	messages_analisis_contextos_ids = fields.One2many('imco.norma.mail.analisis.nltk.contextos', 'channel_id',
		string='Contextos asociados a la conversacion')
	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------

	url_recomendacion = fields.Char(string="URL documento con recomendacion personalizada", 
		compute="_compute_url_recomendacion", store = False)

	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	@api.multi
	def message_post(self, body='', subject=None, message_type='notification', subtype=None, parent_id=False, attachments=None,
		content_subtype='html', **kwargs):
		message = super(MailChannel, self.with_context(mail_create_nosubscribe=True))\
			.message_post(body=body, subject=subject, message_type=message_type,
				subtype=subtype, parent_id=parent_id, attachments=attachments,
				content_subtype=content_subtype, **kwargs)
		#Verifica si es un chat
		if self.channel_type == "livechat":
			#Verifica si es el canal de Norma y es un mensaje del usuario
			if self.livechat_channel_id.codigo_canal == "norma" and kwargs["author_id"] == False:
				respuesta = self.analizar_mensaje_flujo_delito(message, body)
				titulo = "Respuesta automatica de norma"
				norma_user = self.env["res.users"].sudo().search([('codigo_chat', '=', 'robot.norma')], limit=1)
				extra_parameters = {
					'author_id': norma_user.partner_id.id,
					'email_from':  norma_user.email
					}
				message = super(MailChannel, self.with_context(mail_create_nosubscribe=True))\
					.message_post(body=respuesta, subject=titulo, message_type=message_type,
						subtype=subtype, parent_id=parent_id, attachments=attachments,
						content_subtype=content_subtype, **extra_parameters)
		return message
