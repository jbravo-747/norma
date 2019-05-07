# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import dialogflow
import json
import os
import sys, traceback
import logging

_logger = logging.getLogger(__name__)


class mail_message(models.Model):
	_inherit = ['mail.message']

	#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	intent_action = fields.Char(string="DialogFlow - Intent") 
	analisis_entidades = fields.Text(string="DialogFlow - Analisis de contenido")
	messages_analisis_entidades_ids = fields.One2many('imco.norma.mail.analisis.nltk.entidades', 'message_id',
		string='DialogFlow - Entidades asociadas al mensaje')
	messages_analisis_contextos_ids = fields.One2many('imco.norma.mail.analisis.nltk.contextos', 'message_id',
		string='DialogFlow - Contextos asociados al mensaje')
	#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
