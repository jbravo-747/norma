# -*- coding: utf-8 -*-
{
	'name': "OPIT - IMCO - Analitica de APi",

	'summary': """
		Modulo para  analisis de API
		""",

	'description': """
		Modulo para analisis de API
	""",

	'author': "OPIT",
	'website': "http://opit.mx",
	'category': 'Uncategorized',
	'version': '0.1', 

	# any module necessary for this one to work correctly
	'depends': ['base','document', 'opit_imco_general'],
	
	# always loaded
	'data': [
		'security/security_api.xml', 
		'security/ir.model.access.csv', 

		'views/api/api.xml', 

		'menus/menus.xml', 
		'menus/menus_api.xml', 
		],
	# only loaded in demonstration mode
	'demo': [],
	'installable': True,
	'auto_install': False,
	'application': True,
}
