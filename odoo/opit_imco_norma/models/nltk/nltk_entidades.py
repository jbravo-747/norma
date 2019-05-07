# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, date
from pytz import timezone
from openerp import SUPERUSER_ID
from openerp import api, fields, models, _
import openerp.addons.decimal_precision as dp
from openerp.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import except_orm, Warning, RedirectWarning, UserError
from dateutil.parser import parse as parse_date

class imco_norma_nltk_entidades(models.Model):
	_name = "imco.norma.nltk.entidades"
	_description = 'Entidades de interes localizables en los textos'
	_order = "name asc"

	name = fields.Char( string='Nombre de la entidad', default="", required=True)
	codigo = fields.Char( string='Codigo', default="", required=True)
	notas = fields.Text(string='Notas adicionales')

	messages_analisis_entidades_ids = fields.One2many( 'imco.norma.mail.analisis.nltk.entidades', 'entidad_id',
		string='Mensajes asociados a la entidad')
	delitos_jurisdicciones_variantes_ids = fields.One2many( 'imco.norma.delitos.jurisdiccion.variantes.nltk.entidades', 'entidad_id',
		string='Variantes de delitos en jurisdicciones asociados a la entidad')
	alias_ids = fields.One2many( 'imco.norma.nltk.entidades.alias', 'entidad_id',
		string='Alias asociados a la entidad')


class imco_norma_nltk_entidades_alias(models.Model):
	_name = "imco.norma.nltk.entidades.alias"
	_description = 'Alias de las entidades de interes localizables en los textos'
	_order = "valor asc, name asc"

	name = fields.Char( string='Nombre de la entidad', default="", required=True)
	valor = fields.Char( string='Valor asociado', default="", required=True)
	entidad_id = fields.Many2one( 'imco.norma.nltk.entidades', string='Entidad asociada', required=True)
