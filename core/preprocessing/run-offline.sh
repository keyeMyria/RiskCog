# Step 1 prepare sets of data and update the root
# raw data should be organised like:
# your_root/user1/file1
# your_root/user2/file2
# your_root='/home/cyrus/Public/data_of_riskcog/data_of_tx_top_6'
your_root='/home/cyrus/Public/data_of_riskcog/data_of_huawei_by_28_11_2017/train'

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
your_target='./target' # give a name to your target directory
classes=6 # the number of classes
epoches=50

# Step 4 train
rm -rfv ./model ${your_target} ${your_target}_log
mkdir -v ./model ${your_target}
# preprocessing
bash preprocess-offline2.sh ${your_root} ${your_target}
# train
python lstm_offline.py ${epoches} ${classes} ${your_target} | tee ${your_target}_log

# Step 5 plot the result
python plot.py ${your_target}_log

# done
