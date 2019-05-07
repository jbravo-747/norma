# -*- coding: 850 -*-

from datetime import datetime, timedelta
from openerp import SUPERUSER_ID
from openerp import api, fields, models, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import UserError
from openerp.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import except_orm, Warning, RedirectWarning
import math
import pprint
import json

import hashlib
#from elasticsearch import Elasticsearch

#es = Elasticsearch(
#	['https://search-imco-scian-normatividad-lteh2ckcjd6cadqu5zujho3pta.us-west-2.es.amazonaws.com'],
#	port = 443,
#	use_ssl = True,
#	)
	
class imco_analitica_api(models.Model):
	_name = 'imco.analitica.api'
	_description = 'Solicitudes en API'
	_order = "date desc, accion asc"
	_rec_name = "url"
	
	proyecto = fields.Char(string='Proyecto asociado', required=True)
	accion = fields.Char(string='Accion', required=True)
	date = fields.Datetime(string="Fecha de evento") 
	url = fields.Char(string='URL', required=True)
	parametros = fields.Text('Parametros', default=True)
	resultado = fields.Text('Resultados', default=True)
	user_id = fields.Many2one('res.partner', string="Usuario")
	
	@api.model  
	def alta_llamada_ws_api(self, vals):
		v = {
			"proyecto" : vals["proyecto"],
			"url" : vals["url"],
			"accion" : vals["accion"],
			"date" : fields.datetime.now(),
			"parametros" : vals["parametros"],
			"resultado" : vals["resultado"],
			}
		return self.env["imco.analitica.api"].sudo().create(v) 
		
	@api.model  
	def create(self, vals):
		x = super(imco_analitica_api,self).create(vals)
		#obj_elastic={}
		#obj_elastic["id"] = x.id
		#obj_elastic["body"] = {}
		#obj_elastic["body"]["url"] = x.url
		#obj_elastic["body"]["accion"] = x.accion
		##print type(x.date), x.date
		#print "T".join(x.date.split(" "))
		#obj_elastic["body"]["date"] = "T".join(x.date.split(" "))
		#obj_elastic["body"]["parametros"] = json.loads(x.parametros)
		#obj_elastic["body"]["resultado"] = json.loads(x.resultado)
		## print ente_elastic
		#es.index(index="imco_api", doc_type="llamada_api", id=obj_elastic["id"], body=obj_elastic["body"])
		return x
	
	@api.multi
	def write(self, vals):
		x = super(imco_analitica_api,self).write(vals)
		#for r in self:
		#	obj_elastic["id"] = x.id
		#	obj_elastic["body"] = {}
		#	obj_elastic["body"]["url"] = x.url
		#	obj_elastic["body"]["accion"] = x.accion
		#	#obj_elastic["body"]["date"] = x.date.strftime('%Y/%m/%d %H:%M:%S')
		#	obj_elastic["body"]["date"] = x.date.split(" ")[0].replace("-", "/") + " T " + x.date.split(" ")[1]
		#	obj_elastic["body"]["parametros"] = json.loads(x.parametros)
		#	obj_elastic["body"]["resultado"] = json.loads(x.resultado)
		#	if es.exists(index="imco_api", doc_type="llamada_api", id=ente_elastic["id"]):
		#		es.update(index="imco_api", doc_type="llamada_api", id=ente_elastic["id"], body=ente_elastic["body"])
		#	else:
		#		es.index(index="imco_api", doc_type="llamada_api", id=obj_elastic["id"], body=obj_elastic["body"])
		return x
	    
	@api.multi
	def unlink(self):
		#for r in self:
		#	elastic_id = r.id
		#	if es.exists(index="imco_api", doc_type="llamada_api", id=elastic_id):
		#		es.delete(index="imco_api", doc_type="llamada_api", id=elastic_id)
		return super(imco_analitica_api, self).unlink()
	
		
		
		