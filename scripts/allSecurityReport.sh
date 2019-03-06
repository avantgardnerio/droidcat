#!/bin/bash

(test $# -lt 3) && (echo "too few arguments") && exit 0

APKDIR=$1
TRACEDIR=$2
RESULTDIR=$3

mkdir -p $RESULTDIR/securityReport
resultlog=$RESULTDIR/securityReport/log.securityReport.all
> $resultlog
for orgapk in $APKDIR/*.apk
do
    packname=${orgapk##*/}
	if [ ! -s $TRACEDIR/$packname.logcat ];
	then
        echo $orgapk did not have trace.
		continue
	fi
    if [ `grep -a -c $packname $RESULTDIR/securityReport/securityfeatures.txt` -ge 1 ];then
        echo "$orgapk has been processed."
        continue;
    fi
	#rt=`cat lowcov_malware | awk '{print $1}' | grep -a -c "^${i}.apk.logcat$"`
	#if [ $rt -lt 1 ];then
		echo "result for $orgapk" >> $resultlog 2>&1
		/home/hcai/bin/getpackage.sh $orgapk >> $resultlog 2>&1
		sh /home/hcai/testbed/securityReport.sh \
			$orgapk \
			$TRACEDIR/$packname.logcat \
            $RESULTDIR/securityReport >> $resultlog 2>&1
	#fi
done

exit 0




