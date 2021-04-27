# -*- coding: utf-8 -*-
{
	'name': 'OPIT - IMCO - Integración SMS',
	'version': '1.0',
	'sequence': 170,
	'summary': 'Live Chat with sms gateway',
	'category': 'Website',
	'complexity': 'easy',
	'website': 'http://opit.mx',
	'description':
	"""
		""",
		'data': [
			"security/security_sms.xml",
			"security/ir.model.access.csv",
				
			'views/mail_channel_view.xml',
			'views/sms_users_view.xml',
			
			'menus/menus.xml'
		],
	'demo': [],
	'depends': ["opit_imco_norma_chat", "im_livechat", "opit_imco_general"],
	'qweb': ['static/src/xml/*.xml'],
	'installable': True,
	'auto_install': False,
	'application': True,
}
