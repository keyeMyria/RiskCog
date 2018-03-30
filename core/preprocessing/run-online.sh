# Step 1 prepare sets of data and update the root
tx_root='/home/cyrus/Public/data_of_riskcog/data_of_tx_top_6'
train_root='/home/cyrus/Public/data_of_riskcog/data_of_huawei_by_28_11_2017/train'
train_imei='861955030016110'
test_self_root='/home/cyrus/Public/data_of_riskcog/data_of_huawei_by_28_11_2017/test_self'
test_other_root='/home/cyrus/Public/data_of_riskcog/data_of_huawei_by_28_11_2017/test_other'

# Step 2 make sure that all scripts are available
# Checklist (these scripts below should be in the same directory)
# preprocess-offline2.sh
# format2.py
# window_sliding.py
# normalization.py
# extrema_check.py
# split.py
# zrerr_check.py
# eqerr_check.py
# lstm_offline.py
# plot.py

# Step 3 update some paramaters in "preprocess-offline2.sh"
# then update the params below
your_target="./${train_imei}" # give a name to your target directory
classes=7 # the number of classes
epoches=50

# Step 4 train
rm -rfv ./model ${your_target} ${your_target}_log
mkdir -v ./model ${your_target}

mkdir mix
cp -r ${train_root}/${train_imei} mix/
cp -r ${tx_root}/* mix/
# preprocessing
bash preprocess-online-train.sh ${train_imei} mix ${your_target}
# train
python lstm_online_train.py ${epoches} $[classes] ${your_target}

# Step 5 test
for file_self in `ls ${test_self_root}`; do
	bash preprocess-online-test.sh ${train_imei} ${file_self} ${test_self_root} test_self_${file_self}
	python lstm_online_test.py ${classes} ${train_imei} test_self_${file_self}
	rm -r test_self_${file_self}
done
for file_other in `ls ${test_other_root}`; do
	bash preprocess-online-test.sh ${train_imei} ${file_other} ${test_other_root} test_other_${file_other}
	python lstm_online_test.py ${classes} ${train_imei} test_other_${file_other}
	rm -r test_other_${file_other}
done

# python plot.py ${your_target}_log
rm -rf mix

# done
