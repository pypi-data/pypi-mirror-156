import unittest

from click.testing import CliRunner

from drb_xquery import drb_xquery_cmd

OPTION_VAR = '-v'
QUERY_STRING_KEY = '-s'
QUERY_URL_KEY = '-f'


class TestCmd(unittest.TestCase):

    def test_command_with_help(self):
        runner = CliRunner()
        result = runner.invoke(drb_xquery_cmd.drb_xquery_cmd,
                               ['--help'])

    def test_command_with_query_string(self):
        runner = CliRunner()
        result = runner.invoke(drb_xquery_cmd.drb_xquery_cmd,
                               [QUERY_STRING_KEY,
                                'if (1 != 0) then '
                                'if (4 != 5) then 1 '
                                'else 2 else 3'])
        self.assertEqual(result.exit_code, 0)
        output = result.output.rstrip('\r')
        output = output.rstrip('\n')

        self.assertEqual(output, '1')

    def test_command_with_query_string_and_var(self):
        runner = CliRunner()

        result = runner.invoke(drb_xquery_cmd.drb_xquery_cmd, [
            QUERY_STRING_KEY,
            'declare variable $x external; '
            'declare variable $y external := 5; '
            '$x +$y', OPTION_VAR, 'x',  '9', '-v', 'y', '2'])

        self.assertEqual(result.exit_code, 0)
        output = result.output.rstrip('\r')
        output = output.rstrip('\n')

        self.assertEqual(output, '11')

    def test_command_with_query_string_and_typed_var(self):
        runner = CliRunner()

        result = runner.invoke(drb_xquery_cmd.drb_xquery_cmd, [
            QUERY_STRING_KEY,
            'declare variable $x external; '
            'declare variable $y external := 5; '
            '$x +$y',
            OPTION_VAR, 'x', '9', 'as', 'xs:integer',
            OPTION_VAR, 'y', '2', 'as', 'xs:integer'])

        self.assertEqual(result.exit_code, 0)
        output = result.output.rstrip('\r')
        output = output.rstrip('\n')

        self.assertEqual(output, '11')

    def test_command_with_query_string_and_typed_var_no_ns(self):
        runner = CliRunner()

        result = runner.invoke(drb_xquery_cmd.drb_xquery_cmd, [
            QUERY_STRING_KEY,
            'declare variable $x external; '
            'declare variable $y external := 5; '
            '$x +$y',
            OPTION_VAR, 'x', '9', 'as', 'integer',
            OPTION_VAR, 'y', '2', 'as', 'integer'])
        self.assertEqual(result.exit_code, 0)
        output = result.output.rstrip('\r')
        output = output.rstrip('\n')

        self.assertEqual(output, '11')

    def test_command_with_query_string_and_bad_type_var(self):
        runner = CliRunner()

        result = runner.invoke(drb_xquery_cmd.drb_xquery_cmd, [
            QUERY_STRING_KEY,
            'declare variable $x external; '
            'declare variable $y external := 5; '
            '$x',
            OPTION_VAR, 'x', '1', 'as', 'xs:integer',
            OPTION_VAR, 'y', 'g', 'as', 'xs:integer'])

        self.assertEqual(result.exit_code, 1)

    def test_command_with_query_string_and_malformed_type_var(self):
        runner = CliRunner()

        result = runner.invoke(drb_xquery_cmd.drb_xquery_cmd, [
            QUERY_STRING_KEY,
            'declare variable $x external; '
            'declare variable $y external := 5; '
            '$x',
            OPTION_VAR, 'x', '1', 'as', 'xs:integer',
            OPTION_VAR, 'y', '3', 'to', 'xs:integer'])

        self.assertIn('malformed', result.output.lower())
        self.assertEqual(result.exit_code, 2)

    def test_command_with_query_file_and_node(self):
        runner = CliRunner()

        # data( /Level-2A_Tile_ID/Test_FLF[@name_attr='test_two' or
        # serie='B'][position() < 5][2] / name)
        result = runner.invoke(drb_xquery_cmd.drb_xquery_cmd, [
            QUERY_URL_KEY,
            './tests/files/test.xq',
            '--url-node',
            './tests/files/MTD_TL.xml'])
        self.assertEqual(result.exit_code, 0)

        self.assertTrue('first_doublon' in result.output)

    def test_command_with_query_string_and_node(self):
        runner = CliRunner()

        # data( /Level-2A_Tile_ID/Test_FLF[@name_attr='test_two' or
        # serie='B'][position() < 5][2] / name)
        result = runner.invoke(drb_xquery_cmd.drb_xquery_cmd, [
            QUERY_STRING_KEY,
            ' ./Level-2A_Tile_ID/Test_FLF/elt',
            '--url-node',
            './tests/files/MTD_TL.xml'])
        self.assertEqual(result.exit_code, 0)

        self.assertIn('<elt>This is one</elt>', result.output)
        self.assertIn('<elt>End</elt>', result.output)

    def test_command_with_query_string_and_node_attr(self):
        runner = CliRunner()

        # data( /Level-2A_Tile_ID/Test_FLF[@name_attr='test_two' or
        # serie='B'][position() < 5][2] / name)
        result = runner.invoke(drb_xquery_cmd.drb_xquery_cmd, [
            QUERY_STRING_KEY,
            ' ./Level-2A_Tile_ID/Test_FLF/@name_attr',
            '--url-node',
            './tests/files/MTD_TL.xml'])
        self.assertEqual(result.exit_code, 0)

        self.assertIn('@name_attr=test_three', result.output)

    def test_command_with_query_string_and_url_query(self):
        runner = CliRunner()

        result = runner.invoke(drb_xquery_cmd.drb_xquery_cmd, [
            QUERY_STRING_KEY,
            'test',
            QUERY_URL_KEY,
            './tests/files/test.xq'])

        self.assertIn('exclusive', result.output.lower())
        self.assertEqual(result.exit_code, 2)

    def test_command_verbose(self):
        runner = CliRunner()

        # data( /Level-2A_Tile_ID/Test_FLF[@name_attr='test_two' or
        # serie='B'][position() < 5][2] / name)
        result = runner.invoke(drb_xquery_cmd.drb_xquery_cmd, [
            '--verbose',
            QUERY_URL_KEY,
            './tests/files/test.xq',
            OPTION_VAR,
            'myvar',
            'valeu_var',
            '--url-node',
            './tests/files/MTD_TL.xml'])

        self.assertIn('Level-2A_Tile_ID/Test_FLF', result.output)
        self.assertIn('myvar', result.output)

        self.assertEqual(result.exit_code, 0)

    def test_command_no_verbose(self):
        runner = CliRunner()

        # data( /Level-2A_Tile_ID/Test_FLF[@name_attr='test_two' or
        # serie='B'][position() < 5][2] / name)
        result = runner.invoke(drb_xquery_cmd.drb_xquery_cmd, [
            QUERY_URL_KEY,
            './tests/files/test.xq',
            OPTION_VAR,
            'myvar',
            'valeu_var',
            '--url-node',
            './tests/files/MTD_TL.xml'])

        self.assertNotIn('Level-2A_Tile_ID/Test_FLF', result.output)
        self.assertNotIn('myvar', result.output)

        self.assertEqual(result.exit_code, 0)

    def test_command_without_query_string_and_url_query(self):
        runner = CliRunner()

        result = runner.invoke(drb_xquery_cmd.drb_xquery_cmd, [])

        self.assertIn('at least', result.output.lower())
        self.assertEqual(result.exit_code, 2)
