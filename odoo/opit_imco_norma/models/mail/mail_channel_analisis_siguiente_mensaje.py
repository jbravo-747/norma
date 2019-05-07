# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, date
from pytz import timezone
from openerp import SUPERUSER_ID
from openerp import api, fields, models, _
import openerp.addons.decimal_precision as dp
from openerp.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import except_orm, Warning, RedirectWarning, UserError
from dateutil.parser import parse as parse_date
import random
import sys, traceback
import logging
import pprint

_logger = logging.getLogger(__name__)

class MailChannel(models.Model):
	_inherit = ['mail.channel']

	
	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	#Funcion de control en el flujo para obtencion del siguiente mensaje no predeterminado en la conversacion
	@api.multi
	def analizar_conversacion_siguiente_mensaje(self, message):
		variante = self.identifica_variante_delito_en_jurisdiccion()
		#Antes buscaba  identificar la variable para obtener la siguiente pregunta (buscaba la ultima entidad con valor conocido), 
		#ahora busca siempre la siguiente pregunta a traves de buscar el ultimo contexto dado de alta
		#(hasta que ya no haya mas entidades) 
		# Obtener id y codigo de la siguiente entidad requerida desde la DB
		sql  = " SELECT d.id as entidad_requerida_id, e.codigo as entidad_codigo  "
		sql += " FROM  imco_norma_nltk_entidades e, imco_norma_delitos_jurisdiccion_entidades_requeridas d "
		sql += " WHERE  "
		sql += " e.id = d.entidad_id AND "
		sql += " d.entidad_id not in (SELECT entidad_id FROM imco_norma_mail_analisis_nltk_entidades WHERE channel_id = %s) AND "
		sql += " d.entidad_id not in ("
		sql += " SELECT id FROM imco_norma_nltk_entidades WHERE "
		sql += " codigo IN ( SELECT replace(valor, 'entidad_','') FROM imco_norma_mail_analisis_nltk_contextos WHERE channel_id = %s)"
		sql += " ) AND "
		sql += " d.delito_id = %s AND "
		sql += " d.jurisdiccion_id = %s AND "
		sql += " d.tipo_analisis != 'previo' "
		sql += " ORDER BY sequence LIMIT 1;"
		self.env.cr.execute(sql,(self.id, self.id, self.delito_id.id, self.jurisdiccion_id.id, ))
		# Intentar asignar el valor contenido con el query y obtener la pregunta de la siguiente entidad requerida
		try:
			entidad_requerida_id, entidad_codigo = self.env.cr.fetchone()
			message.save_contexts_odoo(contextos = [ ("entidad_" + entidad_codigo) ], session_id = self.id)
			return self.env['imco.norma.delitos.jurisdiccion.entidades.requeridas'].browse([entidad_requerida_id]).get_random_question().name
		# Si falla significa que ya no hay mas entidades faltantes
		except:
			#Verifica si encontro la variante o no a la finalizacion de la conversacion
			if variante == False:
				self.write({ 'status'  : 'variante_sin_definir' })
			else:
				self.write({ 'status'  : 'finalizado_exitoso' })
			#return ("Lo siento, no pudimos identificar la modalidad de delito que has sufrido. Te prometo que me van a revisar para mejorar y que no se vuelva a repetir")
			return self.finaliza_conversacion(finaliza_prematuro = False)

	