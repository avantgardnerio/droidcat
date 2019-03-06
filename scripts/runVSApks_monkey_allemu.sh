#!/bin/bash

tmv=${1:-"60"}
port=${2:-"5554"}
avd=${3:-"Nexus-One-10"}
year=${4:-"2010"}
did="emulator-$port"

timeout() {

    time=$1

    # start the command in a subshell to avoid problem with pipes
    # (spawn accepts one command)
    command="/bin/sh -c \"$2\""

    expect -c "set echo \"-noecho\"; set timeout $time; spawn -noecho $command; expect timeout { exit 1 } eof { exit 0 }"    

    if [ $? = 1 ] ; then
        echo "Timeout after ${time} seconds"
    fi

}
processOneApk()
{
    fnapk=$1

    #ret=`timeout 120 "/home/hcai/bin/apkinstall $fnapk $did"`
    echo "now installing $fnapk"
    ret=`/home/hcai/bin/apkinstall $fnapk $did`
    n1=`echo $ret | grep -a -c "Success"`
    if [ $n1 -lt 1 ];then 
        echo "killing pid $pidemu, the process of emulator at port $port, from runAndroZooApks_monkey.sh... because app cannot be installed successfully"
        echo $ret
        return 1
    fi

    # try running it and seeing if it immediately crashes (in one minute)

    adb -s $did logcat -v raw -s "hcai-intent-monitor" "hcai-cg-monitor" &>$OUTDIR/${fnapk##*/}.logcat &
    pidadb=$!
    tgtp=`~/bin/getpackage.sh $fnapk | awk '{print $2}'`
    timeout $tmv "adb -s $did shell monkey -p $tgtp --ignore-crashes --ignore-timeouts --ignore-security-exceptions --throttle 200 10000000 >$OUTDIR/${fnapk##*/}.monkey"

    #timeout 30 "/home/hcai/bin/apkuninstall $fnapk $did"
    /home/hcai/bin/apkuninstall $fnapk $did
    kill -9 $pidadb
    return 0
}
tryInstall()
{
    cate=$1

    srcdir=/home/hcai/testbed/cg.instrumented/VirusShare/$cate
    finaldir=$srcdir

    OUTDIR=/home/hcai/testbed/otheremulators/VSLogs-$avd/$cate
    mkdir -p $OUTDIR

	k=1

    echo "tracing $fnapk ..."
    /home/hcai/testbed/setupEmu.sh ${avd} $port
    sleep 3
    pidemu=`ps axf | grep -v grep | grep -a -E "$avd -scale .3 -no-window -port $port" | awk '{print $1}'`

    flag=false
    for fnapk in $finaldir/*.apk;
	do

        #if [ `grep -a -c ${fnapk##*/} otheremulators/list.malware-vs-$year.txt` -lt 1 ];then
        #if [ `grep -a -c ${fnapk##*/} otheremulators/apkname_run_fail_malware-$year.txt` -lt 1 ];then
        if [ `grep -a -c ${fnapk##*/} otheremulators/installedapks/emulator-25/malware-vs-${year}` -lt 1 ];then
            echo "$fnapk was not included in previous run-time study"
            continue
        fi

        echo "================ RUN INDIVIDUAL APP: ${fnapk##*/} ==========================="
        if [ -s $OUTDIR/${fnapk##*/}.logcat ];
        then
            echo "$fnapk has been processed already, skipped."
            continue
        fi

        timeout 180 "traceOneApk.sh $tmv $fnapk $did $OUTDIR"
        if [ $? -ne 0 ];then
            continue
        fi
		k=`expr $k + 1`
        continue

        :'
		#ret=`timeout 120 "/home/hcai/bin/apkinstall $fnapk $did"`
        echo "now installing $fnapk"
		ret=`/home/hcai/bin/apkinstall $fnapk $did`
		n1=`echo $ret | grep -a -c "Success"`
		if [ $n1 -lt 1 ];then 
            echo "killing pid $pidemu, the process of emulator at port $port... because app cannot be installed successfully"
            echo $ret
            #kill -9 $pidemu
            continue
        fi

		# try running it and seeing if it immediately crashes (in one minute)

        adb -s $did logcat -v raw -s "hcai-intent-monitor" "hcai-cg-monitor" &>$OUTDIR/${fnapk##*/}.logcat &
        pidadb=$!
        tgtp=`~/bin/getpackage.sh $fnapk | awk '{print $2}'`
        timeout $tmv "adb -s $did shell monkey -p $tgtp --ignore-crashes --ignore-timeouts --ignore-security-exceptions --throttle 200 10000000 >$OUTDIR/${fnapk##*/}.monkey"

        #timeout 30 "/home/hcai/bin/apkuninstall $fnapk $did"
        /home/hcai/bin/apkuninstall $fnapk $did
        kill -9 $pidadb
        '

		#k=`expr $k + 1`
	done

    echo "killing pid $pidemu, the process of emulator at port $port..."
    kill -9 $pidemu
    rm -rf /tmp/android-hcai/*

	echo "totally $k apps in category $cate successfully traced."
}


s=0

#for cate in 2016 2015 2014
#for cate in 2013 2011 2010
for cate in "$year"
do
    c=0
    echo "================================="
    echo "try installing category $cate ..."
    echo "================================="
    echo
    echo

    tryInstall $cate
    rm -rf /tmp/android-hcai/*
done

exit 0
