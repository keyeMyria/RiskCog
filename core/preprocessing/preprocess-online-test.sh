# KEY PARAMS
IMEI=$1
TEST_FILE=$2
TEST_ROOT=$3
TEST_TARGET=$4

TH='0.7'
# IL='0.1'
WINDOW_SIZE=75
OVERLAP=0.5
LEAST_FILE_NUMBER=575 # only for train set

echo 'Data preprocessing starts ...'
echo 'Summary: '
echo " -root of test set: ${TEST_ROOT}"
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
mkdir -p temp_test/${IMEI}
cp ${TEST_ROOT}/${TEST_FILE} temp_test/${IMEI}/${TEST_FILE}
echo -e "Copy ${TEST_ROOT}/${TEST_FILE} -> temp_test/${IMEI}/${TEST_FILE}"
echo -e " -done\n"
echo "Check eqerr and zrerr"
# Eqerr check
echo "Eqerr check"
eqerr_state=$(python eqerr_check.py "temp_test/${IMEI}/${TEST_FILE}" "${TH}")
if [ ${eqerr_state} = '1' ]
then
	echo " -invalid"
	exit 1
fi
echo -e " -done\n"
# jperr check
# python jperr_check.py "temp_test/${imei}/${file_}" "temp_test/${imei}/${file_}" ${IL}
# Split data by zrerr
echo "Split data by zrerr"
python split.py -z "temp_test/${IMEI}/${TEST_FILE}"
rm temp_test/${IMEI}/${TEST_FILE}
echo -e " -done\n"
# normalization
echo "Normalization"
python normalization.py -v extrema temp_test temp_nmlzt_test
echo -e " -done\n"
# window sliding
echo "Windows sliding"
python window_sliding.py -l ${WINDOW_SIZE} -ol ${OVERLAP} temp_nmlzt_test temp_wd_test
# Format
echo "Format"
python format2.py -n 0 -np 0 -p 0 temp_wd_test ${TEST_TARGET}
echo -e " -done\n"

rm -rf temp*
echo 'Data preprocessing over.'
