import html
import re
import unittest

from drb import DrbNode

from drb_xquery import DrbXQuery
from drb_xquery.drb_xquery_res_to_string import XQueryResToString


class XQueryTest:

    def __init__(self, node: DrbNode):
        self.node = node

        self.name = node.get_attribute("name")
        self.query = self.node['query']
        try:
            self.expected_result = self.node['result']
        except Exception as Error:
            self.expected_result = None

        self.dynamicError = False
        try:
            attr_value = self.query.get_attribute("dynamicError")
            if attr_value is not None and str(attr_value).lower() == "true":
                self.dynamicError = True
        except Exception as Error:
            pass
        self.staticError = False
        try:
            attr_value = self.query.get_attribute("staticError")
            if attr_value is not None and str(attr_value).lower() == "true":
                self.staticError = True
        except Exception as Error:
            pass

    @staticmethod
    def remove_blank(str_result):
        # Remove blank for simplify the compare operation
        str_result = str(str_result).lower()
        str_result = str_result.replace('\n', '')
        str_result = str_result.strip()
        str_result = re.sub('\\s+', ' ', str_result)
        str_result = str_result.replace(', ', ',')
        str_result = str_result.replace('> ', '>')
        str_result = str_result.replace(' />', '/>')

        return str_result

    @staticmethod
    def compare_result_and_expected(expected_str,
                                    result_string):
        expected_str = XQueryTest.remove_blank(expected_str)
        result_string = XQueryTest.remove_blank(result_string)

        if expected_str == result_string:
            return True

        # import difflib
        # out = list(difflib.Differ().compare(expected_str, result_string))
        # if out:
        #     for line in out:
        #         print(line)
        return False

    def run_test(self, testClass: unittest.TestCase):
        try:
            query_string = self.query.value
            query_string = html.unescape(query_string)

            query = DrbXQuery(query_string)
            result = query.execute(None)
        except Exception as error_query:
            if self.dynamicError or self.staticError:
                return True
            else:
                raise Exception(error_query,
                                'Error raise  in ' + str(self.name))
        if result is None:
            if self.expected_result is None:
                return True
            else:
                return False

        if self.dynamicError or self.staticError:
            print("Test OK but error is waited")
            return False

        if not isinstance(result, list):
            result = [result]

        result_string = None
        for item in result:
            result_string = XQueryResToString.add_item_to_result(
                result_string, item,
                context=query.static_context)

        if result_string is None:
            result_string = ''

        if self.expected_result is None or self.expected_result.value is None:
            expected_result = ''
        else:
            expected_result = self.expected_result.value

        if XQueryTest.compare_result_and_expected(expected_result,
                                                  result_string):
            return True

        testClass.assertTrue(False, self.name
                             + ' result are not as expected\n'
                             + result_string + '\n != \n' +
                             expected_result + '\n')
