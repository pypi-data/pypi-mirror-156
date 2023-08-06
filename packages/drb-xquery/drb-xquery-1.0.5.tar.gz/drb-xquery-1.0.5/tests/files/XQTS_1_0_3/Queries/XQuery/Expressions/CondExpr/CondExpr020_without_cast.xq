(: FileName: CondExpr020 :)
(: Purpose: Test case where then-expression raises a dynamic error, but test-expression selects else-expression so no error is raised :)

(: insert-start :)
declare variable $input-context external;
(: insert-end :)

if( false() )
then $input-context/Folder[1]
else 10
