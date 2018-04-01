# unchanged
Other_users_path = "/home/cyrus/Public/arffs"
RATIO = 5
test_predict_refuse_ACC=0.001
TRAIN_PROPORTION=3

# new
LABEL_BEGIN = 100
LABEL_TREE_DEPTH = 3
LABEL_TREE_SKEWNESS = 2
# In these multi-model-based system, all the box will be asked and give responses (accuracy).
# Decision will be made if the accuracy is in [BOX_IN_ACCURACY_LOWER, BOX_IN_ACCURACY_UPPER].
SIT_OR_WALK_THRESHOLD = 0.6
BOX_IN_ACCURACY_LOWER = 0.5
# deprecated, has to be 1, modified trainapp.views.UploadView#update_groud_id
TRAIN_FILE_GROUP_SIZE = 1
# TRAINING_TIME means how many models we will get in this system. (we don't delete past models)
TRAINING_TIME = 1000
# In production environment, test data we get may not be enough.
TEST_MIN_NUMBER_OF_LINES= 10


# no usage
number2start = 100
raw_numebr2start = 10
ACCURACY_TRESHOLD = 0.85
PRECISION_TRESHOLD = 0.85
RECALL_TRESHOLD = 0.85
BOX_IN_ACCURACY_UPPER = 1
NOISE_ACCURACY_UPPER= 0.1

# replaced by BOX_IN_ACCURACY_UPPER and BOX_IN_ACCURACY_LOWER
refuse_high_ACC=0.95

# meaningless
sumfilesneed = 300
pper_bound_file = 400
