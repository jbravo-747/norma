# -*- coding: utf-8 -*-
{
	'name': 'OPIT - IMCO - Modificacion Chat para Norma',
	'version': '1.0',
	'sequence': 170,
	'summary': 'Live Chat with Norma Robot',
	'category': 'Website',
	'complexity': 'easy',
	'website': 'https://opit.mx',
	'description':
	"""
		""",
		'data': [
			"views/res_partner.xml",
			"views/im_livechat_channel_views.xml",
			"views/im_livechat_channel_templates.xml"
		],
	'demo': [],
	'depends': ["mail", "im_livechat", "opit_imco_general", "opit_imco_norma"],
	'qweb': ['static/src/xml/*.xml'],
	'installable': True,
	'auto_install': False,
	'application': True,
}
