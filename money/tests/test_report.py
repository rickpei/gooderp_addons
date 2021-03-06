# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError

class test_report(TransactionCase):
    def test_bank_report(self):
        ''' 测试银行对账单报表 '''
        # 生成收款单记录
        self.env.ref('money.get_40000').money_order_done()
        # 生成其他收支单记录
        last_balance = self.env.ref('core.comm').balance
        self.env.ref('money.other_get_60').other_money_done()
        # tax_rate = self.env.ref('base.main_company').import_tax_rates
        self.assertAlmostEqual(self.env.ref('core.comm').balance, last_balance + 60.0)
        # 生成转账单记录
        self.env.ref('money.transfer_300').money_transfer_done()
        # 执行向导
        statement = self.env['bank.statements.report.wizard'].create({'bank_id': self.env.ref('core.comm').id,
                                                                      'from_date': '2016-11-01', 'to_date': '2016-11-03'})
        # 输出报表
        statement.confirm_bank_statements()
        # 测试现金银行对账单向导：'结束日期不能小于开始日期！'
        statement_date_error = self.env['bank.statements.report.wizard'].create({'bank_id':self.env.ref('core.comm').id,
                                                                                'from_date': '2016-11-03', 'to_date': '2016-11-02'})
        with self.assertRaises(UserError):
            statement_date_error.confirm_bank_statements()
        # 测试现金银行对账单向导：from_date的默认值是否是公司启用日期
        statement_date = self.env['bank.statements.report.wizard'].create({'bank_id': self.env.ref('core.comm').id,
                                                                           'to_date': '2016-11-03'})
        self.assertEqual(statement_date.from_date, self.env.user.company_id.start_date)
        # 查看对账单明细; 同时执行_compute_balance
        statement_money = self.env['bank.statements.report'].search([])
        for money in statement_money:
            self.assertNotEqual(str(money.balance), 'zxy')
            money.find_source_order()

    def test_other_money_report(self):
        ''' 测试其他收支单明细表'''
        # 执行向导
        statement = self.env['other.money.statements.report.wizard'].create({'from_date': '2016-11-01',
                                                                             'to_date': '2016-11-03'})
        # 输出报表
        statement.confirm_other_money_statements()
        # 测试其他收支单明细表向导：'结束日期不能小于开始日期！'
        statement_error_date = self.env['other.money.statements.report.wizard'].create({'from_date': '2016-11-03',
                                                                                        'to_date': '2016-11-01'})
        with self.assertRaises(UserError):
            statement_error_date.confirm_other_money_statements()
        # 测试其他收支单明细表向导：from_date的默认值
        statement_date = self.env['other.money.statements.report.wizard'].create({'to_date': '2016-11-03'})
        # 判断from_date的值是否是公司启用日期
        self.assertEqual(statement_date.from_date, self.env.user.company_id.start_date)

    def test_partner_statements_report(self):
        ''' 测试业务伙伴对账单报表'''
        # onchange_from_date 业务伙伴先改为供应商，再改为客户
        self.partner_id = self.env.ref('core.lenovo').id
        self.env['partner.statements.report.wizard'].onchange_from_date()
        self.assertEqual(self.partner_id, self.env.ref('core.lenovo').id)
        self.partner_id = self.env.ref('core.jd').id
        self.env['partner.statements.report.wizard'].with_context({'default_customer': True}).onchange_from_date()
        self.assertEqual(self.partner_id, self.env.ref('core.jd').id)
