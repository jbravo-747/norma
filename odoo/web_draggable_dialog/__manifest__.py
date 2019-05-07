# -*- coding: utf-8 -*-
# Copyright (C) 2018 MAXSNS Corp (http://www.maxsns.com)
# @author Henry Zhou (zhouhenry@live.com)
# License OPL-1 - See https://www.odoo.com/documentation/user/11.0/legal/licenses/licenses.html
{
    'name': 'Web Draggable Dialog',
    'summary': 'Make backend dialog draggable for better user experience.',
    'description': """
        Make backend dialog draggable for better user experience.
        """,
    'author': "MAXSNS",
    'website': "http://www.maxsns.com",
    'category': 'Web',
    'version': '1.0.0',
    'images': ['static/description/banner.png'],
    'depends': ['web'],
    'data': [
        'views/assets.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,

    'license': 'OPL-1',
}
