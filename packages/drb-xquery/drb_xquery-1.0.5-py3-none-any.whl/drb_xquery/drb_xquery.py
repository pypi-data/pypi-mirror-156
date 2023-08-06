import io

import sys

from antlr4 import InputStream, CommonTokenStream

from drb import DrbNode

from .XQueryLexer import XQueryLexer
from .XQueryParser import XQueryParser
from .drb_xquery_context import DynamicContext
from .drb_xquery_visitor import DrbQueryVisitor, \
    DrbXqueryParserErrorListener


class DrbXQuery:

    def __init__(self, xquery):
        self.static_context = None

        if isinstance(xquery, DrbNode):
            xquery = xquery.get_impl(io.BufferedIOBase)

        if isinstance(xquery, io.BufferedIOBase):
            xquery = xquery.read().decode()

        # init Lexer with query
        lexer = XQueryLexer(InputStream(xquery))

        self.stream = CommonTokenStream(lexer)
        self.parser = XQueryParser(self.stream)

        self.parser.addErrorListener(DrbXqueryParserErrorListener())
        # parse query and reject it if error
        self.tree = self.parser.module()

    def execute(self, node: DrbNode, external_var: dict = None):

        old_limit = sys.getrecursionlimit()
        sys.setrecursionlimit(10000)

        # Execute the query on the node
        visitor = DrbQueryVisitor(DynamicContext(node), tokens=self.stream)
        visitor.external_var_map = external_var
        self.static_context = visitor.static_context

        output = visitor.visitModule(self.tree)
        if not isinstance(output, list):
            output = [output]

        sys.setrecursionlimit(old_limit)

        return output
