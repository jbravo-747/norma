# -*- coding: utf-8 -*-
import pytz
import logging
from datetime import datetime, timedelta
from openerp import SUPERUSER_ID
from openerp import api, fields, models, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import UserError
from openerp.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT

import hashlib
#from elasticsearch import Elasticsearch

#--------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------
class imco_general_entes_sepomex_localidades(models.Model):
	_name = 'imco.general.entes.sepomex.localidades'
	_description = "Listado de localidades existentes en SEPOMEX"
	_order = 'estado_id asc, municipio_id asc, name asc'

	name = fields.Char(string='Nombre de la localidad', required=True, copy=False, index=True, default='')
	tipo_localidad = fields.Char(string='Tipo de la localidad', required=True, copy=False, index=True, default='')
	ciudad = fields.Char(string="Ciudad", default=False)
	cp = fields.Char(string="Codigo Postal", default=False)
	estado_id = fields.Many2one('imco.general.entes.geograficos', required=False, string='Entidad federativa asociada')
	municipio_id = fields.Many2one('imco.general.entes.geograficos', required=False, string='Municipio asociado')
	note = fields.Text('Notas Adicionales')

	@api.model
	def name_search(self, name, args=None, operator='ilike', limit=100):
		args = args or []
		domain = []
		if name:
			domain = [
				'|',
				('name', operator, name),
				'|',
				('cp', operator, name),
				'|',
				('estado_id.name', operator, name),
				('municipio_id.acronimo', operator, name),
				]
		t = self.search(domain + args, limit=limit)
		return t.name_get()

	@api.multi
	@api.depends('name', 'cp', 'estado_id', 'municipio_id')
	def name_get(self):
		result = []
		for t in self:
			cad = ""
			try:
				cad += "[" + t.cp + "]"
			except:
				pass
			try:
				cad +=  t.estado_id.name + " / "
			except:
				pass
			try:
				cad +=  " / " + t.municipio_id.name + " / "
			except:
				pass
			cad += t.name
			result.append( (t.id, cad) )
		return result

	
