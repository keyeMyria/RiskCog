# KEY PARAMS
# bash preprocess-offline2.sh ROOT TARGET
ROOT=$1
TARGET=$2
# config by yourself
TH='0.7'
# IL='0.1'
WINDOW_SIZE=75
OVERLAP=0.5
LEAST_FILE_NUMBER=575

echo 'Data preprocessing starts ...'
echo 'Summary: '
echo " -Root of data set: ${ROOT}"
echo " -Target of data set: ${TARGET}"
echo " -Preprocessing method adopted: eqerr, zrerr"
echo "Method: eqerr"
echo " -Threshold: ${TH}"
# echo "Method: jperr"
# echo " -a: ${IL}"
echo "Method: zrerr"
echo " -NO OPTION"
echo "Format: "
echo " -Window Size: ${WINDOW_SIZE}"
echo " -Overlap: ${OVERLAP}"
echo -e " -Least file number: ${LEAST_FILE_NUMBER} \n"

rm -rf temp*
cp -r ${ROOT} temp
echo -e "Copy ${ROOT} -> temp/ done\n"
echo -e "Check eqerr and zrerr"

for imei in `ls temp`
do
	echo "${imei}"
	for file_ in `ls temp/${imei}`
	do
        # eqerr check
        eqerr_state=$(python eqerr_check.py "temp/${imei}/${file_}" "${TH}")
        if [ ${eqerr_state} = '1' ]
        then
            echo " -remove ${imei}/${file_}"
            rm temp/${imei}/${file_}
            continue
        fi

        # jperr check
        # python jperr_check.py "temp/${imei}/${file_}" "temp/${imei}/${file_}" ${IL}

        # split data by zrerr
        python split.py -z "temp/${imei}/${file_}"
        rm temp/${imei}/${file_}
	done
	echo -e " -done\n"
done

# extrema check
echo "Extrema check"
python extrema_check.py -v temp_extrema temp temp_extrema
echo -e " -done\n"
# normalization
echo "Normalization"
python normalization.py -v temp_extrema temp temp_nmlzt
echo -e " -done\n"
# window sliding
echo "Windows sliding"
python window_sliding.py -l ${WINDOW_SIZE} -ol ${OVERLAP} -v temp_nmlzt temp_wd
echo -e " -done\n"
# format
echo "Format"
python format2.py -n ${LEAST_FILE_NUMBER} -v temp_wd ${TARGET}
echo -e " -done\n"
rm -rf temp*

echo 'Data preprocessing over.'
