#!/bin/bash

(test $# -lt 1) && (echo "too few arguments") && exit 0
fncat=${1:-"cat-final.txt"}

s=0
cats=""
while read cate;
do
    cats="$cats""$cate""    "
done < $fncat

for cate in $cats;
do
    c=0
    echo "================================="
    echo "characterizing category $cate ..."
    echo "================================="
    echo
    echo

    bash allSecurityReport_catapk.sh  firstrep $cate
    bash allSecurityReport_catapk.sh  secondrep $cate
    bash allSecurityReport_catapk.sh  thirdrep $cate
done

exit 0
