from drb import DrbNode
from drb_impl_xml import XmlNode
from xml.etree import ElementTree
import re
from drb_xquery.drb_xquery_context import StaticContext, DynamicContext
from drb_xquery.drb_xquery_item import DrbXqueryItem
from drb_xquery.drb_xquery_utils import DrbQueryFuncUtil


class XQueryResToString:

    @staticmethod
    def manage_prefix_namespace(namespace_uri,
                                context: StaticContext,
                                dynamic_context: DynamicContext,
                                namespace_declared):
        if namespace_uri is None:
            return '', ''
        prefix_ret = ''
        prefix = None

        if dynamic_context is not None:
            prefix = dynamic_context.get_namespace_prefix_name(namespace_uri)
        if prefix is None or len(prefix) == 0:
            prefix = context.get_namespace_prefix_name(namespace_uri)
        if prefix is None or len(prefix) == 0:
            namespace_def = ' xmlns' + '="' \
                            + namespace_uri + '"'
        else:
            namespace_def = ' xmlns:' + prefix + '="' \
                            + namespace_uri + '"'
            prefix_ret = prefix + ':'

        if namespace_uri not in namespace_declared:
            namespace_declared.append(namespace_uri)
            return prefix_ret, namespace_def
        return prefix_ret, ''

    @staticmethod
    def drb_name_value_to_str(item):
        result = '@' + item.name
        if item.value is None:
            return result
        result = result + '=' + str(item.value)

        return result

    @staticmethod
    def drb_item_to_xml(item,
                        context: StaticContext,
                        namespace_declared: list,
                        dynamic_context: DynamicContext):
        if not isinstance(item, (DrbXqueryItem, DrbNode)):
            return item.name

        namespace_definition = ''
        result = '<'

        if dynamic_context is not None:
            for (ns_full,
                 ns_prefix) in dynamic_context.name_space_map\
                    .namespace_prefix_map.items():
                if ns_full not in namespace_declared:
                    namespace_definition = namespace_definition + \
                                           ' xmlns:' + ns_prefix + '="' + \
                                           ns_full + '"'
                    namespace_declared.append(ns_full)

        prefix, namespace_def = XQueryResToString.manage_prefix_namespace(
            item.namespace_uri,
            context,
            dynamic_context,
            namespace_declared)

        namespace_definition = namespace_definition + namespace_def

        result = result + prefix + item.name
        for key in item.attributes.keys():
            if isinstance(key, tuple):
                if len(key) == 2 and key[1] is not None:
                    prefix_attr, namespace_def = \
                        XQueryResToString.manage_prefix_namespace(
                            key[1],
                            context,
                            dynamic_context,
                            namespace_declared)
                    name_key = prefix_attr + key[0]
                    namespace_definition = namespace_definition + namespace_def
                else:
                    name_key = key[0]
            else:
                name_key = key
            value_attr = item.attributes[key]
            if not isinstance(value_attr, str) or \
                    not value_attr.startswith('"'):
                value_attr = '"' + str(value_attr) + '"'

            result = result + ' ' + name_key + '=' + value_attr

        result = result + namespace_definition
        if item.value is None and len(item.children) == 0:
            return result + '/>'
        result = result + '>'

        for child in item.children:
            result = XQueryResToString.add_item_to_result(
                result, child, '',
                context=context,
                namespace_declared=namespace_declared,
                dynamic_context=dynamic_context)
        if item.value is not None:
            if isinstance(item.value, (DrbNode, DynamicContext)):
                result = XQueryResToString.add_item_to_result(
                    result,
                    item.value,
                    separator='',
                    context=context,
                    dynamic_context=dynamic_context,
                    namespace_declared=namespace_declared)
            else:
                result = result + str(item.value)
        result = result + '</'
        result = result + prefix + item.name + '>'

        return result

    @staticmethod
    def add_item_to_result(result_string: str, item, separator=',',
                           context: StaticContext = None,
                           dynamic_context: DynamicContext = None,
                           namespace_declared: list = None,
                           float_format_g=True):
        if namespace_declared is None:
            namespace_declared = []

        if result_string is None:
            result_string = ''
        else:
            result_string = result_string + separator

        if isinstance(item, DynamicContext):
            if isinstance(item.node, XmlNode):
                xml_bytes = ElementTree.tostring(item.node._elem)
                result_string = result_string + xml_bytes.decode()
                if result_string.find('ns0=') >= 0:
                    result_string = result_string.replace('xmlns:ns0=',
                                                          'xmlns=')
                    result_string = result_string.replace('ns0:', '')
                    result_string = re.sub('>\\s+<', '><', result_string)

            elif isinstance(item.node, (DrbXqueryItem, DrbNode)):
                result_string = result_string + \
                                XQueryResToString.drb_item_to_xml(
                                    item.node,
                                    context=context,
                                    namespace_declared=namespace_declared,
                                    dynamic_context=item)
            else:
                result_string += XQueryResToString.drb_name_value_to_str(item)

        elif isinstance(item, (DrbXqueryItem, DrbNode)):
            result_string = result_string + XQueryResToString.drb_item_to_xml(
                item, context=context,
                namespace_declared=namespace_declared,
                dynamic_context=dynamic_context)
        elif isinstance(item, float):
            if float_format_g is True:
                result_float = '{:g}'.format(item)
                result_float = result_float.replace('+', '')
                if 'inf' not in result_float and \
                        'e' not in result_float and \
                        '.' not in result_float:
                    result_float = result_float + ".0"
            else:
                result_float = str(item).replace('e+', 'e')
                if result_float.endswith(".0"):
                    result_float = result_float[:-2]
            result_string = result_string + result_float
        else:
            result_string = result_string + DrbQueryFuncUtil.get_string(item)
        return result_string
