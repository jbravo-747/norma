# -*- coding: utf-8 -*-
{
    'name': "OPIT - IMCO - Modulo General",

    'summary': """
        Modulo general con modificaciones para el IMCO
		""",

    'description': """
        Modulo con objetos generales a los proyectos utilizados por el IMCO
    """,

    'author': "OPIT",
    'website': "http://opit.mx",
    'category': 'Uncategorized',
    'version': '0.1', 

    # any module necessary for this one to work correctly
    'depends': ['base','document'],
	
    # always loaded
    'data': [
		'security/security.xml', 
		'security/security_all.xml', 
		'security/security_general_entidades.xml', 
		'security/ir.model.access.csv', 
		
		'views/entes/entes.xml', 
		'views/entes/sepomex.xml', 
		
		'menus/menus.xml', 
		'menus/menus_entes_geograficos.xml',
		
		],
    # only loaded in demonstration mode
    'demo': [],
	'installable': True,
	'auto_install': False,
	'application': True,
}
