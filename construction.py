import time
from odoo import models, fields, api, _
from odoo.exceptions import except_orm, ValidationError
from odoo.tools import misc, DEFAULT_SERVER_DATETIME_FORMAT
from dateutil.relativedelta import relativedelta


'''import datetime
from datetime import timedelta'''
from datetime import datetime, timedelta

#import datetime
#from datetime import timedelta
class account_payment(models.Model):
    _inherit = "account.payment"

    #sal_payment_request_id = fields.Many2one('salary.request', string="Salary Ref")
    narration = fields.Text('Narration')
    @api.multi
    def post(self):
        """ Create the journal items for the payment and update the payment's state to 'posted'.
            A journal entry is created containing an item in the source liquidity account (selected journal's default_debit or default_credit)
            and another in the destination reconciliable account (see _compute_destination_account_id).
            If invoice_ids is not empty, there will be one reconciliable move line per invoice to reconcile with.
            If the payment is a transfer, a second journal entry is created in the destination journal to receive money from the transfer account.
        """
        #search_imprest_id = self.env['salary.request'].search([('id','=', self.sal_payment_request_id.id)])
        #search_imprest_id.write({'state':'post'})


        #email_from = self.env.user.email
        #email_to = search_imprest_id.employee_id.work_email
        #bodyx = "Dear Sir/Madam, </br>We wish to notify you that an imprest from {} is on payment process</br> </br>Thanks".format(search_imprest_id.employee_id.name)

        #search_imprest_id.mail_sending(email_from,email_to,bodyx)


        for rec in self:

            if rec.state != 'draft':
                raise UserError(_("Only a draft payment can be posted. Trying to post a payment in state %s.") % rec.state)

            if any(inv.state != 'open' for inv in rec.invoice_ids):
                raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))

            # Use the right sequence to set the name
            if rec.payment_type == 'transfer':
                sequence_code = 'account.payment.transfer'
            else:
                if rec.partner_type == 'customer':
                    if rec.payment_type == 'inbound':
                        sequence_code = 'account.payment.customer.invoice'
                    if rec.payment_type == 'outbound':
                        sequence_code = 'account.payment.customer.refund'
                if rec.partner_type == 'supplier':
                    if rec.payment_type == 'inbound':
                        sequence_code = 'account.payment.supplier.refund'
                    if rec.payment_type == 'outbound':
                        sequence_code = 'account.payment.supplier.invoice'
            rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(sequence_code)
            if not rec.name and rec.payment_type != 'transfer':
                raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))

            # Create the journal entry
            amount = rec.amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
            move = rec._create_payment_entry(amount)

            # In case of a transfer, the first journal entry created debited the source liquidity account and credited
            # the transfer account. Now we debit the transfer account and credit the destination liquidity account.
            if rec.payment_type == 'transfer':
                transfer_credit_aml = move.line_ids.filtered(lambda r: r.account_id == rec.company_id.transfer_account_id)
                transfer_debit_aml = rec._create_transfer_entry(amount)
                (transfer_credit_aml + transfer_debit_aml).reconcile()

            rec.write({'state': 'posted', 'move_name': move.name})

        search_allocatex = self.env['plot.allocatex'].search([('reference_number','=',self.communication)])
        for rex in search_allocatex:
            amount_allocatex = rex.amount_dt

            total_allocatex =rec.amount + amount_allocatex
            rex.write({'amount_dt':total_allocatex})


class project_project(models.Model):
    _inherit = "project.project"
    plot_ids = fields.Many2many('plot.allocatex', 'project_id',string = 'Plot')
    master_project = fields.Boolean('Master Project', default=False)

    @api.onchange('plot_ids')
    def onchange_Plot_id(self):
        self_s = self.search([('id','=',self.ids)])
        allocated_plot_id = []
        for project in self_s:
            project_data = self.browse([])
            for plot_id in project_data.plot_ids:
                allocated_plot_id.append(plot_id.id)
        for now_plot in plot_ids[0][2]:
            allocated_plot_id.append(now_plot)

        return {'domain': {'plot_ids': [('id', 'not in', allocated_plot_id)]}}


''''class Account_invoice(models.Model):
    _inherit = "account.invoice"


    @api.multi
    def name_get(self):
        if not self.ids:
            return []
        res=[]
        for field6 in self.browse(self.ids):
            name = field6.number
            nam = "Name-"+str(name)
            partner = "Customer" +field6.partner_id.name
            res.append((field6.id, "[ "+partner +"] -["+nam+" -["+str(field6.date_invoice)+"]"))
        return res
'''


class Account_Interface(models.Model):
    _name ='account.interfacex' #interface
    _rec_name ='journal_id'
    analytic_account = fields.Many2one('account.analytic.account', 'Analytic account')
    journal_id = fields.Many2one('account.journal', 'Account Journal', default=8)

class Account_Voucher(models.Model):
    _inherit = 'account.voucher'

class plot_allocate(models.Model):
    _name = 'plot.allocatex'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            res.append(
                (record.id,
                 record.plot_no.plot_no +
                 '-' +
                 record.phase if record.phase else record.plot_no.plot_no))
        return res


    @api.depends('offer_price', 'amount_dt')
    def _get_balance(self):
        for i in self:
            balance_x = i.offer_price - i.amount_dt
            i.balance = balance_x

    @api.depends('payment_invoice')
    def _get_invoice_fields(self):
        for order in self:
            if order.payment_invoice:

                offer_date = order.payment_invoice.date_invoice
                ref_num = order.payment_invoice.number
                payment_term = order.payment_invoice.payment_term_id
                payment_type = order.payment_invoice.payment_type
                branch = order.payment_invoice.branch_id
                partner_id = order.payment_invoice.partner_id
                agent_id = order.payment_invoice.agent
                law =order.payment_invoice.law
                origin = order.payment_invoice.origin
                #for ords in order.payment_invoice.invoice_line_ids[0]:
                project_site = order.payment_invoice.invoice_line_ids[0].product_id.categ_id.project_site
                order.update({'reference_number':ref_num,'payment_type':payment_type,'payment_plan':payment_term,'so_no':origin,'agents':agent_id,'partner_id':partner_id,'branch_id':branch,'name':project_site,'lawyer_id':law})# 'offer_price':offer_price})

    @api.depends('payment_invoice')
    def _get_invoice_fieldsx(self):
        invoice_lines = self.payment_invoice
        if invoice_lines:
            for inv_line in invoice_lines.invoice_line_ids:
                total = inv_line.price_subtotal
                self.offer_price += total



    @api.depends('payment_invoice')
    def _get_invoice_payments(self):
        #intervals = self.env['account.payment'].search([('communication','=',self.payment_invoice.number)])
        intervals = self.env['account.payment'].search([('communication','=',self.so_no)])
        if self.payment_invoice:
            total = 0.00
            #for inv_line in invoice_lines:
            for count, interval in enumerate(intervals):
                total += interval.amount
                self.amount_dt = total




    @api.multi
    def see_breakdown(self): #vis_account,
        return {
                'type':'ir.actions.act_window',
                'res_model':'account.payment',
                'res_id':self.id,
                'view_type':'tree',
                'view_mode':'tree',
                'target':'new',
                'domain': [('communication','=',self.so_no)]
    }



    @api.depends('plot_no')
    def _get_auto_field_product(self):

        for order in self:
            if order.plot_no:
                house_type = order.plot_no.house_type.name
                buil_type = order.plot_no.building_type.name
                #project_type = order.plot_no.project_site.id
                phase_id = order.plot_no.phase.name
                #offer_price = order.plot_no.offer_price
                order.update({'build_type':buil_type,'building':house_type,'phase':phase_id})

    def _get_branch(self):
        pass

        '''user_id = self.env.uid
        user_idx = self.env['res.users'].search([('id','=',user_id)])
        return user_idx.branch_id.id'''


    @api.onchange('branch_id')
    def change_project_site(self):
        if self.branch_id:
            search_project_branch = self.env['projectsite.masterx'].search([('branch_id','=',self.branch_id.id)])
            for order in search_project_branch:

                search_project = order.id
                self.name = search_project


    payment_invoice = fields.Many2one('account.invoice', string='Invoice ID',required =True, domain="[('state', '=', 'open')]")
    branch_id=fields.Many2one('res.branch', 'Branch', default=_get_branch, store=True )

    name = fields.Many2one('projectsite.masterx','Project Site', readonly=True, store=True)
    plot_no = fields.Many2one('unit.masterx', 'Plot Number')#,domain = [('project_site','=','name')])#, domain = [('status','=', 'unallocated')])
    build_type = fields.Char(string='Type of building',compute='_get_auto_field_product', store = True)
    building = fields.Char(string='House type',compute='_get_auto_field_product', store = True)
    phase = fields.Char(string='Phase',compute='_get_auto_field_product', store=True)
    reference_number = fields.Char('Ref. Number', compute ="_get_invoice_fields",store=True)
    offer_letter_reference_number = fields.Char('Offer Letter Ref Number')
    partner_id = fields.Many2one('res.partner', 'Primary Customer', required = True)
    current_owner_id = fields.Many2one('res.partner', 'Current Owner', required = False)
    lawyer_id = fields.Many2one('lawyer.model', 'Lawyer', required = True)
    offer_dt = fields.Date('Offer Date', default = fields.Date.today())
    deallocation_date = fields.Date('Deallocation date',default=lambda *a: (datetime.today() + relativedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S'))
    offer_price = fields.Float(string='Offer Amount',store=True, readonly=True, compute ="_get_invoice_fieldsx")
    payment_type = fields.Selection([('installment', 'Installment'),
            ('outright', 'OutRight Payment')],
            "Payment Type")
    so_no = fields.Char('Sale order No.',store=True, readonly=True,compute ="_get_invoice_fields")
    balance = fields.Float(string ='Balance', compute='_get_balance')
    amount_dt = fields.Float(string='Amount Paid', store=True, readonly=True, default=0.00,compute ="_get_invoice_payments")
    saleorder_exists = fields.Boolean(string='Saleorder')
    agent = fields.Many2one('agent.model', string='Agent')
    agents = fields.Many2one('res.partner', string='Agent')
    state = fields.Selection([('draft', 'Draft'),('first', 'Approved'),('reserved', 'Reserved'),
            ('deallocation', 'Deallocated'),
            ('allocation', 'Allocated')],'Status', default='draft')
    #count_total_payment = fields.Float(string = 'Total Payment')#, compute='_get_total_payment')
    payment_form_id = fields.Many2one('register.payment.view.for.plotx', 'Payment')
    active = fields.Boolean('Active', default = True)
    payment_plan = fields.Many2one('account.payment.term', 'Payment Terms')#, compute ="_get_invoice_fields")
    payment_breakdown = fields.One2many('plot.payment.breakdownx', 'project_and_plot_id', 'Payment Breakdown')
    resale_history = fields.One2many('re.salexxmain','plot_no','Resale History')
    description = fields.Text('Description')
    verified = fields.Boolean('Verified & Submitted to Board')


    @api.onchange('name')
    def get_project_list(self):
        domain = {}
        all_plot = []
        if self.name:
            search_plot= self.env['unit.masterx'].search([('project_site','=',self.name.id),('status','=','unallocated')])
            for all_ploter in search_plot:
                all_plot.append(all_ploter.id)
                domain = {'plot_no': [('id', '=', all_plot)]}

        return {'domain': domain}

    @api.onchange('branch_id')
    def filter_branch_project(self):

        domain = {}
        all_project = []
        if self.branch_id:
           search_projectsite = self.env['projectsite.masterx'].search([('branch_id', '=', self.branch_id.id)])
           for all_projects in search_projectsite:
               all_project.append(all_projects.id)
               domain = {'name':[('id', '=', all_project)]}
        return {'domain':domain}

    @api.onchange('branch_id')
    def filter_lawyer(self):

        domain = {}
        all_lawyer = []
        if self.branch_id:
           search_lawyer = self.env['lawyer.model'].search([('branch_id', '=', self.branch_id.id)])
           for all_lawyers in search_lawyer:
               all_lawyer.append(all_lawyers.id)
               domain = {'lawyer_id':[('id', '=', all_lawyer)]}
        return {'domain':domain}

    '''@api.onchange('partner_id')
    def get_partner_inovices(self):
        domain = {}
        all_partner = []
        if self.partner_id:

            search_partner_invoice =self.env['account.invoice'].search([('partner_id','=',self.partner_id.id)])
            if search_partner_invoice:
                for all_partners in search_partner_invoice:
                    all_partner.append(all_partners.id)
                    domain = {'payment_invoice':[('id','=', all_partner)]}
            else:
                domain = {'payment_invoice':[]}
        return {'domain': domain}     '''




    @api.onchange('plot_no', 'offer_price', 'amount_dt')
    def onchange_amount_dt(self):
        if self.plot_no:
            balance = self.offer_price - self.amount_dt
            self.balance = balance

    '''@api.multi
    def print_lagos_receipt(self):
        so_loc = self.name
        get_loc_name = so_loc.location
        loc_name = str(get_loc_name)  #total_lagos_payment_todate
        if loc_name == "abj":
            return self.env['report'].get_action(self.id,'construction_rewrite.lekki_offer_letter_view_report')

        elif loc_name == "los":
            return self.env['report'].get_action(self.id,'construction_rewrite.iganmu_letter_view_report')

        elif loc_name == "kan":
            return self.env['report'].get_action(self.id,'construction_rewrite.iganmu_letter_view_report')
        else:
            return self.env['report'].get_action(self.id,'construction_rewrite.final_provisional_letter_view_report')'''

    '''@api.onchange('payment_plan')
    def onchange_payment_plan(self):#, payment_plan, offer_price,offer_dt):
        if self.payment_plan:
            intervals = self.env['account.payment.term.line'].search([('payment_id', '=', self.payment_plan)])
            incr_interval = 0
            # parse and convert the date to a python datetime date
            offer_dt = datetime.strptime(self.offer_dt, "%Y-%m-%d")
            for count, interval in enumerate(
                self.env['account.payment.term.line'].browse(intervals)):
                print(
                    count,
                    interval.days,
                    interval.value_amount *
                    self.offer_price,
                    offer_dt +
                    timedelta(
                        days=incr_interval))
                incr_interval += interval.days '''





    def get_allocation_followers(self):
        pass


    @api.multi
    def button_first(self):
        for plot in self:
            self.write({'state':'first'})
            plot_no = plot.plot_no.plot_no
            body ="New offer for plot %s awaiting approval" %plot_no
            self.message_post(body=body)

    @api.multi
    def button_allocation(self):
        for plot in self:
            self.write({'state':'allocation'})
            plot_no = plot.plot_no.plot_no
            body ="Plot %s was approved" %plot_no
            self.message_post(body=body)

    @api.multi
    def print_final_allocation_letter(self):
        body = "%s Printed an offer letter" %self.env.user.name
        self.message_post(body=body)
        report = self.env["ir.actions.report.xml"].search([('report_name','=','construction_rewrite.final_provisional_letter_view_report')],limit=1)
        '''if report:
            report.write({'report_type':'qweb-pdf'})
        return self.env['report'].get_action(self.id, 'construction_rewrite.final_provisional_letter_view_report')    '''

        plot = self

        plot_name = self.name.name.lower()
        if 'fish' in plot_name:
            return self.env['report'].get_action(self.id,'construction_rewrite.fish_letter_report_document')

        elif 'city' in plot_name:
            return self.env['report'].get_action(self.id,'construction_rewrite.bh_city_offer_letter_report_document')


        elif 'carcas' in plot_name:
            return self.env['report'].get_action(self.id,'construction_rewrite.galadimawa_carcas_offer_letter_report_document')
        else:
            return self.env['report'].get_action(self.id,'construction_rewrite.new_offer_letter_report_document')


    @api.multi
    def print_indicative_allocation_letter(self):
        body = "%s Printed an offer letter" %self.env.user.name
        self.message_post(body=body)
        report = self.env["ir.actions.report.xml"].search([('report_name','=','construction_rewrite.final_provisional_letter_view_report_indicative')],limit=1)
        if report:
            report.write({'report_type':'qweb-pdf'})
        return self.env['report'].get_action(self.id, 'construction_rewrite.final_provisional_letter_view_report_indicative')


    @api.multi
    def register_payment(self):
        return {
                'type':'ir.actions.act_window',
                'res_model':'register.payment.wizard.for.plotx',
                #'res_id':self.id,
                'view_type':'form',
                'view_mode':'form',
                'target':'new',
                'context': {
                    'default_plot_id': self.id,
                    'default_customer': self.partner_id.id,
                    'default_project_name': self.name.name

                    },
                #'domain': [('fieldx1','=', self.field1)]
    }

    def calc_payment_plan(self, offer_dt, payment_plan):
        """Calculate the payment plan based on percentage."""
        intervals = self.env['account.payment.term'].search([('id', '=', payment_plan)])

        # parse and convert the date to a python datetime date
        offer_dt = datetime.strptime(offer_dt, '%Y-%m-%d')

        #for count, interval in enumerate(intervals):
        for interval in intervals.line_ids:
            due_date = offer_dt + timedelta(interval.days)
            value_amount = interval.value_amount
            interval_payment = interval.value
            amount_to_pay = 0.00
            # compute the amount_to_pay based on the type of payment
            if interval_payment == 'percent':  # procent ==> percent
                amount_to_pay = value_amount * self.offer_price / 100

            elif interval_payment == 'fixed':
                amount_to_pay = value_amount

            values = {
                'project_and_plot_id': self.id,
                'name': 'Payment Breakdowns',
                'interval': str(interval.days) + ' days',
                'amount_to_pay': amount_to_pay,
                'due_date': due_date.strftime('%Y-%m-%d')
            }
            self.env['plot.payment.breakdownx'].create(values)


    def calc_payment_plan_two(self):
        """Calculate the payment plan based on percentage."""
        intervals = self.env['account.payment.term'].search([('id', '=', self.payment_plan.id)])

        # parse and convert the date to a python datetime date
        offer_dt = datetime.strptime(self.offer_dt, '%Y-%m-%d')

        #for count, interval in enumerate(intervals):
        for interval in intervals.line_ids:
            due_date = offer_dt + timedelta(interval.days)
            value_amount = interval.value_amount
            interval_payment = interval.value
            amount_to_pay = 0.00
            # compute the amount_to_pay based on the type of payment
            if interval_payment == 'percent':  # procent ==> percent
                amount_to_pay = value_amount * self.offer_price / 100

            elif interval_payment == 'fixed':
                amount_to_pay = value_amount

            values = {
                'project_and_plot_id': self.id,
                'name': 'Payment Breakdowns',
                'interval': str(interval.days) + ' days',
                'amount_to_pay': amount_to_pay,
                'due_date': due_date.strftime('%Y-%m-%d')
            }
            self.env['plot.payment.breakdownx'].create(values)

    @api.model
    def create(self, vals):
        offer_dt = vals.get('offer_dt')
        offer_price = vals.get('offer_price')
        plot_no = vals.get('plot_no')
        payment_plan = vals.get('payment_plan')
        # generate and store the offer letter reference number
        vals['offer_letter_reference_number'] = self.env['ir.sequence'].get('offer_letter_reference_number')
        # override creation method to prevent creation of duplicate plots
        if plot_no:
            plot_no_duplicate = self.search([('plot_no', '=', plot_no)])
            if plot_no_duplicate:
                raise ValidationError('Duplicate! Plot No is allocated or is open for allocation already')

        # change status of unallocated plots to allocated in unit_master
        unit_master = self.env['unit.masterx'].browse(plot_no)
        # change corresponding plot in unit_master to allocated
        unit_master.write({'status': 'allocated'})
        project_and_plot_id = super(plot_allocate, self).create(vals)
        plot = project_and_plot_id
        if payment_plan:
            plot.calc_payment_plan(offer_dt, payment_plan)
        return project_and_plot_id

    @api.multi
    def write(self, vals):
        plot = self
        offer_dt = vals.get('offer_dt') or plot.offer_dt
        payment_plan = vals.get('payment_plan')
        payment_type = vals.get('payment_type')
        payment_plan_ids = self.env['plot.payment.breakdownx'].search([('project_and_plot_id', '=', self.id)])
        if payment_plan:
            if payment_plan_ids:
                payment_plan_ids.unlink()
                self.calc_payment_plan(offer_dt, payment_plan)
            else:
                self.calc_payment_plan(offer_dt, payment_plan)
        # clear payment_breakdown when payment is changed to outright
        if payment_type and payment_plan_ids and payment_type == 'outright':
            payment_plan_ids.unlink()
            vals['payment_type'] = 'outright'
        elif payment_type == 'installment':
            self.calc_payment_plan_two()
        val = super(plot_allocate, self).write(vals)
        return val




class Register_Payment_View_Plot(models.Model):
    _name = 'register.payment.view.for.plotx'
    name = fields.Char('Name')
    plot_id = fields.Many2one('plot.allocatex', 'Payment For', required=True)
    customer = fields.Many2one('res.partner', 'Customer', required=True)
    payment_line = fields.One2many('register.payment.wizard.for.plotx', 'payment_view_id', string="Payments")
    @api.model
    def create(self,vals):
        response = super(Register_Payment_View_Plot, self).create(vals)

        plot_id = vals.get('plot_id')
        customer = vals.get('customer')
        customer_data = self.env['res.partner'].search([('id','=',customer)])
        plot_data = self.env['plot.allocatex'].search([('plot_id', '=',plot_id)])
        name = str(customer_data.name) +"Payment Summary For"+ str(plot_data.building)
        vals['name'] = name
        return response


    @api.multi
    def print_offer_payment_statement(self):
        return self.env['report'].get_action(self.id, 'construction_rewrite.total_payment_todate')#construction_plot_4devnet.total_payment_todate

    @api.multi
    def print_offer_payment_statement(self):
        return self.env['report'].get_action(self.id, 'construction_rewrite.verification')


class Register_Payment_Wizard_For_Plot(models.Model):
    _name ='register.payment.wizard.for.plotx'
    payment_view_id = fields.Many2one('register.payment.view.for.plotx', string="Payment form")
    name = fields.Char('Name')
    plot_id=fields.Many2one('plot.allocatex', 'Payment For')
    customer=fields.Many2one('res.partner', 'Customer')
    bank = fields.Many2one('res.partner.bank', 'Bank')
    payment_for=fields.Many2one('account.interfacex', 'Account journal', required=True)
    date=fields.Datetime('Date and time of payment') #default= fields.datetime.now)
    amount = fields.Float('Paid Amount')
    payment_type = fields.Text('Narration')
    project_name = fields.Char('Project name')

    @api.multi
    def button_pay(self):
        print "##", "pay"
        return{'type': 'ir.actions.act_window_close'}

    @api.multi
    def print_receipt(self):
        return self.env['report'].get_action(self.id, 'construction_rewrite.receipt_view_report')
#search
    @api.model
    def create(self,vals):
        res = super(Register_Payment_Wizard_For_Plot).create(vals)
        plot_data = self.plot_id
        amount = vals.get('amount')
        date = vals.get('date')
        account_interface = vals.get('payment_for')
        name = "NGN" +str(int(amount))+"Paid for"+str(plot_data.building)
        self.write({'name':name})
        receipt = {}
        receipt['receipt_number']=self.env['ir.sequence'].get('receipt')
        receipt['payment']= res
        self.env['receipt.number'].create(receipt)

        if account_interface:
            account_interface = self.env['account.interfacex']
    	analytic_account_id = account_interface.analytic_account.id
    	account_id=account_interface.journal_id.default_credit_account_id.id
    	journal_id = account_interface.journal_id.id
    	date = date.split()[0].split('-')
        date = '/'.join(date[1::-1])
    	#period_id = self.env['account.period'].search([('code','=',date)])
    	payments = {
    		'analytic_id': analytic_account_id,
                    'account_id': account_id,
                    'new_analytic_id': analytic_account_id,
                    'partner_id': vals.get('customer'),
                    'amount': amount,
                    'journal_id': journal_id,
                    # will raise an IndexError exception if no period was found
                    #'period_id': period_id[0],
                    'reference': 'PF ' + plot_data.plot_no.plot_no,
                    'type': 'receipt'
                }
    	self.env['account.voucher'].create(payments)
    	if plot_data.offer_dt != plot_data.deallocation_date:
    	    plot_data.deallocation_date = plot_data.offer_offer_dt
    	else:
    	    raise orm_except(_('Please configure account interface'),_('You have not configured the right interface for'))
    	return res
class Plot_Payment_Breakdown(models.Model):
    _name = 'plot.payment.breakdownx' # breakdown
    project_and_plot_id =fields.Many2one('plot.allocatex', 'Plot Number')
    name =fields.Char('Payment')
    interval =fields.Char('Payment Interval in days')
    amount_to_pay=fields.Float('Amount to be paid')
    due_date=fields.Datetime('Due date')
    @api.multi
    def print_receipt(self):
        return self.env['report'].get_action(self.id, 'construction_rewrite.receipt_view_report')# allocate construction_plot_4devnet.receipt_view_report


class Title_Documents(models.Model):
    _name = 'title.documentsx'

    customer =fields.Many2one('res.partner', 'Customer', required=True)
    project_site= fields.Many2one('projectsite.masterx', 'Project Site', required=True)
    plot_no= fields.Many2one('unit.masterx', 'Plot Number', domain="[('status', '=', 'allocated')]", required=True)
    completed_documentation= fields.Selection([('yes', 'Yes'), ('no', 'No')], 'Completed documentation')
    completed_payment=fields.Selection([('yes', 'Yes'), ('no', 'No')], 'Completed payment')
    vat_payment=fields.Selection([('yes', 'Yes'), ('no', 'No')], 'VAT Payment')

    @api.multi
    def print_deed_of_sublease(self):
        return self.env['report'].get_action(self.id, 'construction_rewrite.offer_letter_view_report')#construction_plot_4devnet.offer_letter_view_report

# inherited models to make ACL easier
class Res_Partner(models.Model):
    _inherit='res.partner'


class Unit_Master(models.Model):
    _name = 'unit.masterx'
    _rec_name = 'plot_no'

    _sql_constraints = [
        ('combo', 'unique(project_site, plot_no, phase)', 'Error: Duplicate Project site, plot number and phase found'),
    ]

    project_site = fields.Many2one('projectsite.masterx', 'Project Site',required=True)
    building_type = fields.Many2one('buildingtype.masterx', 'Building Type', required=True)
    house_type = fields.Many2one('building.masterx', 'House Type', required=True)
    plot_no = fields.Char('Plot Number', required=True)
    offer_price = fields.Float('Offer Price', required=True)
    status= fields.Selection([('reserved', 'Reserved'),('unallocated', 'Unallocated'),('allocated', 'Allocated')],'Status', required=True, default ="unallocated" )
    phase = fields.Many2one('phase.masterx', 'Phase')#,default =1)
    block_no = fields.Many2one('block.masterx', 'Block No')
    investor = fields.Many2one('investor.masterx', 'Investor', required=True)
    analytic_account = fields.Many2one('project.project', domain="[('master_project', '=', False)]", string='Analytic account')


class ProjectSiteMaster(models.Model):
    _name = 'projectsite.masterx'
    name = fields.Char('Project Site', required = True)
    #site_plan = fields.Binary('Site Plan')
    location= fields.Selection([('kan', 'Kano'),('los', 'Lagos'),('abj', 'Abuja')],'Status', required=True, default ="abj" )
    branch_id=fields.Many2one('res.branch', 'Branch')



class Buildingtype_Master(models.Model):
    _name = 'buildingtype.masterx'
    name = fields.Char('Type of Building', required = True)

class Building_Master(models.Model):
    _name = 'building.masterx'
    name = fields.Char('Building', required = True)

class Phase_Master(models.Model):
    _name = 'phase.masterx'
    name = fields.Char('Phase', required = True)

class Block_Master(models.Model):
    _name = 'block.masterx'
    name = fields.Char('Block No', required = True)

class Block_Master(models.Model):
    _name = 'investor.masterx'
    name = fields.Char('Investor', required = True)


class Plot_Deallocate(models.Model):
    _name = 'plot.deallocatex'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    plot_no = fields.Many2many('plot.allocatex', 'deallocate_and_plot', 'deallocate_id', 'plot_no', 'Select plot')
    reason = fields.Char('Reason', required=True)
    state = fields.Selection([('draft', 'Draft'),('approved', 'Approved')], 'Status', default='draft')
    @api.multi
    def unlink(self):
        for d in self:
            plot_no = d.plot_no.id
            plot_no.unlink()
        return True


    @api.multi
    def button_approve(self):
        plot_allocate = self.env['plot.allocatex'].search([('id','=', self.plot_no.id)])
        for plot in self.plot_no:
            plot_allocate.write({'state':'deallocation'})#, 'active':False})
            unit_master_id = plot.plot_no.id
            unit_dae = self.env['unit.masterx'].browse(unit_master_id) #unit_dae = self.env['unit.masterx'].search([('id', '=',unit_master_id)])
            unit_dae.write({'status':'unallocated'})
            body = "%s deallocated %s" %(self.env.user.name, plot.plot_no.plot_no)
            self.message_post(body=body)

        self.write({'state':'approved'})


class Price_Review(models.Model):
    _name = "price.reviewx"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _rec_name = 'project_site'
    project_site = fields.Many2one('projectsite.masterx', 'Project Site',required=True)
    building_type = fields.Many2one('buildingtype.masterx', 'Building Type', required=True)
    house_type = fields.Many2one('building.masterx', 'House Type', required=True)
    current_price = fields.Many2one('Current Price')
    status = fields.Selection([('saved', 'Saved')], 'Status')
    phase = fields.Many2one('phase.masterx', 'Phase')
    investor =fields.Many2one('investor.masterx', 'Investor')
    @api.model
    def create(self, vals):
        project_site = vals.get('project_site')
        building_type = vals.get('building_type')
        house_type = vals.get('house_type')
        current_price = vals.get('current_price')
        plots= self.env['unit.masterx'].search(
            [
                '&',('project_site','=',project_site),('building_type','=',building_type),
                '&',('house_type','=',house_type), ('status', '=','unallocated')])
        vals['status']='saved'
        price_review_id = super(Price_Review, self).create(vals)
        for plot in plots:
            plot.offer_price = current_price

        return price_review_id




class Re_Salexmain(models.Model):
    _name = "re.salexxmain"
    name = fields.Many2one('projectsite.masterx','Project Site',required=False)
    plot_no = fields.Many2one('plot.allocatex','Plot Number',required=False,domain=[('state','=','allocation')], help="Plot no")
    #source_cust= fields.Many2one('res.partner', 'Primary(Customer)',required=False)
    #purpose = fields.Char('Purpose')
    #appl_deduct = fields.Selection([('yes','Yes'),('no','No')],'Applied Deduction(Yes/No)', default = 'yes')
    resale_fee= fields.Float('Resale Fee in %', default=1.00)
    amount_dt = fields.Float('Amount Paid')
    offer_price = fields.Float('Offer Price')
    status = fields.Selection([('paid', 'Paid'),
            ('notpaid', 'Not Paid')],
            "Status")
    date = fields.Date('Date', default = fields.Date.today())
    payment_type = fields.Selection([('installment', 'Installment'),
            ('outright', 'OutRight Payment')],
            "Payment Type")
    payment_plan = fields.Many2one('account.payment.term', 'Payment Terms')#, compute ="_get_invoice_fields")
    dest_cust= fields.Many2one('res.partner', 'Secondary(Customer)',required=False)
    bank= fields.Many2one('res.partner.bank', 'Bank',required=False)
    name = fields.Many2one('projectsite.masterx','Project Site',required=False)

    @api.multi
    def write(self, vals):
        plot = self
        offer_dt = vals.get('date') or plot.date
        payment_plan = vals.get('payment_plan')
        payment_type = vals.get('payment_type')
        secondary_customer = vals.get('dest_cust') or plot.dest_cust
        payment_plan_ids = self.env['plot.allocatex'].search([('resale_history', '=', self.id)])
        if payment_plan:
            if payment_plan_ids:
                payment_plan_ids.write({'current_owner_id':secondary_customer})
        val = super(Re_Salexmain, self).write(vals)
        return val





    @api.multi
    def print_resale_letter(self):
        #body = "%s Printed an offer letter" %self.env.user.name
        #self.message_post(body=body)
        report = self.env["ir.actions.report.xml"].search([('report_name','=','construction_rewrite.resale_letter_view_report')],limit=1)
        if report:
            report.write({'report_type':'qweb-pdf'})
        return self.env['report'].get_action(self.id, 'construction_rewrite.resale_letter_view_report')



    '''@api.onchange('plot_no')
    def onchange_plot_id(self):


        plot= self.env['plot.allocatex'].search([('id','=',self.plot_no.id)])


        for order in self:
            if order.plot_no:
                #order.source_cust = plot.partner_id.id
                order.name = plot.name.id
                order.amount_dt = plot.amount_dt
                #order.balance = plot.balance'''


class Re_Sale(models.Model):
    _name = "re.salexx"
    name = fields.Many2one('projectsite.masterx','Project Site',required=False)
    plot_no = fields.Many2one('plot.allocatex','Plot Number',required=False,domain=[('state','=','allocation')], help="Plot no")
    source_cust= fields.Many2one('res.partner', 'Primary(Customer)',required=False)
    purpose = fields.Char('Purpose')
    appl_deduct = fields.Selection([('yes','Yes'),('no','No')],'Applied Deduction(Yes/No)', default = 'yes')
    resale_fee= fields.Float('Resale Fee in %', default=1.00)
    amount_dt = fields.Float('Amount Paid')
    balance = fields.Float('Balance')
    dest_cust= fields.Many2one('res.partner', 'Secondary(Customer)',required=False)




    @api.onchange('plot_no')
    def onchange_plot_id(self):


        plot= self.env['plot.allocatex'].search([('id','=',self.plot_no.id)])


        for order in self:
            if order.plot_no:
                order.source_cust = plot.partner_id.id
                order.name = plot.name.id
                order.amount_dt = plot.amount_dt
                order.balance = plot.balance

    '''@api.model
    def create(self, vals):
        plot= self.env['plot.allocatex'].search([('id','=',self.plot_no.id)])
        #plot_no = vals.get('plot_no')
        #source_cust = vals.get('source_cust')
        #dest_cust = vals.get('dest_cust')
        plot_no =  self.plot_no.id
        source_cust = self.source_cust.id
        dest_cust = self.dest_cust.id
        plot.write({'partner_id':dest_cust})
        return super(Re_Sale, self).create(vals)   '''


    @api.model
    def create(self,vals):
        xxx= vals.get('plot_no')
        dest_cust=vals.get('dest_cust')
        plot = self.env['plot.allocatex'].search([('id','=',xxx)])

        record = super(Re_Sale,self).create(vals)
        #record['amount_dt']  = plot.id
        plot.write({'partner_id':dest_cust})

        return record

class Plot_Revocate(models.Model):
    _name = 'plot.revocatex'
    name = fields.Many2one('projectsite.masterx','Project Site',required=True)
    plot_no = fields.Many2one('plot.allocatex','Plot Number',required=True,domain=[('state','!=','deallocation')])
    partner_id = fields.Many2one('res.partner', 'Customer',required=True)
    reason = fields.Char("Reason", required=True)
    amount_dt=fields.Float('Amount Paid')
    appl_deduct = fields.Selection([('yes','Yes'),('no','No')], 'Apply Deduction?(Yes/No)', default= 'yes')
    administrative_charge=fields.Float(string='Administrative Charge')
    refund_amount = fields.Float(string='Refund Amount', compute='cal_refund', store=True)
    #administrative_charge= fields.Float('Administrative charge in %', default= 10.00)
    #refund_amount =fields.Float('Refund Amount', compute ='cal_refund', store = True)
    allocation_stage= fields.Char('Allocated Stage')

    @api.depends('appl_deduct')
    def cal_refund(self):
        if self.appl_deduct == 'yes':
            refund = 0.0
            refund = (self.amount_dt - ((self.amount_dt * self.administrative_charge/100)))
            self.refund_amount = refund
        elif self.appl_deduct=='no':
            self.refund_amount= self.amount_dt

    def onchange_project_site(self):
        pass
    @api.onchange('plot_no')
    def onchange_plot_id(self):
        plot= self.env['plot.allocatex'].search([('id','=',self.plot_no.id)])
        for order in self:
            if order.plot_no:
                order.partner_id = plot.partner_id.id
                order.amount_dt = plot.amount_dt

    #@api.onchange('plot_no')
    @api.model
    def create(self, vals):
        xxx= vals.get('plot_no')
        plot_allocate_obj = self.env['plot.allocatex'].search([('id','=', xxx)])
        unit_master_obj = self.env['unit.masterx'].search([('plot_no','=',self.plot_no.name.name)])
        plot_no =vals.get('plot_no')
        if plot_no:
            vals['allocation_stage']=plot_allocate_obj.state
            plot_allocate_obj.write({'state':'deallocation', 'active':False})
            plot = plot_allocate_obj.plot_no.id
            unit_master_obj.write({'status':'deallocation'})


        return super(Plot_Revocate, self).create(vals)




    @api.multi
    def unlink(self):
        unlink_ids=[]
        allocate_obj = self.env['plot.allocatex']
        plot_allocate_obj = self.env['plot.allocatex'].search([('id','=', self.plot_no.id)])
        for d in self:
            allocation_stage = d.allocation_stage
            allocate_obj.write({'state':allocation_stage})
            unlink_ids.append(d.id)
        self.unlink(unlink_ids)



class Transfer(models.Model):
    _name = 'transferx'
    name = fields.Many2one('projectsite.masterx', 'Project Site', required=True)
    plot_no = fields.Many2one('plot.allocatex', 'Plot Number', required=True, domain=[('state','=','allocation')], help="Here Allocated Plot list only")
    source_cust = fields.Many2one('res.partner', 'Primary(Customer)', required=True)
    dest_cust = fields.Many2one('res.partner', 'Secondary(Customer)', required=True)
    purpose = fields.Char('Purpose', required=True)


    @api.onchange('name')
    #onchange method for project -> returns domain that filters out the appropraite plot numbers
    def onchange_project_site(self):
        domain = {}
        if self.plot_no:

            plot_nums = self.env['plot.allocatex'].search([('name', '=', self.name), ('state', '!=', 'deallocated')])
            for all_plots in plot_nums:
                domain = {'plot_no': [('id', '=', plot_nums)]}
        return {'domain':domain}




    @api.onchange('plot_no')
    def onchange_plot_id(self):
        vals = {}
        if self.plot_no:
            plot = self.env['plot.allocatex'].search([('id', '=', self.plot_no.id)])
            vals['source_cust'] = plot.partner_id
            vals['name'] = plot.name.id
        return {'value':vals}

    @api.model
    def create(self,vals):
        xxx= vals.get('plot_no')
        dest_cust=vals.get('dest_cust')
        plot = self.env['plot.allocatex'].search([('id','=',xxx)])

        record = super(Re_Sale,self).create(vals)
        #record['amount_dt']  = plot.id
        plot.write({'partner_id':dest_cust})

        return record


class Partnership(models.Model):
    _name = "lawyer.model"
    #_inherit ="res.partner"

    lawyer = fields.Many2one('res.partner','Lawyer')
    branch_id=fields.Many2one('res.branch', 'Assigned Branch',required=True)
    @api.multi
    def name_get(self):
        if not self.ids:
            return []
        res=[]
        for field6 in self.browse(self.ids):
            #name = field6.name
            #nam = "Name-"+str(name)
            partner = "Lawyer: " +str(field6.lawyer.name)
            res.append((field6.id, " "+partner +" "))
        return res

class Partnership(models.Model):
    _name = "agent.model"
    #_inherit ="res.partner"

    agent = fields.Many2one('res.partner','Agent')
    branch_id=fields.Many2one('res.branch', 'Assigned Branch',required=True)
    @api.multi
    def name_get(self):
        if not self.ids:
            return []
        res=[]
        for field6 in self.browse(self.ids):
            #name = field6.name
            #nam = "Name-"+str(name)
            partner = str(field6.agent.name)
            res.append((field6.id, "[ "+partner +"]"))
        return res


class ProductCat(models.Model):
    _inherit = "product.category"

    project_site = fields.Many2one('projectsite.masterx', 'Project Site',required=False)
    project_name = fields.Char('Project name', store=True)

    @api.multi
    def name_get(self):
        if not self.ids:
            return []
        res=[]
        for field6 in self.browse(self.ids):
            name = field6.name
            name_get = field6.project_site.name
            nam = str(name)
            res.append((field6.id,str(field6.name)+" / " +str(name_get)))# "[ "+partner +"] -["+nam+" -["+str(field6.date_invoice)+"]"))
        return res

class ProductCus(models.Model):
    _inherit = "product.product"

    location = fields.Many2one('location.model', 'Location',required=False)
    house_number = fields.Integer('House Number',required=False)


    @api.onchange('categ_id.project_site')
    def changeCategoryName(self):
        self.categ_id = self.categ_id.name + "/" +str(categ_id.project_ste.name)

class Location(models.Model):
    _name = "location.model"

    location = fields.Char('Item Location',required=False)




class SalesOrdercus(models.Model):
    _inherit = "sale.order"
    '''def _get_branch(self):
        user_id = self.env.uid
        user_idx = self.env['res.users'].search([('id','=',user_id)])
        return user_idx.branch_id.id'''
    payment_type = fields.Selection([('installment', 'Installment'),
            ('outright', 'OutRight Payment')],
            "Payment Type")
    bank_account = fields.Many2one('account.journal','Bank Account')
    law = fields.Many2one('lawyer.model', 'Lawyer', required = False)

    #branch_id=fields.Many2one('res.branch', 'Branch', default=_get_branch, store=True )
################ CREATING FIELD FROM SALE TO INVOICE ######################
    def _prepare_invoice(self):
        ret = super(SalesOrdercus, self)._prepare_invoice()

        for rex in self:
            sale_agent = rex.sale_commission_user_ids.user_id.id
            if rex.payment_type:
                ret['payment_type'] = rex.payment_type
                ret['agent'] = sale_agent
                ret['law'] = rex.law.id
                ret['sale_commission_user_ids'] = [(6, 0, [rex.sale_commission_user_ids.id])]
                #ret['sale_commission_user_ids'] = [(6, 0, [rex.sale_commission_user_ids.id])]
                ret['sale_commission_percentage_ids'] = [(6, 0, [rex.sale_commission_percentage_ids.id])]

        return ret

    @api.onchange('order_line')
    def autofil_branch(self):
        for order in self:
            ords = order.order_line.product_id.categ_id.project_site.branch_id.id
            order.branch_id = ords

    @api.multi
    def print_indicative_allocation_letter(self):

        report = self.env["ir.actions.report.xml"].search([('report_name','=','construction_rewrite.final_provisional_letter_view_report_indicative')],limit=1)
        if report:
            report.write({'report_type':'qweb-pdf'})
        return self.env['report'].get_action(self.id, 'construction_rewrite.final_provisional_letter_view_report_indicative')


    @api.multi
    def print_final_allocation_letter(self):

        report = self.env["ir.actions.report.xml"].search([('report_name','=','construction_rewrite.final_provisional_letter_view_report')],limit=1)

        so_line = self.order_line
        get_product_cat_name = so_line.product_id.categ_id.project_site.name

        plot_name = get_product_cat_name
        '''if 'lekki1' in plot_name.lower():
            return self.env['report'].get_action(self.id,'construction_rewrite.lekki_offer_letter_view_report')
        elif 'Elegushi' in plot_name.lower():
            return self.env['report'].get_action(self.id,'construction_rewrite.lekki_offer_letter_view_report')
        elif 'lekki ii' in plot_name.lower():
            return self.env['report'].get_action(self.id,'construction_rewrite.iganmu_letter_view_report')


        elif 'iganmu' in plot_name.lower():
            return self.env['report'].get_action(self.id,'construction_rewrite.iganmu_letter_view_report')

        elif 'jubilee estate' in plot_name.lower():
            return self.env['report'].get_action(self.id,'construction_rewrite.iganmu_letter_view_report')  '''
        '''
          BRAINS & HAMMERS ESTATE, ELEGUSHI, LEKKI
          BRAINS & HAMMERS ESTATE, CASTLE AND TEMPLE, LEKKI PHASE I
          BRAINS & HAMMERS JUBILEE ESTATE, IGANMU, TOWERS
          BRAINS & HAMMERS JUBILEE ESTATE, IGANMU
          BRAINS & HAMMERS ESTATE, LEKKI II
        '''
        if plot_name=='BRAINS & HAMMERS ESTATE, CASTLE AND TEMPLE, LEKKI PHASE I':
            return self.env['report'].get_action(self.id,'construction_rewrite.lekki_offer_letter_view_report')
        elif plot_name=='BRAINS & HAMMERS ESTATE, ELEGUSHI, LEKKI':
            return self.env['report'].get_action(self.id,'construction_rewrite.lekki_offer_letter_view_report')
        elif plot_name=='BRAINS & HAMMERS JUBILEE ESTATE, IGANMU':
            return self.env['report'].get_action(self.id,'construction_rewrite.iganmu_letter_view_report')

        elif plot_name=='BRAINS & HAMMERS ESTATE, LEKKI II':
            return self.env['report'].get_action(self.id,'construction_rewrite.iganmu_letter_view_report')

        elif plot_name=='BRAINS & HAMMERS JUBILEE ESTATE, IGANMU TOWERS':
            return self.env['report'].get_action(self.id,'construction_rewrite.iganmu_letter_view_report')
        
        elif plot_name=='BRAINS & HAMMERS BUNGALOW CITY, KUBWA EXPRESS':
            return self.env['report'].get_action(self.id,'construction_rewrite.new_offer_letter_report_document')

        else:
            raise ValidationError('Please ensure that your project site name corresponds')
            #return self.env['report'].get_action(self.id,'construction_rewrite.final_provisional_letter_view_report')



class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    payment_type = fields.Selection([('installment', 'Installment'),
            ('outright', 'OutRight Payment')],
            "Payment Type")
    agent = fields.Many2one('res.partner','Agent')
    law = fields.Many2one('lawyer.model', 'Lawyer', required = False)

    @api.multi
    def name_get(self):
        if not self.ids:
            return []
        res=[]
        for field6 in self.browse(self.ids):
            name = field6.number
            nam = "Name-"+str(name)
            partner = "Customer" +field6.partner_id.name
            res.append((field6.id, "[ "+partner +"] -["+nam+" -["+str(field6.date_invoice)+"]"))
        return res

    @api.onchange('payment_term_id')
    def change_type(self):
        get_origin = self.env['sale.order'].search([('name','=',self.origin)])
        if get_origin:
            for order in get_origin:
                origin_type = order.payment_type
                self.payment_type = origin_type

    @api.multi
    def see_breakdown_invoice(self): #vis_account,
        return {
                'type':'ir.actions.act_window',
                'res_model':'account.payment',
                'res_id':self.id,
                'view_type':'form',
                'key2':'client_action_multi',
                'view_mode':'tree',
                'target':'current',
                'domain': [('partner_id','=',self.partner_id.id)]
    }
class ResPartner(models.Model):
    _inherit = "res.partner"

    #bank_acc = fields.Many2one('res.partner.bank', 'Bank Account')


class SaleAdvancePaymentInvAllocate(models.TransientModel):
    _inherit = "sale.advance.payment.inv"


    @api.multi
    def _create_invoice(self, order, so_line, amount):
        inv_obj = self.env['account.invoice']
        ir_property_obj = self.env['ir.property']

        account_id = False
        if self.product_id.id:
            account_id = self.product_id.property_account_income_id.id or self.product_id.categ_id.property_account_income_categ_id.id
        if not account_id:
            inc_acc = ir_property_obj.get('property_account_income_categ_id', 'product.category')
            account_id = order.fiscal_position_id.map_account(inc_acc).id if inc_acc else False
        if not account_id:
            raise UserError(
                _('There is no income account defined for this product: "%s". You may have to install a chart of account from Accounting app, settings menu.') %
                (self.product_id.name,))

        if self.amount <= 0.00:
            raise UserError(_('The value of the down payment amount must be positive.'))
        context = {'lang': order.partner_id.lang}
        if self.advance_payment_method == 'percentage':
            amount = order.amount_untaxed * self.amount / 100
            name = _("Down payment of %s%%") % (self.amount,)
        else:
            amount = self.amount
            name = _('Down Payment')
        del context
        taxes = self.product_id.taxes_id.filtered(lambda r: not order.company_id or r.company_id == order.company_id)
        if order.fiscal_position_id and taxes:
            tax_ids = order.fiscal_position_id.map_tax(taxes).ids
        else:
            tax_ids = taxes.ids

        invoice = inv_obj.create({
            'name': order.client_order_ref or order.name,
            'origin': order.name,
            'type': 'out_invoice',
            'reference': False,
            'account_id': order.partner_id.property_account_receivable_id.id,
            'partner_id': order.partner_invoice_id.id,
            'partner_shipping_id': order.partner_shipping_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': name,
                'origin': order.name,
                'account_id': account_id,
                'price_unit': amount,
                'quantity': 1.0,
                'discount': 0.0,
                'uom_id': self.product_id.uom_id.id,
                'product_id': self.product_id.id,
                'sale_line_ids': [(6, 0, [so_line.id])],
                'invoice_line_tax_ids': [(6, 0, tax_ids)],
                'account_analytic_id': order.project_id.id or False,
            })],
            'currency_id': order.pricelist_id.currency_id.id,
            'payment_term_id': order.payment_term_id.id,
            #'payment_type': order.payment_type,
            'fiscal_position_id': order.fiscal_position_id.id or order.partner_id.property_account_position_id.id,
            'team_id': order.team_id.id,
            'user_id': order.user_id.id,
            'comment': order.note,
        })
        invoice.compute_taxes()
        invoice.message_post_with_view('mail.message_origin_link',
                    values={'self': invoice, 'origin': order},
                    subtype_id=self.env.ref('mail.mt_note').id)
        return invoice
