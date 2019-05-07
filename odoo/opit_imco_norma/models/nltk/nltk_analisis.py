# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, date
from pytz import timezone
from openerp import SUPERUSER_ID
from openerp import api, fields, models, _
import openerp.addons.decimal_precision as dp
from openerp.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import except_orm, Warning, RedirectWarning, UserError
from dateutil.parser import parse as parse_date

class imco_norma_mail_analisis_nltk_entidades(models.Model):
	_name = "imco.norma.mail.analisis.nltk.entidades"
	_description = 'Relacion de entidades encontradas despues de analizar los mensajes'
	_rec_name = "channel_id"
	_order='channel_id asc, message_id desc, entidad_id asc, valor asc'


	channel_id = fields.Many2one( 'mail.channel', string='Chat asociado')
	message_id = fields.Many2one( 'mail.message', string='Mensaje asociado')
	entidad_id = fields.Many2one( 'imco.norma.nltk.entidades', string='Entidad asociada')
	valor = fields.Char(string="Valor de la entidad")



class imco_norma_mail_analisis_nltk_contextos(models.Model):
	_name = "imco.norma.mail.analisis.nltk.contextos"
	_description = 'Relacion de contextos encontrados despues de analizar los mensajes'
	_rec_name = "channel_id"
	_order='channel_id asc, message_id desc, date desc, valor asc'


	channel_id = fields.Many2one( 'mail.channel', string='Chat asociado')
	message_id = fields.Many2one( 'mail.message', string='Mensaje asociado')
	date = fields.Datetime(string="Fecha de creacion")
	valor = fields.Char(string="Valor de la entidad")

	@api.model
	def create(self, vals):
		vals['date'] = fields.datetime.now()
		result = super(imco_norma_mail_analisis_nltk_contextos, self).create(vals)
		return result
