import time
from odoo import fields, models, api
from odoo import fields
from odoo.tools.translate import _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import odoo.addons.decimal_precision as dp
from num2words import num2words
from datetime import datetime
from collections import Counter

#class of plot screen report
class site_report(models.Model):
    _name = 'site.report'
    name=fields.Many2one('projectsite.master','Project Site',required=True)

    project_site = None

    def onchange_name(self,pj_site):
        if pj_site:
            global project_site
            project_site = pj_site

    def print_report(self):
        global project_site
        ids[0] = project_site
        print (project_site, ids)

        return self.env['report'].get_action('construction_rewrite.site_report')

class offer_letter(models.AbstractModel):
    #_name = 'report.construction_plot_4devnet.final_provisional_letter_view_report'

    _name = 'report.final_provisional_letter_view_report'

    @api.multi
    def render_html(self, data=None):
        """Print the report."""
        # load the active_model from the file that was pickled earlier
        import pickle
        with open('active_model.pickle', 'rb') as f:
            model = pickle.load(f)

        report_obj = self.env['report']

        plot = self.env[model].browse(self.ids)

        # convert the date to human readable format
        ptime = datetime.strptime(plot.offer_dt.split(' ')[0], '%Y-%m-%d')
        offer_date = ptime.strftime("%d %B, %Y")

        if plot.offer_letter_reference_number:
            split = plot.offer_letter_reference_number.split('/')
            c_split = split[:]
            c_split.insert(1, plot.name.name[-4::1] if ' ' not in plot.name.name or 'city' in plot.name.name.lower() else plot.name.name[-5::1])
            reference_number_head = '/'.join(c_split)
            reference_number_body = split[1]
        else:
            reference_number_head, reference_number_body = ('', '')


        report = report_obj._get_report_from_name('construction_rewrite.final_provisional_letter_view_report')

        docargs = {
            'doc_ids': self._ids,
            'doc_model': model,
            'docs': plot,
            'offer_date': offer_date,
            'num2words': num2words,
            'reference_number_head': reference_number_head,
            'reference_number_body': reference_number_body
        }
        return report_obj.render('construction_rewrite.final_provisional_letter_view_report', docargs)


class bh_city_offer_letter(models.AbstractModel):
    #_name = 'report.construction_plot_4devnet.bh_city_offer_letter_report'
    _name = 'report.bh_city_offer_letter_report'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']

        plot = self.env['plot.allocate'].browse(self._ids)

        # convert the date to human readable format
        ptime = datetime.strptime(plot.offer_dt.split(' ')[0], '%Y-%m-%d')
        offer_date = ptime.strftime("%d %B, %Y")
        if plot.offer_letter_reference_number:
            split = plot.offer_letter_reference_number.split('/')
            c_split = split[:]

            plot_name = plot.name.name.lower()
            if ' ' in plot_name and 'city' in plot_name and 'galadimawa' not in plot_name:
                c_split.insert(1, plot_name[-4::1].upper())
            elif 'galadimawa' in plot_name:
                c_split.insert(1, plot_name[:3].upper())
            else:
                c_split.insert(1, plot_name[:5].upper())

            reference_number_head = '/'.join(c_split)
            reference_number_body = split[1]
        else:
            reference_number_head, reference_number_body = ('', '')


        report = report_obj._get_report_from_name('construction_rewrite.bh_city_offer_letter_report')

        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': plot,
            'offer_date': offer_date,
            'num2words': num2words,
            'reference_number_head': reference_number_head,
            'reference_number_body': reference_number_body
        }
        return report_obj.render('construction_rewrite.bh_city_offer_letter_report', docargs)

# TODO too much copy pasting refactor later, regex for reference_number
class galadimawa_carcas_offer_letter(models.AbstractModel):
    #_name = 'report.construction_plot_4devnet.galadimawa_carcas_offer_letter_report'
    _name = 'report.galadimawa_carcas_offer_letter_report'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']

        plot = self.env['plot.allocate'].browse(self._ids)

        # convert the date to human readable format
        ptime = datetime.strptime(plot.offer_dt.split(' ')[0], '%Y-%m-%d')
        offer_date = ptime.strftime("%d %B, %Y")
        if plot.offer_letter_reference_number:
            split = plot.offer_letter_reference_number.split('/')
            c_split = split[:]

            plot_name = plot.name.name.lower()
            if ' ' in plot_name and 'city' in plot_name and 'galadimawa' not in plot_name:
                c_split.insert(1, plot_name[-4::1].upper())
            elif 'galadimawa' in plot_name:
                c_split.insert(1, plot_name[:3].upper())
            else:
                c_split.insert(1, plot_name[:5].upper())

            reference_number_head = '/'.join(c_split)
            reference_number_body = split[1]
        else:
            reference_number_head, reference_number_body = ('', '')

        report = report_obj._get_report_from_name('construction_rewrite.galadimawa_carcas_offer_letter_report')

        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': plot,
            'offer_date': offer_date,
            'num2words': num2words,
            'reference_number_head': reference_number_head,
            'reference_number_body': reference_number_body
        }
        return report_obj.render('construction_rewrite.galadimawa_carcas_offer_letter_report', docargs)



# TODO too much copy pasting refactor later, regex for reference_number
class fish_offer_letter(models.AbstractModel):
    #_name = 'report.construction_plot_4devnet.fish_offer_letter_report'
    _name = 'report.fish_offer_letter_report'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']

        plot = self.env['plot.allocate'].browse(self._ids)

        # convert the date to human readable format
        ptime = datetime.strptime(plot.offer_dt.split(' ')[0], '%Y-%m-%d')
        offer_date = ptime.strftime("%d %B, %Y")
        if plot.offer_letter_reference_number:
            split = plot.offer_letter_reference_number.split('/')
            c_split = split[:]

            plot_name = plot.name.name.lower()
            if ' ' in plot_name and 'city' in plot_name and 'galadimawa' not in plot_name:
                c_split.insert(1, plot_name[25:29].upper())
            elif 'galadimawa' in plot_name:
                c_split.insert(1, plot_name[:3].upper())
            else:
                c_split.insert(1, plot_name[:5].upper())

            reference_number_head = '/'.join(c_split)
            reference_number_body = split[1]
        else:
            reference_number_head, reference_number_body = ('', '')

        report = report_obj._get_report_from_name('construction_rewrite.fish_offer_letter_report')

        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': plot,
            'offer_date': offer_date,
            'num2words': num2words,
            'reference_number_head': reference_number_head,
            'reference_number_body': reference_number_body
        }
        return report_obj.render('construction_rewrite.fish_offer_letter_report', docargs)


class receipt_number(models.Model):
    _name = 'receipt.number'
    _rec_name = 'receipt_number'

    payment = fields.Many2one('register.payment.wizard.for.plot', string='Payment')
    receipt_number = fields.Char(string='Receipt number')


class receipt(models.AbstractModel):
    #_name = 'report.construction_plot_4devnet.receipt_view_report'
    _name = 'report.receipt_view_report'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        payment = self.env['register.payment.wizard.for.plot'].browse(self.ids)

        # calculate the amount in words
        amount_in_words = num2words(payment.amount).capitalize()

        # convert the date to human readable format
        ptime = datetime.strptime(payment.date.split(' ')[0], '%Y-%m-%d')
        verbal_date = ptime.strftime("%B %d, %Y")

        # search for the plot in plot_allocate
        project_site = self.env['plot.allocate'].browse(payment.plot_id.id).name.name

        # get the receipt number
        receipt_number = self.env['receipt.number'].search([('payment', '=', self.id)]).receipt_number
        if not receipt_number:
            # if the receipt_number was not found create a new receipt number and save it
            receipt_number = self.env['ir.sequence'].get('receipt')

            receipt_dict = {}
            receipt_dict['receipt_number'] = receipt_number
            receipt_dict['payment'] = self.id
            self.env['receipt.number'].create(receipt_dict)

        # get the the payment kind (initial payment, additonal payment or final payment)
        plot = payment.plot_id
        payments = self.env['register.payment.wizard.for.plot'].search([('plot_id', '=', plot.id)])

        if payments[0].id != self.id:
            if int(plot.amount_dt) >= int(plot.offer_price) and payments[-1].id == self.id:
                payment_kind="final payment"

            elif len(payments) > 1 and int(plot.amount_dt) <= int(plot.offer_price):
                payment_kind = "additional payment"

        else:
            payment_kind = "inital payment"

        payment_kind = payment_kind.capitalize()
        report = report_obj._get_report_from_name('construction_rewrite.receipt_view_report')

        docargs = {
            'doc_ids': self.ids,
            'doc_model': report.model,
            'docs': payment,
            'project_site': project_site,
            'amount_in_words': amount_in_words,
            'verbal_date': verbal_date,
            'receipt_number': receipt_number,
            'payment_kind': payment_kind
        }
        return report_obj.render('construction_rewrite.receipt_view_report', docargs)

class total_payment_todate(models.AbstractModel):
    #_name='report.construction_rewrite.total_payment_todate'
    _name='report.total_payment_todate'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        payment_view_obj = self.env['register.payment.view.for.plot']
        payment_todate = payment_view_obj.browse(self.ids)

        # get the last payment
        payments = payment_view_obj.browse(self.ids).payment_line
        last_payment = payments[-1]

        # generate the receipt number
        receipt_number = self.env['ir.sequence'].get('receipt')

        #convert the date to a human readable date
        ptime = datetime.strptime(payments[-1].date.split(' ')[0], '%Y-%m-%d')
        verbal_date = ptime.strftime("%B %d, %Y")

        # set the other attributes
        customer = last_payment.plot_id.partner_id
        bank = last_payment.bank.bank_name
        plot_num = last_payment.plot_id.plot_no.plot_no
        project_site = last_payment.plot_id.name.name

        report = report_obj._get_report_from_name('construction_rewrite.total_payment_todate')

        docargs = {
            'doc_ids': self.ids,
            'doc_model': report.model,
            'docs': payment_todate,
            'customer': customer,
            'bank': bank,
            'verbal_date': verbal_date,
            'plot_num': plot_num,
            'project_site': project_site,
            'payments': payments,
            'receipt_number': receipt_number
        }

        return report_obj.render('construction_rewrite.total_payment_todate', docargs)

class site_report(models.AbstractModel):
    #_name = 'report.construction_plot_4devnet.site_report'
    _name = 'report.site_report'


    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']

        pj_site = self.env['projectsite.master'].browse(self._ids)

        # get the total amount for houses sold, average amount sold and number of houses sold
        sold_houses = self.env['plot.allocate'].search([('name', '=', pj_site.id), ('state', '=', 'allocation')])
        number_of_houses_sold = len(sold_houses)
        total_allocated = sum([plot.offer_price for plot in sold_houses])
        average_amount = total_allocated / (number_of_houses_sold if number_of_houses_sold !=0 else 1)

        #get the count of types of houses sold
        house_count = Counter([plot.build_type for plot in sold_houses])
        #sort according to the number of sales
        house_count = sorted(house_count.iteritems(), key=lambda x: x[1], reverse=True)

        print house_count

        print total_allocated, average_amount, number_of_houses_sold


        report = report_obj._get_report_from_name('construction_rewrite.site_report')

        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': [pj_site],
            'number_of_houses_sold': number_of_houses_sold,
            'total_allocated': total_allocated,
            'average_amount': average_amount,
            'house_count': house_count
        }
        return report_obj.render('construction_rewrite.site_report', docargs)
