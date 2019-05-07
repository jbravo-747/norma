# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import sys, traceback
import logging

_logger = logging.getLogger(__name__)

class MailChannel(models.Model):
	_inherit = ['mail.channel']

	user_sms_id = fields.Many2one('imco.norma.sms.user',string="Usuario SMS")