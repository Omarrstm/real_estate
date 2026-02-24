
{
    'name': 'Real Estate',
    'summary': 'Real Estate Module',
    'website': '',
    'depends': [
        'base','base_setup'
    ],
    'data': [ 
        'security/ir.model.access.csv',
        'views/estate_property_views.xml',
        'views/estate_menus.xml',
    ],
    'demo': [
        
    ],
    'installable': True,
    'application': True,
    'assets': {
        
    },
    'author': 'omar',
    'license': 'LGPL-3',

    'data': [
    'security/ir.model.access.csv',
    'views/estate_property_views.xml',
    'views/estate_property_type_views.xml',   
],

}
