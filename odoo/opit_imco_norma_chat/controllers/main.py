# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64

from odoo import http, _
from odoo.http import request
from odoo.addons.base.ir.ir_qweb import AssetsBundle
from odoo.addons.web.controllers.main import binary_content


class LivechatController(http.Controller):

	@http.route('/im_livechat/norma/external_lib.<any(css,js):ext>', type='http', auth='none')
	def livechat_lib(self, ext, **kwargs):
		# _get_asset return the bundle html code (script and link list) but we want to use the attachment content
		xmlid = 'opit_imco_norma_chat.external_lib'
		files, remains = request.env["ir.qweb"]._get_asset_content(xmlid, options=request.context)
		asset = AssetsBundle(xmlid, files, remains)
		mock_attachment = getattr(asset, ext)()
		if isinstance(mock_attachment, list):  # suppose that CSS asset will not required to be split in pages
			mock_attachment = mock_attachment[0]
		# can't use /web/content directly because we don't have attachment ids (attachments must be created)
		status, headers, content = binary_content(id=mock_attachment.id, unique=asset.checksum)
		content_base64 = base64.b64decode(content) if content else ''
		headers.append(('Content-Length', len(content_base64)))
		return request.make_response(content_base64, headers)

	@http.route('/im_livechat/norma/loader/<int:channel_id>', type='http', auth='public')
	def loader(self, channel_id, **kwargs):
		username = kwargs.get("username", _("Visitante"))
		channel = request.env['im_livechat.channel'].sudo().browse(channel_id)
		info = request.env['im_livechat.channel'].get_livechat_info(channel.id, username=username)
		return request.render('im_livechat.loader', {'info': info, 'web_session_required': True}, headers=[('Content-Type', 'application/javascript')])

	@http.route('/im_livechat/init', type='json', auth="public")
	def livechat_init(self, channel_id):
		LivechatChannel = request.env['im_livechat.channel']
		ch = LivechatChannel.browse(channel_id) 
		if ch.codigo_canal == "norma":
			available = True
		else:
			available = len(ch.get_available_users())
		rule = {}
		if available:
			# find the country from the request
			country_id = False
			country_code = request.session.geoip and request.session.geoip.get('country_code') or False
			if country_code:
				country_ids = request.env['res.country'].sudo().search([('code', '=', country_code)])
				if country_ids:
					country_id = country_ids[0].id
			# extract url
			url = request.httprequest.headers.get('Referer')
			# find the first matching rule for the given country and url
			matching_rule = request.env['im_livechat.channel.rule'].sudo().match_rule(channel_id, url, country_id)
			if matching_rule:
				rule = {
					'action': matching_rule.action,
					'auto_popup_timer': matching_rule.auto_popup_timer,
					'regex_url': matching_rule.regex_url,
				}
		return {
			'available_for_me': available and (not rule or rule['action'] != 'hide_button'),
			'rule': rule,
		}
	
	@http.route('/im_livechat/norma/<string:metodo_contacto>/get_session', type="json", auth='public')
	def get_session(self, metodo_contacto, channel_id, anonymous_name, **kwargs):
		# if geoip, add the country name to the anonymous name
		if request.session.geoip:
			anonymous_name = anonymous_name + " ("+request.session.geoip.get('country_name', "")+")"
		# if the user is identifiy (eg: portal user on the frontend), don't use the anonymous name. The user will be added to session.
		if request.session.uid:
			anonymous_name = request.env.user.name
		ch = request.env["im_livechat.channel"].with_context(lang=False).get_mail_channel(channel_id, anonymous_name)
		c = request.env["mail.channel"].sudo().search([('uuid','=',ch["uuid"])])
		c.sudo().write({"metodo_contacto": metodo_contacto})
		return ch

	#@http.route('/im_livechat/history', type="json", auth="public")
	#def history_pages(self, pid, channel_uuid, page_history=None):
	#	channel = request.env['mail.channel'].search([('uuid', '=', channel_uuid)])
	#	if channel:
	#		channel._send_history_message(pid, page_history)
	#	return True
