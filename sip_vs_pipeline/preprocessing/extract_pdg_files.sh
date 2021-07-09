function waitforjobs {
        while test $(jobs -p | wc -w) -ge "$1"; do wait -n; done
}
function checkoutput {
        if [ $? -ne 0 ]; then
                echo $1
                exit 1
        fi
}
for ds in 'simple-cov' 'mibench-cov'; do
        waitforjobs $(nproc)
        echo SPAWNING $(nproc) processes to generate CSV files from labled BC samples
        bash ../program-dependence-graph/collect-seg-dataset-features.sh LABELED-BCs/$ds skip > /dev/null &
done
waitforjobs 1
checkoutput 'Failed to generate CSV files'
