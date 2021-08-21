FLA='FLAs'
SUB='SUB'
BCF='BCF'

PERC=30
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
	do
		for prot in 'OH' 'CFI' 'SC' ;
		do
			for combination in "$@";
			do
				#generator-prot-obf.sh OH FLAs-SUB-BCF coverage mibench-OH-FLAs-SUB-BCF
				comb_dir="${combination/FLAs/FLA}"
				comb_dir="${comb_dir/BCF/BCF$PERC}"
				waitforjobs $(nproc)
				echo generator-prot-obf.sh $prot $combination $ds "$GENERATIONPATH/$OUT_DIR/$comb_dir"
				bash generator-prot-obf.sh $prot $combination $ds "$GENERATIONPATH/$OUT_DIR/$comb_dir" > /dev/null &
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
  OUT_DIR='mibench-cov'

  cp mibench-dataset-6/* dataset/ &&
    cp mibench-dataset/* dataset/ &&
    rm dataset/cjpeg.x.bc && rm dataset/djpeg.x.bc && # Remove programs that cause crash
    bash coverage-improver.sh dataset mibench-cov/ &&
    bash combinator.sh mibench-cov/ combinations

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
	OUT_DIR='simple-cov'

	edit 30
	generate "NONE"
	generate "$BCF" "$FLA-$BCF" "$BCF-$FLA" "$SUB-$BCF" "$BCF-$SUB" "$FLA-$BCF-$SUB" "$FLA-$SUB-$BCF" "$BCF-$FLA-$SUB" "$BCF-$SUB-$FLA" "$SUB-$FLA-$BCF" "$SUB-$BCF-$FLA" "$SUB" "$FLA" "$SUB-$FLA" "$FLA-$SUB"
	verifyCountFiles "$GENERATIONPATH/$OUT_DIR/*" "160"
}

function generateSimple2 {
	DATASET='simple-cov'
	OUT_DIR='simple-cov2'

	generate "NONE"
	edit 30
	generate "$BCF" "$FLA-$BCF" "$BCF-$FLA" "$SUB-$BCF" "$BCF-$SUB" "$FLA-$BCF-$SUB" "$FLA-$SUB-$BCF" "$BCF-$FLA-$SUB" "$BCF-$SUB-$FLA" "$SUB-$FLA-$BCF" "$SUB-$BCF-$FLA" "$SUB" "$FLA" "$SUB-$FLA" "$FLA-$SUB" "$BCF-$FLA"2 "$BCF-$FLA"2"-$SUB"2 "$BCF-$SUB"2"-$FLA"2

	verifyCountFiles "$GENERATIONPATH/$OUT_DIR/*" "76"

	#edit bogus contrl flow to 40
	edit 40
	generate "$BCF" "$BCF-$FLA" "$BCF-$FLA-$SUB" "$BCF-$SUB" "$BCF-$SUB-$FLA" "$FLA-$BCF" "$FLA-$BCF-$SUB" "$FLA-$SUB-$BCF" "$SUB-$BCF" "$SUB-$BCF-$FLA" "$SUB-$FLA-$BCF"
	verifyCountFiles "$GENERATIONPATH/$OUT_DIR/*" "76"
	edit 100
	generate "$BCF" "$BCF-$FLA" "$BCF-$FLA-$SUB" "$BCF-$SUB" "$BCF-$SUB-$FLA" "$FLA-$BCF" "$FLA-$BCF-$SUB" "$FLA-$SUB-$BCF" "$SUB-$BCF" "$SUB-$BCF-$FLA" "$SUB-$FLA-$BCF"
	verifyCountFiles "$GENERATIONPATH/$OUT_DIR/*" "76"
}

generateSimple
generateMibench
generateSimple2
