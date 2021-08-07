# File taken from https://github.com/mr-ma/composition-sip-eval/blob/smwyg/generate-ml-files.sh

FLA='FLAs'
SUB='SUB'
BCF='BCF'

PERC=30
DATASET='mibench-cov'
GENERATIONPATH='LABELED-BCs/'
function edit {
	echo switched to $1
	sed -i "s/const int defaultObfRate = 30/const int defaultObfRate = $1/g" /home/sip/offtree-o-llvm/passes/obfs/BogusControlFlow.cpp
	sed -i "s/const int defaultObfRate = 40/const int defaultObfRate = $1/g" /home/sip/offtree-o-llvm/passes/obfs/BogusControlFlow.cpp
	sed -i "s/const int defaultObfRate = 100/const int defaultObfRate = $1/g" /home/sip/offtree-o-llvm/passes/obfs/BogusControlFlow.cpp
	#edit bogus control flow $1
	#build obfuscation passes
	make -C /home/sip/offtree-o-llvm/passes/build > /dev/null
	PERC=$1
}
function waitforjobs {
    while test $(jobs -p | wc -w) -ge "$1"; do wait -n; done
}
function generate {

	for ds in $DATASET;
		#for ds in 'simple-cov';
	do
		for prot in 'OH' 'CFI' 'SC' ;
			#
		do
			#N=16
			#(
			for combination in "$@";
			do
				#generator-prot-obf.sh OH FLAs-SUB-BCF coverage mibench-OH-FLAs-SUB-BCF
			#	((i=i%N)); ((i++==0)) && wait
				comb_dir="${combination/FLAs/FLA}"
				comb_dir="${comb_dir/BCF/BCF$PERC}"
				waitforjobs $(nproc)
				echo generator-prot-obf.sh $prot $combination $ds "$GENERATIONPATH/$ds/$comb_dir"
				bash generator-prot-obf.sh $prot $combination $ds "$GENERATIONPATH/$ds/$comb_dir" > /dev/null &
			done
			waitforjobs 1
		done
	done

}

function verifyCountFiles {
	VerifyPath=$1
	BCInFolder=$2
	for folder in ${VerifyPath};
	do
		count=$(ls -1 $folder/*.bc|wc -l)
		if [ $count != $2 ]; then
			echo "COUNTERR"
			echo "$folder/*.bc does not have $2 items but $count items"
			#exit 1
		fi

	done
}

function generateMibench {
	DATASET='mibench-cov'
	generate "NONE"
	edit 30
	generate "$BCF" "$FLA-$BCF" "$BCF-$FLA" "$SUB-$BCF" "$BCF-$SUB" "$FLA-$BCF-$SUB" "$FLA-$SUB-$BCF" "$BCF-$FLA-$SUB" "$BCF-$SUB-$FLA" "$SUB-$FLA-$BCF" "$SUB-$BCF-$FLA" "$SUB" "$FLA" "$SUB-$FLA" "$FLA-$SUB" "$BCF-$FLA"2 "$BCF-$FLA"2"-$SUB"2 "$BCF-$SUB"2"-$FLA"2

	verifyCountFiles "$GENERATIONPATH/$DATASET/*" "76"


	#edit bogus contrl flow to 40
	edit 40
	generate "$BCF" "$BCF-$FLA" "$BCF-$FLA-$SUB" "$BCF-$SUB" "$BCF-$SUB-$FLA" "$FLA-$BCF" "$FLA-$BCF-$SUB" "$FLA-$SUB-$BCF" "$SUB-$BCF" "$SUB-$BCF-$FLA" "$SUB-$FLA-$BCF"
	verifyCountFiles "$GENERATIONPATH/$DATASET/*" "76"
	edit 100
	generate "$BCF" "$BCF-$FLA" "$BCF-$FLA-$SUB" "$BCF-$SUB" "$BCF-$SUB-$FLA" "$FLA-$BCF" "$FLA-$BCF-$SUB" "$FLA-$SUB-$BCF" "$SUB-$BCF" "$SUB-$BCF-$FLA" "$SUB-$FLA-$BCF"
	verifyCountFiles "$GENERATIONPATH/$DATASET/*" "76"

}
function generateSimple {
	DATASET='simple-cov'
	edit 30
	generate "NONE"
	generate "$BCF" "$FLA-$BCF" "$BCF-$FLA" "$SUB-$BCF" "$BCF-$SUB" "$FLA-$BCF-$SUB" "$FLA-$SUB-$BCF" "$BCF-$FLA-$SUB" "$BCF-$SUB-$FLA" "$SUB-$FLA-$BCF" "$SUB-$BCF-$FLA" "$SUB" "$FLA" "$SUB-$FLA" "$FLA-$SUB"
	verifyCountFiles "$GENERATIONPATH/$DATASET/*" "160"
}

function generateSimple2 {
	DATASET='simple-cov2'

	generate "NONE"
	edit 30
	generate "$BCF" "$FLA-$BCF" "$BCF-$FLA" "$SUB-$BCF" "$BCF-$SUB" "$FLA-$BCF-$SUB" "$FLA-$SUB-$BCF" "$BCF-$FLA-$SUB" "$BCF-$SUB-$FLA" "$SUB-$FLA-$BCF" "$SUB-$BCF-$FLA" "$SUB" "$FLA" "$SUB-$FLA" "$FLA-$SUB" "$BCF-$FLA"2 "$BCF-$FLA"2"-$SUB"2 "$BCF-$SUB"2"-$FLA"2

	verifyCountFiles "$GENERATIONPATH/$DATASET/*" "76"

	#edit bogus contrl flow to 40
	edit 40
	generate "$BCF" "$BCF-$FLA" "$BCF-$FLA-$SUB" "$BCF-$SUB" "$BCF-$SUB-$FLA" "$FLA-$BCF" "$FLA-$BCF-$SUB" "$FLA-$SUB-$BCF" "$SUB-$BCF" "$SUB-$BCF-$FLA" "$SUB-$FLA-$BCF"
	verifyCountFiles "$GENERATIONPATH/$DATASET/*" "76"
	edit 100
	generate "$BCF" "$BCF-$FLA" "$BCF-$FLA-$SUB" "$BCF-$SUB" "$BCF-$SUB-$FLA" "$FLA-$BCF" "$FLA-$BCF-$SUB" "$FLA-$SUB-$BCF" "$SUB-$BCF" "$SUB-$BCF-$FLA" "$SUB-$FLA-$BCF"
	verifyCountFiles "$GENERATIONPATH/$DATASET/*" "76"
}

# generateSimple
# generateMibench
generateSimple2

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