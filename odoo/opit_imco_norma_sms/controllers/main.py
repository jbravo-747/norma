# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64

from odoo import http, _
from odoo.http import request
from odoo.addons.base.ir.ir_qweb import AssetsBundle
from odoo.addons.web.controllers.main import binary_content
from odoo.addons.web.controllers.main import serialize_exception
import json


class SmsController(http.Controller):

	#@http.route(['/sms/receptor/','/sms/receptor/<gateway>'], type='http', auth='none', csrf=False)
	#@serialize_exception
	#def sms_receptor_json_temp(self,gateway='quiubas',**post):
	#	result =  json.dumps({
	#		'result':True, 
	#		"mensaje" : "xxx",
	#		"res_gateway" : "yyy",
	#		})
	#	print (result)
	#	return result
		
	@http.route(['/sms/receptor/','/sms/receptor/<gateway>'], type='json', auth='none', csrf=False)
	@serialize_exception
	def sms_receptor_json(self,gateway='quiubas',**post):
		print("JSON ...")
		user = None
		sms_data = None
		mensaje  = ""
		res_gateway = {}
		if post == {}:
			try:
				post=request.jsonrequest
			except:
				print ("REQUEST ...")
				print(request)
		if post != {}:
			print ("POST ...")
			print(post)
			if gateway=='quiubas':
				user = request.env['imco.norma.sms.user'].sudo().get_sms_user(post['source_addr'])
				sms_data={
					'message':post['message'],
					'user_id': user.id, 
					'gateway':gateway
					} 
			elif gateway=='nexmo':
				user = request.env['imco.norma.sms.user'].sudo().get_sms_user(post['msisdn'])
				sms_data={
					'message':post['text'],
					'date':post['message-timestamp'],
					'messageId':post['messageId'],
					'user_id': user.id,
					'gateway':gateway
				}
			print("SMS DATA ...")
			print(sms_data)
			#Registra el mensaje
			sms = request.env['imco.norma.sms.channel'].sudo().create(sms_data)
			#Revisa conversaciones abiertas (o inicializa nuevas)
			mail_channel = sms.sudo().check_channel_open()
			reply_messsage = sms.message_analysis(mail_channel)
			res_gateway = sms.message_send(reply_messsage)
		result =  json.dumps({
			'result':True, 
			"mensaje" : mensaje,
			"res_gateway" : res_gateway,
			})
		print("RESULT ...")
		print (result)
		return result
