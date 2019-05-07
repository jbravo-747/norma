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

#es = Elasticsearch(
#	['https://search-imco-scian-normatividad-lteh2ckcjd6cadqu5zujho3pta.us-west-2.es.amazonaws.com'],
#	port = 443,
#	use_ssl = True,
#	)

#--------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------
class imco_general_entes_geograficos(models.Model):
	_name = 'imco.general.entes.geograficos'
	_description = "Listado de Entes geograficos en Mexico"
	_order = 'tipo_ente asc, padre_id asc, name asc'

	name = fields.Char(string='Nombre del ente geografico', required=True, copy=False, index=True, default='')
	activo = fields.Boolean(string="Activo?", default=False)
	tipo_ente = fields.Selection([
		('sin_definir','Sin definir'),
		('federal','Pais'),
		('estado','Estado'),
		('municipio','Municipio'),
		], string='Tipo de ente', required=True, index=True, default='sin_definir')
	clave_completa = fields.Char(string='Clave completa', required=False, copy=False, index=True, default='')
	acronimo = fields.Char(string='Acronimo', required=False, copy=False, index=True, default='')
	clave_age = fields.Char(string='Clave AGE (Inegi)', required=False, copy=False, index=True, default='')
	padre_id = fields.Many2one('imco.general.entes.geograficos', required=False, string='Entidad padre')
	hijos_ids = fields.One2many('imco.general.entes.geograficos', 'padre_id', string='Entidades hijas')
	localidades_estado_ids = fields.One2many('imco.general.entes.sepomex.localidades', 'estado_id', string='Localidades si es estado')
	localidades_municipio_ids = fields.One2many('imco.general.entes.sepomex.localidades', 'municipio_id', string='Localidades si es municipio')
	alias_ids = fields.One2many('imco.general.entes.geograficos.alias', 'ente_id', string='Alias de la entidad')
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
				('acronimo', operator, name),
				'|',
				('padre_id.name', operator, name),
				('padre_id.acronimo', operator, name),
				]
		t = self.search(domain + args, limit=limit)
		return t.name_get()

	@api.multi
	@api.depends('name', 'padre_id')
	def name_get(self):
		result = []
		for t in self:
			cad = ""
			try:
				cad += "[" + t.tipo_ente + "]"
			except:
				pass
			
			if t.tipo_ente == "municipio":
				try:
					cad += "[" + t.padre_id.acronimo + "] "
				except:
					pass			
			try:
				cad += "[" + t.acronimo + "] "
			except:
				pass
			cad += t.name
			result.append( (t.id, cad) )
		return result

	@api.multi
	def cambio_activo(self):
		for r in self:
	#		ente_elastic={}
	#		ente_elastic["id"] = r.id
	#		ente_elastic["body"] = {}
	#		ente_elastic["body"]["doc"] = {}
			if r.activo == True:
				r.activo = False
	#			ente_elastic["body"]["doc"]["activo"] = False
			else:
				r.activo = True
	#			ente_elastic["body"]["doc"]["activo"] = True
	#		if es.exists(index="imco_general_entes_geograficos", doc_type="ente", id=ente_elastic["id"]):
	#			es.update(index="imco_general_entes_geograficos", doc_type="ente", id=ente_elastic["id"], body=ente_elastic["body"])

	#@api.onchange('name')
	#def check_change(self):
	#	ente_elastic={}
	#	ente_elastic["id"]=str(self.sector_id.id)+"-"+str(self.subsector_id.id)+"-"+str(self.rama_id.id)+"-"+str(self.id)
	#	ente_elastic["body"]={}
	#	ente_elastic["body"]["doc"]={}
	#	ente_elastic["body"]["doc"]["name"]=self.name
	#	if es.exists(index="imco_general_entes_geograficos", doc_type="ente", id=ente_elastic["id"]):
	#		es.update(index="imco_general_entes_geograficos", doc_type="ente", id=ente_elastic["id"], body=ente_elastic["body"])

	@api.model
	def search_query(self,vals):
		return False
	#	result = es.search(index="imco_general_entes_geograficos",body={"query": {		
	#		"multi_match" : {		  
	#			"query": vals['query'],		   
	#			"fields": [ "name" ]		
	#			}
	#		} })
	#	return result

	@api.model
	def create(self, vals):
		ente = super(imco_general_entes_geograficos,self).create(vals)
	#	ente_elastic={}
	#	ente_elastic["id"] = ente.id
	#	ente_elastic["body"] = {}
	#	ente_elastic["body"]["tipo_ente"] = ente.tipo_ente
	#	ente_elastic["body"]["name"] = ente.name
	#	ente_elastic["body"]["activo"] = False if ente.activo != True else True
	#	es.index(index="imco_general_entes_geograficos", doc_type="ente", id=ente_elastic["id"], body=ente_elastic["body"])
		return ente

	#@api.multi
	#def unlink(self):
	#	for r in self:
	#		elastic_id = r.id
	#		res = super(imco_general_entes_geograficos, self).unlink()
	#		if es.exists(index="imco_general_entes_geograficos", doc_type="ente", id=elastic_id):
	#			es.delete(index="imco_general_entes_geograficos", doc_type="ente", id=elastic_id)
	#		return res
			
	#@api.model
	#def search_omnibusqueda_entes(self, vals):
	#	res = {}
	#	res= es.search(index=vals['index'], body=vals["query"])
	#	res['resultado'] = 't' if res['hits']['total']>0 else 'f'
	#	return res

#--------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------
class imco_general_entes_geograficos_alias(models.Model):
	_name = 'imco.general.entes.geograficos.alias'
	_description = "Listado de Alias de Entes geograficos en Mexico"
	_order = 'ente_id asc, name asc'

	name = fields.Char(string='Alias del ente geografico', required=True, copy=False, index=True, default='')
	ente_id = fields.Many2one('imco.general.entes.geograficos', required=True, string='Ente geográfico asociado')
	
