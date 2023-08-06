# Xquery for DRB
This xquery module allows execute xquery on DRB nodes.

## Using this module
To include this module into your project, the `drb-xquery` module shall be referenced into `requirement.txt` file, or the following pip line can be run:

```commandline
pip install drb-xquery
```

Example for execute a query on xml node:

```python
node_file = DrbFileFactory().create("/path_xml_file/namefile.xml")
node = XmlNodeFactory().create(node_file)

# request node named 2A_Tile_ID with ns as namespace
query = DrbXQuery("/ns:Level-2A_Tile_ID")
result = query.execute(node)

```

Result is always a list of value or dynamic context

Example with external variables:

```python
# create the query from  String   
query = DrbXQuery("declare variable $x external; "
                 "declare variable $y external := 5; $x+$y")

list_var = {'x': 9, 'y': 12}

result = query.execute(node, list_var)

# result[0] == 21
```


## Command line

A command line is available for use this module.

The name of the command line is ```xquery```

```commandline
xquery --help

Usage: drb-xquery-cmd [OPTIONS]

  This command evaluates the XQuery script provided as a string or a file. The
  output of the evaluation is printed out in the standard output. The output
  format may have several forms according to the resulting sequence. Basically
  the resulting nodes are output as XML fragments, the attributes not attached
  to nodes are written as in XML but prefixed with '@' symbol and finally, the
  atomic values are printed without decoration, according to the XML Schema
  lexical space definitions. All items of the output sequence are comma
  separated. A '()' result denotes the empty sequence.

Options:
  -s, --string TEXT    Command line string to be evaluated as XQuery script.
                       This parameter cannot be used jointly with -f. At least
                       -s or -f is to be set.
  -f, --file TEXT      Path to a file containing the sctript to be evaluated.
                       This parameter cannot be used jointly with -s. At least
                       -f or -s is to be set..
  -n, --url-node TEXT  Url to a node, in drb meaning, that give the context of
                       the query. It can be the pathof a xml file for example on
                       which the xquery willbe executed
  -V, --verbose
  -v, --variable TEXT  Variable define -v <QName> <value> [ as <type>].Pushes an
                       external variable in the environment prior to parse and
                       evaluate the XQuery script. The variable is pushed in the
                       the environment altough it has not been declared has an
                       external variable, to provide it to the potential nested
                       XQuerys (e.g. a call to evaluate-uri() built-in
                       function). <QName> is the qualified name of the variable
                       to declare whether <value> is a string to bind as value
                       of the variable. If <QName> matches a typed external
                       variable declared in the script, <value> is converted to
                       that type before being bound. The trailing "as <type>" is
                       optional and shall follow the XQuery sequence type
                       declaration (e.g. as xs:integer+ )
  --help               Show this message and exit.

```

Example with string query

```commandline
xquery  -s "declare variable \$x external; declare variable \$y external := 5; \$x +\$y" -v x  9 -v y 2
11
```

```commandline
xquery  -s "/Level-2A_Tile_ID/Test_FLF[@name_attr='test_two' or serie='B'][position() < 5][2]" --url-node "./tests/files/MTD_TL.xml"

<Test_FLF xmlns="nc3" xmlns:ns1="SB" name_attr="test_one" index="03" occurence="4" atr="quattre"><name>first_doublon</name><ns1:french>premier</ns1:french><number>one</number><serie>B</serie><elt>This is 4</elt></Test_FLF> 
```

Example with file query and url node

```commandline
xquery  -f "./tests/files/test.xq" --url-node "./tests/files/MTD_TL.xml"
first_doublon
```



# Limitations and differences with W3C standard

The data() function return only the value of elt

for example :


```
 data(element root {element foo {"child"}, " parent" })
```

return in W3C standard:

```
child parent
```

return in this implementation: 

```
parent
```

The infinity value is allowed for Decimal as for float: In W3C infinity is 
only allowed for float or double.

The type xs:double is identical to xs:float
The type xs:long, xs:short, xs:byte are identical to xs:integer


Other limitations

Some types are not defined like:
    xs:anyURI
    xs:untypedAtomic
    ...

Some functions are not yet implemented like:
    yearMonthDuration
    deep-equal
    remove
    processing-instruction
    exactly-one
    ...

Some expressions are not (yet) implemented like:
    group by 
    order by 
    typeswitch
    treat as
    map and array are not defined too    

# Warning for user using drb java implementation of Xquery

When using positional predicates, you should be aware that the to keyword does not work as you might expect when used in predicates. If you want the first three products, it may be tempting to use the syntax:

```
doc("catalog.xml")/catalog/product[1 to 3]
```
However, this will raise an error[*] because the predicate evaluates to multiple numbers instead of a single one. You can, however, use the syntax:

```
doc("catalog.xml")/catalog/product[position() = (1 to 3)]
```

For compare function the result is only -1,0, 1 , in java thi function return a negative value that can be different to -1
or a positive value that represent a difference between the two string...







