declare variable $a := <a/>;
declare function local:testDoubleNodeIdentity($a as node(), $b as node())
{
    $a is $b
};
local:testDoubleNodeIdentity( <a/>, <a/>), local:testDoubleNodeIdentity($a, $a)