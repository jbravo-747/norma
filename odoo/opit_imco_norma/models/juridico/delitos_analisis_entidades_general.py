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
import re
import json
import pprint


#action_delito_robo_perfil_genero
#action_delito_robo_perfil_edad
#action_delito_robo_perfil_repartidor
#action_delito_robo_perfil_discapacidad
#action_delito_robo_tiempo_hora
#action_delito_robo_tiempo_clima
#action_delito_robo_donde_municipio
#action_delito_robo_donde_lugar
#action_delito_robo_objeto_objeto
#action_delito_robo_objeto_monto
#action_delito_robo_pr_numero
#action_delito_robo_pr_arma
#action_delito_robo_pr_violencia
#action_delito_robo_pr_pr
#action_delito_robo_circunstancias_testigo
#action_delito_robo_circunstancias_camara
#action_delito_robo_policia_policia
#action_delito_robo_policia_tiempo
#action_delito_robo_policia_entrevista
#action_delito_robo_policia_cadena

class imco_norma_delitos_jurisdiccion_entidades_requeridas(models.Model):
	_inherit = "imco.norma.delitos.jurisdiccion.entidades.requeridas"

	def clean_text(self,text):
		cleanr = re.compile('<.*?>')
		cleantext = re.sub(cleanr, '', text)
		return cleantext.strip()

	def search_text_in_entidades_alias(self, text, codigo):
		sql = "SELECT distinct a.valor"
		sql += " FROM imco_norma_nltk_entidades e, imco_norma_nltk_entidades_alias a"
		sql += " WHERE e.id = a.entidad_id AND e.codigo = %s AND"
		sql += " to_tsvector('spanish', %s ) @@ to_tsquery('spanish', replace(a.name, ' ' , '_') ) OR"
		sql += " %s = a.name" 
		self.env.cr.execute(sql, (codigo, text, text) )
		r = self.env.cr.dictfetchall()
		if len(r) != 1:
			return False
		else:
			return r[0]["valor"]
	
	def analisis_mensaje_dialogflow_manejo_unknown(self, text, session_id, message=None, context = None):
		analisis = message.analisis_dialogflow(text = text, session_id = session_id, context = context) 
		if analisis["action"] == "input.unknown":
			codigo = context.split("_")[-1]
			sql = "SELECT distinct a.valor"
			sql += " FROM imco_norma_nltk_entidades e, imco_norma_nltk_entidades_alias a"
			sql += " WHERE e.id = a.entidad_id AND e.codigo = %s AND"
			sql += " to_tsvector('spanish', %s ) @@ to_tsquery('spanish', replace(a.name, ' ' , '_') ) OR"
			sql += " %s = a.name" 
			print(sql)
			self.env.cr.execute(sql, (codigo, text, text) )
			r = self.env.cr.dictfetchall()
			print(r)
			analisis["entidades"]  = {} 
			for x in r:
				print(x)
				if codigo not in analisis["entidades"]:
					analisis["entidades"][codigo] =  []
				analisis["entidades"][codigo].append(x["valor"])
		else:
			return analisis
		return analisis

	