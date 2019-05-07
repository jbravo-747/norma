# -*- coding: 850 -*-
from datetime import datetime, timedelta, date
from pytz import timezone
from openerp import SUPERUSER_ID
from openerp import api, fields, models, _
import openerp.addons.decimal_precision as dp
from openerp.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import except_orm, Warning, RedirectWarning, UserError
from dateutil.parser import parse as parse_date
import random

class imco_norma_delitos_jurisdiccion(models.Model):
	_name = "imco.norma.delitos.jurisdiccion"
	_description = 'Relacion de aplicabilidad de delitos en distintas jurisdicciones'
	_order='delito_id asc, jurisdiccion_id asc'

	@api.depends('jurisdiccion_id', 'delito_id')
	def _compute_name(self):
		for r in self:
			cad = ""
			try:
				cad += r.delito_id.name
			except:
				pass
			cad += " / "
			try:
				cad += r.jurisdiccion_id.name
			except:
				pass
			r.name = cad

	name = fields.Char(string="Referencia", compute='_compute_name', store=True)
	recomendacion_sin_variante = fields.Text(string='Recomendacion si no se detecta variante')
	notas = fields.Text(string='Notas adicionales')
	#---------------------
	delito_id = fields.Many2one( 'imco.norma.delitos', string='Delito asociado')
	jurisdiccion_id = fields.Many2one( 'imco.norma.jurisdiccion', string='Jurisdiccion asociada')
	#---------------------
	entidades_requeridas_ids = fields.One2many( 'imco.norma.delitos.jurisdiccion.entidades.requeridas', 'delito_jurisdiccion_id',
		string='Entidades requeridas de los delitos en las jurisdicciones')
	variantes_ids = fields.One2many( 'imco.norma.delitos.jurisdiccion.variantes', 'delito_jurisdiccion_id',
		string='Variantes de los delitos en las jurisdicciones')
	variantes_entidades_ids = fields.One2many( 'imco.norma.delitos.jurisdiccion.variantes.nltk.entidades', 'delito_jurisdiccion_id',
		string='Variantes de los delitos en las jurisdicciones')


#------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------
class imco_norma_delitos_jurisdiccion_entidades_requeridas(models.Model):
	_name = "imco.norma.delitos.jurisdiccion.entidades.requeridas"
	_description = 'Entidades requeridas de los delitos en las jurisdicciones'
	_order='delito_id asc, jurisdiccion_id asc, sequence'

	@api.depends('delito_jurisdiccion_id','jurisdiccion_id', 'delito_id','entidad_id')
	def _compute_name(self):
		for r in self:
			cad = ""
			try:
				cad += "[" + r.delito_jurisdiccion_id.delito_id.name + "]"
			except:
				pass
			try:
				cad += "[" + r.delito_jurisdiccion_id.nombre_variante+ "]"
			except:
				pass
			try:
				cad += "[" + r.delito_jurisdiccion_id.jurisdiccion_id.name + "]"
			except:
				pass
			try:
				cad +=  " " + r.entidad_id.name
			except:
				pass
			r.name = cad

	@api.depends('delito_jurisdiccion_id')
	def _compute_delito_id(self):
		for r in self:
			try:
				r.delito_id = r.delito_jurisdiccion_id.delito_id.id
			except:
				pass

	@api.depends('delito_jurisdiccion_id')
	def _compute_jurisdiccion_id(self):
		for r in self:
			try:
				r.jurisdiccion_id = r.delito_jurisdiccion_id.jurisdiccion_id.id
			except:
				pass

	name = fields.Char(string="Referencia", compute='_compute_name',  store=True)
	sequence = fields.Integer(string='Secuencia')
	tipo_analisis = fields.Selection([
		('previo','Entidad requerida a priori'),
		('interno','Logica Interna'),
		], string='Tipo de entidad', default="interno", required=True)
	funcion_analisis_interno = fields.Char(string='Funcion de analisis interno')
	notas = fields.Text(string='Notas adicionales')
	#---------------------
	entidad_id = fields.Many2one( 'imco.norma.nltk.entidades', string='Entidad NLTK asociada')
	delito_id = fields.Many2one( 'imco.norma.delitos', string='Delito asociado', compute="_compute_delito_id", store=True)
	jurisdiccion_id = fields.Many2one( 'imco.norma.jurisdiccion', string='Jurisdiccion asociada', compute="_compute_jurisdiccion_id", store=True)
	delito_jurisdiccion_id = fields.Many2one( 'imco.norma.delitos.jurisdiccion', string='Relacion Delito - Jurisdiccion')
	#---------------------
	preguntas_ids = fields.One2many( 'imco.norma.delitos.jurisdiccion.entidades.requeridas.pre', 'delito_jurisdiccion_entidad_id',
		string='Preguntas disponibles para solicitar la entidad')

	@api.multi
	def get_random_question(self):
		self.ensure_one()
		return  random.choice(self.preguntas_ids)
#------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------
class imco_norma_delitos_jurisdiccion_entidades_requeridas_pre(models.Model):
	_name = "imco.norma.delitos.jurisdiccion.entidades.requeridas.pre"
	_description = 'Preguntas para obtener entidades requeridas de los delitos en las jurisdicciones'
	_order='delito_jurisdiccion_entidad_id asc, delito_id asc, jurisdiccion_id asc, sequence'

	@api.depends('delito_jurisdiccion_entidad_id')
	def _compute_delito_jurisdiccion_id(self):
		for r in self:
			try:
				r.delito_jurisdiccion_id = r.delito_jurisdiccion_entidad_id.delito_jurisdiccion_id.id
			except:
				pass

	@api.depends('delito_jurisdiccion_entidad_id')
	def _compute_delito_id(self):
		for r in self:
			try:
				r.delito_id = r.delito_jurisdiccion_entidad_id.delito_jurisdiccion_id.delito_id.id
			except:
				pass

	@api.depends('delito_jurisdiccion_entidad_id')
	def _compute_jurisdiccion_id(self):
		for r in self:
			try:
				r.jurisdiccion_id = r.delito_jurisdiccion_entidad_id.delito_jurisdiccion_id.jurisdiccion_id.id
			except:
				pass

	@api.depends('delito_jurisdiccion_entidad_id')
	def _compute_entidad_id(self):
		for r in self:
			try:
				r.entidad_id = r.delito_jurisdiccion_entidad_id.entidad_id.id
			except:
				pass

	name = fields.Char(string="Pregunta", required=True)
	sequence = fields.Integer(string='Secuencia')
	notas = fields.Text(string='Notas adicionales')
	#---------------------
	entidad_id = fields.Many2one( 'imco.norma.nltk.entidades', string='Entidad NLTK asociada', compute="_compute_entidad_id", store=True)
	delito_id = fields.Many2one( 'imco.norma.delitos', string='Delito asociado', compute="_compute_delito_id", store=True)
	jurisdiccion_id = fields.Many2one( 'imco.norma.jurisdiccion', string='Jurisdiccion asociada', compute="_compute_jurisdiccion_id", store=True)
	delito_jurisdiccion_id = fields.Many2one( 'imco.norma.delitos.jurisdiccion', string='Relacion Delito - Jurisdiccion',  compute="_compute_delito_jurisdiccion_id", store=True)
	delito_jurisdiccion_entidad_id = fields.Many2one( 'imco.norma.delitos.jurisdiccion.entidades.requeridas', string='Entidades requeridas para relacion Delito - Jurisdiccion')



#------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------
class imco_norma_delitos_jurisdiccion_variantes(models.Model):
	_name = "imco.norma.delitos.jurisdiccion.variantes"
	_description = 'Variantes de los delitos en las jurisdicciones'
	_order='delito_id asc, jurisdiccion_id asc, name'

	@api.depends('delito_jurisdiccion_id','jurisdiccion_id', 'delito_id')
	def _compute_name(self):
		for r in self:
			cad = ""
			try:
				cad += "[" + r.delito_jurisdiccion_id.delito_id.name + "]"
			except:
				pass
			try:
				cad += "[" + r.delito_jurisdiccion_id.jurisdiccion_id.name + "]"
			except:
				pass
			try:
				cad +=  " " + r.nombre_variante
			except:
				pass
			r.name = cad

	@api.depends('delito_jurisdiccion_id')
	def _compute_delito_id(self):
		for r in self:
			try:
				r.delito_id = r.delito_jurisdiccion_id.delito_id.id
			except:
				pass

	@api.depends('delito_jurisdiccion_id')
	def _compute_jurisdiccion_id(self):
		for r in self:
			try:
				r.jurisdiccion_id = r.delito_jurisdiccion_id.jurisdiccion_id.id
			except:
				pass

	name = fields.Char(string="Referencia", compute='_compute_name',  store=True)
	nombre_variante = fields.Char(string="Nombre de la variante", required=True)
	recomendacion = fields.Text(string="Recomendacion de la variante")
	notas = fields.Text(string='Notas adicionales')
	#---------------------
	delito_id = fields.Many2one( 'imco.norma.delitos', string='Delito asociado', compute="_compute_delito_id", store=True)
	jurisdiccion_id = fields.Many2one( 'imco.norma.jurisdiccion', string='Jurisdiccion asociada', compute="_compute_jurisdiccion_id", store=True)
	delito_jurisdiccion_id = fields.Many2one( 'imco.norma.delitos.jurisdiccion', string='Relacion Delito - Jurisdiccion')
	variantes_entidades_ids = fields.One2many( 'imco.norma.delitos.jurisdiccion.variantes.nltk.entidades', 'variante_id',
		string='Variantes de los delitos en las jurisdicciones')

#------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------
class imco_norma_delitos_jurisdiccion_variantes_nltk_entidades(models.Model):
	_name = "imco.norma.delitos.jurisdiccion.variantes.nltk.entidades"
	_description = 'Entidades requeridas en las variantes de los delitos en las jurisdicciones'
	_order='delito_id asc, jurisdiccion_id asc, entidad_id asc, valor'

	@api.depends('variante_id', 'delito_jurisdiccion_id','jurisdiccion_id', 'delito_id', 'entidad_id', 'valor')
	def _compute_name(self):
		for r in self:
			cad = ""
			try:
				cad += "[" + r.variante_id.delito_jurisdiccion_id.delito_id.name + "]"
			except:
				pass
			try:
				cad += "[" + r.variante_id.delito_jurisdiccion_id.nombre_variante+ "]"
			except:
				pass
			try:
				cad += "[" + r.variante_id.delito_jurisdiccion_id.jurisdiccion_id.name + "]"
			except:
				pass
			try:
				cad +=  " " + r.entidad_id.name
			except:
				pass
			try:
				cad +=  " " + r.valor
			except:
				pass
			r.name = cad

	@api.depends('variante_id')
	def _compute_delito_jurisdiccion_id(self):
		for r in self:
			try:
				r.delito_jurisdiccion_id = r.variante_id.delito_jurisdiccion_id.id
			except:
				pass

	@api.depends('variante_id')
	def _compute_delito_id(self):
		for r in self:
			try:
				r.delito_id = r.variante_id.delito_jurisdiccion_id.delito_id.id
			except:
				pass

	@api.depends('variante_id')
	def _compute_jurisdiccion_id(self):
		for r in self:
			try:
				r.jurisdiccion_id = r.variante_id.delito_jurisdiccion_id.jurisdiccion_id.id
			except:
				pass

	name = fields.Char(string="Referencia", compute='_compute_name',  store=True)
	valor = fields.Char(string="Valor de la entidad", required=True)
	notas = fields.Text(string='Notas adicionales')
	#---------------------
	entidad_id = fields.Many2one( 'imco.norma.nltk.entidades', string='Entidad NLTK asociada')
	delito_id = fields.Many2one( 'imco.norma.delitos', string='Delito asociado',
		compute="_compute_delito_id", store=True)
	jurisdiccion_id = fields.Many2one( 'imco.norma.jurisdiccion', string='Jurisdiccion asociada',
		compute="_compute_jurisdiccion_id", store=True)
	delito_jurisdiccion_id = fields.Many2one( 'imco.norma.delitos.jurisdiccion', string='Relacion Delito - Jurisdiccion',
		compute="_compute_delito_jurisdiccion_id", store=True)
	variante_id = fields.Many2one( 'imco.norma.delitos.jurisdiccion.variantes', string='Relacion Delito - Variante - Jurisdiccion')
