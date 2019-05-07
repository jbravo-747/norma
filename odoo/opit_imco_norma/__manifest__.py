# -*- coding: utf-8 -*-
{
	'name': 'OPIT - IMCO - Modulo de administracion de  Norma',
	'version': '1.0',
	'summary': 'Modulo de administracion de Morma',
	'category': 'Others',
	'complexity': 'hard',
	'website': 'https://opit.mx',
	'description':
		"""
		""",
	'data': [
	 	"security/security_all.xml",
	 	"security/security_configuracion.xml",
	 	"security/security_juridico.xml",
	 	"security/security_mail.xml",
	 	"security/ir.model.access.csv",

		"views/juridico/entidades_requeridas.xml",
		"views/juridico/jurisdicciones.xml",
		"views/juridico/delitos.xml",
		"views/juridico/delitos_jurisdicciones_entidades_requeridas.xml",
		
		"views/mail/mail_channel.xml",

		"menus/menus.xml", 
		"menus/menus_mail_channel.xml",
		"menus/menus_juridico.xml",
		"menus/menus_analisis.xml",
	],
	'demo': [],
	'depends': ["mail","im_livechat","opit_imco_general"],
	'installable': True,
	'auto_install': False,
	'application': True,
}
