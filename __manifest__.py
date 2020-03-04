{
    'name': 'Construction Management Applications',
    'version': '1.1',
    'category': 'management',
    'description': """

    The application enables you to manage different construction module rewrites.

Rewrite for :
==============
* Sales.
* Allocations.
* Constrcution.
* Branch.
* Commission.
    """,
    'author': 'Abdulkadir Haruna & Hafiz Abbas',
    'website': 'http://www.brainsandhammers.com',
    'depends': ['base', 'project', 'account', 'branch'],
    'data':[
            'security/security_groups.xml',
            'report/indicative_offer_letter.xml',
            'construction_view.xml',
            'report/new_report_template.xml',
            'report/new_report.xml',
            'report/offer_letter_view_report.xml',
            'report/final_provisional_letter_view.xml',
            'report/bh_city_offer_letter.xml',
            'report/galadimawa_carcas.xml',
            'report/fish.xml',
            'report/receipt.xml',
            'report/iganmu_final_provision_letter.xml',
            # 'report/site_reports.xml',
            'report/lagos_final_offer_letter.xml',
            'report/resale_provisional_letter_view.xml',
            'report/new_receipt_chris.xml',
            'report/offer_letter_lekki.xml',
            'report/finished_offer_bungalow_offer.xml',
            'report/lagos_receipt.xml',
            'report/total_payment_todate.xml',
            # 'report/final_provisional_letter_view_report.xml',
            'security/ir.model.access.csv',
            #'wizard/plot_report_views.xml',
            #'view.xml'
            ##'security/view_update.xml'
            ],
    ''''qweb': [
        'static/src/xml/base.xml',
    ],'''
    'installable': True,
    'auto_install': False,
    'application': True,
}
