PERMIT_1_OR_2_REMAINING_POINTS = True
PERMIT_RANDOM_SEED = False

# Testing seed...
# seed with 2 lines left : 13300
# seed with 1 point left : 1330
# number_points = 51

RANDOM_SEED = 1330
#POINTS_LIST = [1,5,10,50,100,250,500,1000,2000,3000,4000,5000,6000,7000,8000,9000,10000]
POINTS_LIST = [50, 100, 1000, 5000, 10000]


X_LIM = 1000
Y_LIM = 1000
X_WINDOW = 16
Y_WINDOW = 12

REMAINING_POINTS_COMPUTE_CH = 1
POINTS_RANGE = 1000

LET_ANIMATION = True
ANIMATION_INTERVAL_MS = 300


# Options: 'grid', 'random', 'collinear'
GEN_MODE = "grid"

# this is really bad, don't change it.
# in the main.py window caption should be changed such that for each number in
# POINTS_LIST will have a diff caption
NUMBER_POINTS = 10000


CHECKED_HULL_COLOR = 'gray'
CURRENT_HULL_COLOR = 'red'
POINTS_COLOR = 'black'
POINT_SIZE = 100
LINE_SIZE = 5
CHECKED_POINTS_COLOR = 'gray'
