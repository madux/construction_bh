import time
from odoo import models, fields, api, _
from odoo.exceptions import except_orm, ValidationError
from odoo.tools import misc, DEFAULT_SERVER_DATETIME_FORMAT
from dateutil.relativedelta import relativedelta
import datetime

#class of plot screen report
class plot_report(models.Model):
    _name = 'plot.reportx'
    name = fields.Many2one('projectsite.masterx','Project Site',required=True)

    # function for printing screen report click on print report
    def print_report(self):
        #self._cr.execute("delete from plot_data_report")
        #self._cr.execute("""delete from plot_data_report_master""")
        wizard = self
        plot_obj = self.env['plot.allocatex']
        #print "********",plot_obj.name
        building=self.name.id

        result = {}
        plot_ids = plot_obj.search([('name','=',building)])
        master_report=self.env['plot.data.report.master'].create({'name':"Report"})
        for plot in plot_obj.browse(plot_ids):
            result = {
                      'plot_master_id':master_report,
                      'name':plot.partner_id.name,
                      'house_no':plot.plot_no,
                      'offer_date':plot.offer_dt,
                      'offer_price':plot.offer_price,
                      'sold':False,
                      }
            if plot.so_no:
                result.update({'sold':True})
            self.env['plot.data.report'].create(result)
        return {
               'type':'ir.actions.act_window',
               'res_model':'plot.data.report.master',
               'view_type':'form',
               'view_mode':'form',
               'res_id': master_report,
               }
