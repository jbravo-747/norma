# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import random
import re
from datetime import datetime, timedelta
from odoo import api, fields, models, modules, tools

class ImLivechatChannel(models.Model):
	_inherit = 'im_livechat.channel'
	
	codigo_canal = fields.Char('Codigo de canal', default='') 
	
	# --------------------------
	# Channel Methods
	# --------------------------
	
	@api.multi
	def get_available_users(self):
		self.ensure_one()
		if self.sudo().codigo_canal == "norma":
			return self.env["res.users"].sudo().search([('codigo_chat','=','robot.norma')])
		else:
			return self.sudo().user_ids.filtered(lambda user: user.im_status == 'online')

	@api.model
	def get_mail_channel(self, livechat_channel_id, anonymous_name):
		# get the avalable user of the channel
		users = self.sudo().browse(livechat_channel_id).get_available_users()
		if len(users) == 0:
			return False
		# choose the res.users operator and get its partner id
		user = random.choice(users)
		operator_partner_id = user.partner_id.id
		# partner to add to the mail.channel
		channel_partner_to_add = [(4, operator_partner_id)]
		if self.env.user and self.env.user.active:  # valid session user (not public)
			channel_partner_to_add.append((4, self.env.user.partner_id.id))
		# create the session, and add the link with the given channel
		mail_channel = self.env["mail.channel"].with_context(mail_create_nosubscribe=False).sudo().create({
			'channel_partner_ids': channel_partner_to_add,
			'livechat_channel_id': livechat_channel_id,
			'anonymous_name': anonymous_name,
			'channel_type': 'livechat',
			'name': ', '.join([anonymous_name, user.name]),
			'public': 'private',
			'email_send': False,
		})
		return mail_channel.sudo().with_context(im_livechat_operator_partner_id=operator_partner_id).channel_info()[0]

	@api.model
	def get_channel_infos(self, channel_id):
		channel = self.browse(channel_id)
		return {
			'button_text': channel.button_text,
			'input_placeholder': channel.input_placeholder,
			'default_message': channel.default_message,
			"channel_name": channel.name,
			"channel_id": channel.id,
		}

	@api.model
	def get_livechat_info(self, channel_id, username='Visitante'):
		info = {}
		ch = self.env["im_livechat.channel"].sudo().search([("id","=",channel_id)], limit=1)
		if ch.codigo_canal == "norma":
			info['available'] = True
		else:
			info['available'] = len(self.browse(channel_id).get_available_users()) > 0
		info['server_url'] = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
		if info['available']:
			info['options'] = self.sudo().get_channel_infos(channel_id)
			info['options']["default_username"] = username
		return info

