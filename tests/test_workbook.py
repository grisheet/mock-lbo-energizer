import unittest
from mock_lbo.sources import ROOT
from mock_lbo.validation import audit_workbook


class WorkbookTests(unittest.TestCase):
    def test_complete_workbook(self):
        result=audit_workbook(ROOT/'excel/mock_lbo_energizer.xlsx')
        self.assertEqual(result['native_data_tables'],5)
        self.assertEqual(result['sensitivity_combinations'],95)
        self.assertLess(result['max_absolute_difference'],.001)


if __name__=='__main__':
    unittest.main()
