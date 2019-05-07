# -*- coding: 850 -*-
from datetime import datetime, timedelta, date
from pytz import timezone
from openerp import SUPERUSER_ID
from openerp import api, fields, models, _
import openerp.addons.decimal_precision as dp
from openerp.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import except_orm, Warning, RedirectWarning, UserError
from dateutil.parser import parse as parse_date

class imco_norma_jurisdiccion(models.Model):
	_name = "imco.norma.jurisdiccion"
	_description = 'Jurisdicciones aplicables a los diferentes delitos'
	_order='tipo_jurisdiccion asc, name' 
	
	name = fields.Char(string="Nombre de la jurisdiccion", default='', required=True)
	tipo_jurisdiccion = fields.Selection( [
		('sin_definir','Sin definir'),
		('federal','Federal'),
		('estatal','Estatal'),
		('municipal','Municipal'),
		('localidad','Localidad'),
		], string='Tipo de jurisdiccion', default='sin_definir', required=True)
	notas = fields.Text(string='Notas adicionales')
	#---------------------
	
	estado_id = fields.Many2one( 'imco.general.entes.geograficos', string="Entidad federativa asociada")
	entes_geograficos_ids = fields.One2many( 'imco.norma.jurisdiccion.entes.geograficos', 'jurisdiccion_id', 
		string='Entes geograficos asociados')
	jurisdicciones_delitos_ids = fields.One2many( 'imco.norma.delitos.jurisdiccion', 'jurisdiccion_id', 
		string='Delitos asociados')
	entidades_requeridas_ids = fields.One2many( 'imco.norma.delitos.jurisdiccion.entidades.requeridas', 'jurisdiccion_id', 
		string='Entidades requeridas de los delitos en las jurisdicciones')
	variantes_ids = fields.One2many( 'imco.norma.delitos.jurisdiccion.variantes', 'jurisdiccion_id', 
		string='Variantes de los delitos en las jurisdicciones')
	variantes_entidades_ids = fields.One2many( 'imco.norma.delitos.jurisdiccion.variantes.nltk.entidades', 'jurisdiccion_id', 
		string='Variantes de los delitos en las jurisdicciones')
		
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class imco_norma_jurisdiccion_entes_geograficos(models.Model):
	_name = "imco.norma.jurisdiccion.entes.geograficos"
	_description = 'Entes geograficos comprendidos en la jurisdiccion'
	_order='jurisdiccion_id asc, ente_id' 
	
	@api.depends('jurisdiccion_id', 'ente_id')
	def _compute_name(self):
		for r in self:
			cad = ""
			try:
				cad += r.jurisdiccion_id.name
			except:
				pass
			cad += " / "
			try:
				cad += r.ente_id.name
			except:
				pass
			r.name = cad
			
	name = fields.Char(string="Referencia", compute='_compute_name', store=True)
	#---------------------
	jurisdiccion_id = fields.Many2one( 'imco.norma.jurisdiccion', string='Jurisdiccion asociada')
	ente_id = fields.Many2one( 'imco.general.entes.geograficos', string='Entes geografico asociado')
		
