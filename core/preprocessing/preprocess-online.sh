# KEY PARAMS
TRAIN_ROOT='/home/cyrus/Public/data_of_riskcog/data_of_huawei_by_28_11_2017/train_t'
TEST_ROOT='/home/cyrus/Public/data_of_riskcog/data_of_huawei_by_28_11_2017/test'
TRAIN_TARGET='train_clean'
TEST_TARGET='test_clean'
TH='0.7'
# IL='0.1'
WINDOW_SIZE=75
OVERLAP=0.5
LEAST_FILE_NUMBER=575 # only for train set

echo 'Data preprocessing starts ...'
echo 'Summary: '
echo " -root of train set: ${TRAIN_ROOT}"
echo " -root of test set: ${TEST_ROOT}"
echo " -target of train set: ${TRAIN_TARGET}"
echo " -target of test set: ${TEST_TARGET}"
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
echo -e " -Least file number(only for train set): ${LEAST_FILE_NUMBER} \n"

rm -rf temp*
cp -r ${TRAIN_ROOT} temp_train
echo -e "Copy ${TRAIN_ROOT} -> temp_train/"
cp -r ${TEST_ROOT} temp_test
echo -e "Copy ${TEST_ROOT} -> temp_test/" 
echo -e " -done\n"
echo "Check eqerr and zrerr"
echo "TRAIN SET"
for imei in `ls temp_train`
do
	echo "${imei}"
	for file_ in `ls temp_train/${imei}`
	do
        # eqerr check
        eqerr_state=$(python eqerr_check.py "temp_train/${imei}/${file_}" "${TH}")
        if [ ${eqerr_state} = '1' ]
        then
            echo " -remove ${imei}/${file_}"
            rm temp_train/${imei}/${file_}
            continue
        fi

        # jperr check
        # python jperr_check.py "temp_train/${imei}/${file_}" "temp_train/${imei}/${file_}" ${IL}

        # split data by zrerr
        python split.py -z "temp_train/${imei}/${file_}"
        rm temp_train/${imei}/${file_}
	done
	echo -e " -done\n"
done
echo "TEST SET"
for imei in `ls temp_test`
do
	echo "${imei}"
	for file_ in `ls temp_test/${imei}`
	do
        # eqerr check
        eqerr_state=$(python eqerr_check.py "temp_test/${imei}/${file_}" "${TH}")
        if [ ${eqerr_state} = '1' ]
        then
            echo " -remove ${imei}/${file_}"
            rm temp_test/${imei}/${file_}
            continue
        fi

        # jperr check
        # python jperr_check.py "temp_test/${imei}/${file_}" "temp_test/${imei}/${file_}" ${IL}

        # split data by zrerr
        python split.py -z "temp_test/${imei}/${file_}"
        rm temp_test/${imei}/${file_}
	done
	echo -e " -done\n"
done
# extrema check
echo "Extrema check"
echo "TRAIN SET"
python extrema_check.py -v -g temp_extrema temp_train temp_extrema
echo "TEST SET"
python extrema_check.py -v -g temp_extrema temp_test temp_extrema
echo -e " -done\n"
# normalization
echo "Normalization"
echo "TRAIN SET"
python normalization.py -v -g temp_extrema temp_train temp_nmlzt_train
echo "TEST SET"
python normalization.py -v -g temp_extrema temp_test temp_nmlzt_test
echo -e " -done\n"
# window sliding and Format
echo "Windows sliding and Format"
echo "TRAIN SET"
python window_sliding.py -l ${WINDOW_SIZE} -ol ${OVERLAP} -v temp_nmlzt_train temp_wd_train
python format2.py -n ${LEAST_FILE_NUMBER} -v temp_wd_train ${TRAIN_TARGET}
echo "TEST SET"
for imei in `ls temp_nmlzt_test`; do
	index=0
	mkdir -p temp_wd_test/${imei}/${imei}_${index}
	mkdir -p ${TEST_TARGET}/${imei}/${imei}_${index}
	for file in `ls temp_nmlzt_test/${imei}`; do
		mkdir -p temp_nmlzt_test/${imei}/${imei}_${index}/${index}
		mv temp_nmlzt_test/${imei}/${file} temp_nmlzt_test/${imei}/${imei}_${index}/${index}/${file}
		python window_sliding.py -l ${WINDOW_SIZE} -ol ${OVERLAP} temp_nmlzt_test/${imei}/${imei}_${index} temp_wd_test/${imei}/${imei}_${index}
		python format2.py -n 0 -np 0 -p 0 temp_wd_test/${imei}/${imei}_${index} ${TEST_TARGET}/${imei}/${imei}_${index}
		((index++))
	done
done
echo -e " -done\n"

rm -rf temp*
echo 'Data preprocessing over.'
