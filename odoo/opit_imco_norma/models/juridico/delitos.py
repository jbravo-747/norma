# -*- coding: 850 -*-
from datetime import datetime, timedelta, date
from pytz import timezone
from openerp import SUPERUSER_ID
from openerp import api, fields, models, _
import openerp.addons.decimal_precision as dp
from openerp.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import except_orm, Warning, RedirectWarning, UserError
from dateutil.parser import parse as parse_date

class imco_norma_delitos(models.Model):
	_name = "imco.norma.delitos"
	_description = 'Listado de delitos'
	_order='name' 
	
	
	name = fields.Char(string="Nombre de la jurisdiccion", default='', required=True) 
	codigo = fields.Char(string="Codigo", required=True)
	fuero_delito = fields.Selection([
		('sin_definir','Sin definir'),
		('federal','Federal'),
		('estatal','Estatal'),
		],string="Fuero del delito", default="sin_definir")
		
	asesoria = fields.Boolean(string="Se brinda asesoria?", default=False)
	canalizacion= fields.Boolean(string="Se canaliza a otra institucion?", default=False)
	
	mensaje_no_asesoria = fields.Text(string='Mensaje predeterminado si no se ofrece asesoria para el delito')
	mensaje_jurisdiccion_no_aplica= fields.Text(string='Mensaje predeterminado si se ofrece asesoria pero no en la jurisdiccion aplicable')
	mensaje_canalizacion = fields.Text(string='Mensaje predeterminado si se canaliza con otra institucion')
	notas = fields.Text(string='Notas adicionales')
	#---------------------
	jurisdicciones_delitos_ids = fields.One2many( 'imco.norma.delitos.jurisdiccion', 'delito_id', 
		string='Jurisdicciones aplicables')
	entidades_requeridas_ids = fields.One2many( 'imco.norma.delitos.jurisdiccion.entidades.requeridas', 'delito_id', 
		string='Entidades requeridas de los delitos en las jurisdicciones')
	variantes_ids = fields.One2many( 'imco.norma.delitos.jurisdiccion.variantes', 'delito_id', 
		string='Variantes de los delitos en las jurisdicciones')
	variantes_entidades_ids = fields.One2many( 'imco.norma.delitos.jurisdiccion.variantes.nltk.entidades', 'delito_id', 
		string='Variantes de los delitos en las jurisdicciones')
	
		