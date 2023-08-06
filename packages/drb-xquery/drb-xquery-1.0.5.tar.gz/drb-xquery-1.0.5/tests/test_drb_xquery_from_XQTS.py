import os
import unittest
from pathlib import Path

from drb_impl_file import DrbFileFactory
from drb_impl_xml import XmlNodeFactory

from tests.XQueryTestXQTS import XQueryTestXQTS


class TestDrbXQueryXQTS(unittest.TestCase):
    current_path = Path(os.path.dirname(os.path.realpath(__file__)))

    xml_path = current_path / "files"

    def test_xquery_xqts_func_abs(self):
        xml_file = str(self.xml_path / "XQTS_1_0_3/cat/ABSFunc.xml")
        #
        self.from_xml_xqts(xml_file)

    def test_xquery_xqts_analyse_string(self):

        xml_file = str(self.xml_path / "XQTS_1_0_3/cat/AnalyzeString.xml")
        self.from_xml_xqts(xml_file)

    def test_xquery_xqts_direct_con_elt(self):
        xml_file = str(self.xml_path / "XQTS_1_0_3/cat/DirectConElem.xml")
        self.from_xml_xqts(xml_file)

    def test_xquery_xqts_FLWOR(self):
        xml_file = str(self.xml_path / "XQTS_1_0_3/cat/FLWORExprSI.xml")
        self.from_xml_xqts(xml_file)

    def test_xquery_xqts_fn_substring(self):
        xml_file = str(
            self.xml_path / "XQTS_1_0_3/cat/functx-fn-substring.xml")
        self.from_xml_xqts(xml_file)

    def test_xquery_xqts_fn_substring_after(self):
        xml_file = str(
            self.xml_path / "XQTS_1_0_3/cat/functx-fn-substring-after.xml")
        self.from_xml_xqts(xml_file)

    def test_xquery_xqts_fn_substring_before(self):
        xml_file = str(
            self.xml_path / "XQTS_1_0_3/cat/functx-fn-substring-before.xml")
        self.from_xml_xqts(xml_file)

    def test_xquery_xqts_fn_sum(self):
        xml_file = str(
            self.xml_path / "XQTS_1_0_3/cat/functx-fn-sum.xml")
        self.from_xml_xqts(xml_file)

    def test_xquery_xqts_filter_expr(self):
        xml_file = str(self.xml_path / "XQTS_1_0_3/cat/FilterExpr.xml")
        self.from_xml_xqts(xml_file)

    def test_xquery_xqts_for_exp_wtih(self):
        xml_file = str(self.xml_path / "XQTS_1_0_3/cat/ForExprWith.xml")
        self.from_xml_xqts(xml_file)

    def test_xquery_xqts_module_import(self):
        xml_file = str(self.xml_path / "XQTS_1_0_3/cat/ModuleImport.xml")
        self.from_xml_xqts(xml_file)

    def test_xquery_xqts_module_predicates(self):
        xml_file = str(self.xml_path / "XQTS_1_0_3/cat/Predicates.xml")
        self.from_xml_xqts(xml_file)

    def test_xquery_xqts_module_range(self):
        xml_file = str(self.xml_path / "XQTS_1_0_3/cat/RangeExpr.xml")
        self.from_xml_xqts(xml_file)

    def test_xquery_xqts_module_return(self):
        xml_file = str(self.xml_path / "XQTS_1_0_3/cat/ReturnExpr.xml")
        self.from_xml_xqts(xml_file)

    def test_xquery_xqts_module_function_prolog(self):
        xml_file = str(self.xml_path / "XQTS_1_0_3/cat/FunctionProlog.xml")
        self.from_xml_xqts(xml_file)

    def test_xquery_xqts_module_function_paren(self):
        xml_file = str(self.xml_path / "XQTS_1_0_3/cat/ParenExpr.xml")
        self.from_xml_xqts(xml_file)

    def test_xquery_xqts_module_comma_op(self):
        xml_file = str(self.xml_path /
                       "XQTS_1_0_3/cat/commaOp.xml")
        self.from_xml_xqts(xml_file)

    def test_xquery_xqts_function_call_exp(self):
        xml_file = str(self.xml_path /
                       "XQTS_1_0_3/cat/FunctionCallExpr.xml")
        self.from_xml_xqts(xml_file)

    def test_xquery_xqts_function_lower_cae(self):
        xml_file = str(self.xml_path /
                       "XQTS_1_0_3/cat/functx-fn-lower-case.xml")
        self.from_xml_xqts(xml_file)

    def test_xquery_xqts_function_upper_cae(self):
        xml_file = str(self.xml_path /
                       "XQTS_1_0_3/cat/functx-fn-upper-case.xml")
        self.from_xml_xqts(xml_file)

    def test_xquery_xqts_function_reverse(self):
        xml_file = str(self.xml_path /
                       "XQTS_1_0_3/cat/functx-fn-reverse.xml")
        self.from_xml_xqts(xml_file)

    def test_xquery_xqts_fn_in_seq_count_func(self):
        xml_file = str(self.xml_path /
                       "XQTS_1_0_3/cat/SeqCountFunc.xml")
        self.from_xml_xqts(xml_file)

    def test_xquery_xqts_function_count(self):
        xml_file = str(self.xml_path /
                       "XQTS_1_0_3/cat/functx-fn-count.xml")
        self.from_xml_xqts(xml_file)

    def test_xquery_xqts_function_distinct_values(self):
        xml_file = str(self.xml_path /
                       "XQTS_1_0_3/cat/functx-fn-distinct-values.xml")
        self.from_xml_xqts(xml_file)

    def test_xquery_xqts_function_compare(self):
        xml_file = str(self.xml_path /
                       "XQTS_1_0_3/cat/functx-fn-compare.xml")
        self.from_xml_xqts(xml_file)

    def test_xquery_xqts_function_concat(self):
        xml_file = str(self.xml_path /
                       "XQTS_1_0_3/cat/functx-fn-concat.xml")
        self.from_xml_xqts(xml_file)

    def test_xquery_xqts_function_contains(self):
        xml_file = str(self.xml_path /
                       "XQTS_1_0_3/cat/functx-fn-contains.xml")
        self.from_xml_xqts(xml_file)

    def test_xquery_xqts_compare_function(self):
        xml_file = str(self.xml_path /
                       "XQTS_1_0_3/cat/CompareFunction.xml")
        self.from_xml_xqts(xml_file)

    def test_xquery_xqts_cond_exp(self):
        xml_file = str(self.xml_path /
                       "XQTS_1_0_3/cat/CondExpr.xml")
        self.from_xml_xqts(xml_file)

    def test_xquery_xqts_fn_function_boolean(self):
        xml_file = str(self.xml_path /
                       "XQTS_1_0_3/cat/functx-fn-boolean.xml")
        self.from_xml_xqts(xml_file)

    def test_xquery_xqts_fn_function_not(self):
        xml_file = str(self.xml_path /
                       "XQTS_1_0_3/cat/functx-fn-not.xml")
        self.from_xml_xqts(xml_file)

    def test_xquery_xqts_let_expr(self):
        xml_file = str(self.xml_path /
                       "XQTS_1_0_3/cat/LetExprWith.xml")
        self.from_xml_xqts(xml_file)

    def test_xquery_xqts_fn_deep_equal(self):
        xml_file = str(self.xml_path /
                       "XQTS_1_0_3/cat/functx-fn-deep-equal.xml")
        self.from_xml_xqts(xml_file)

    def test_xquery_xqts_seq_deep_equal(self):
        xml_file = str(self.xml_path /
                       "XQTS_1_0_3/cat/SeqDeepEqualFunc.xml")
        self.from_xml_xqts(xml_file)

    def test_xquery_xqts_fn_empty(self):
        xml_file = str(self.xml_path /
                       "XQTS_1_0_3/cat/functx-fn-empty.xml")
        self.from_xml_xqts(xml_file)

    def test_xquery_xqts_fn_ends_with(self):
        xml_file = str(self.xml_path /
                       "XQTS_1_0_3/cat/functx-fn-ends-with.xml")
        self.from_xml_xqts(xml_file)

    def test_xquery_xqts_fn_exists(self):
        xml_file = str(self.xml_path /
                       "XQTS_1_0_3/cat/functx-fn-exists.xml")
        self.from_xml_xqts(xml_file)

    def test_xquery_xqts_fn_floor(self):
        xml_file = str(self.xml_path /
                       "XQTS_1_0_3/cat/functx-fn-floor.xml")
        self.from_xml_xqts(xml_file)

    def test_xquery_xqts_fn_false(self):
        xml_file = str(self.xml_path /
                       "XQTS_1_0_3/cat/functx-fn-false.xml")
        self.from_xml_xqts(xml_file)

    # def test_xquery_xqts_fn_last(self):
    #     xml_file = str(self.xml_path /
    #                    "XQTS_1_0_3/cat/functx-fn-last.xml")
    #     self.from_xml_xqts(xml_file)

    def test_xquery_xqts_fn_max(self):
        xml_file = str(self.xml_path /
                       "XQTS_1_0_3/cat/functx-fn-max.xml")
        self.from_xml_xqts(xml_file)

    def test_xquery_xqts_fn_min(self):
        xml_file = str(self.xml_path /
                       "XQTS_1_0_3/cat/functx-fn-min.xml")
        self.from_xml_xqts(xml_file)

    # def test_xquery_xqts_fn_name(self):
    #     xml_file = str(self.xml_path /
    #                    "XQTS_1_0_3/cat/functx-fn-name.xml")
    #     self.from_xml_xqts(xml_file)
    # def test_xquery_xqts_fn_in_progess(self):
    #     xml_file = str(self.xml_path /
    #                     "XQTS_1_0_3/cat/in_progress.xml")
    #     self.from_xml_xqts(xml_file)

    def from_xml_xqts(self, xml_path):
        node_file = DrbFileFactory().create(xml_path)
        node = XmlNodeFactory().create(node_file)

        document = node['test-group']

        for child in document['test-case', :]:
            current_test_node = child
            test = XQueryTestXQTS(current_test_node)
            with self.subTest(test.name):
                self.assertTrue(test.run_test(self), 'error in test '
                                + test.name)
