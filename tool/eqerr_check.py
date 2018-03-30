"""
Equal value error check tool.

Usage:
    python eqerr_check.py [-v] YOUR_PATH THRESHOLD

Return:
    Return 1 when one of sensors' three axes's equle value ratios are
larger than THRESHOLD

Args:
    -v: show details on every axis
    YOUR_PAHT: file path to be checked
    THRESHOLD: see 'Return'

Author:
    Qiang Liu
"""

import sys
import os


def getSensorData(path, *sensor):
    """
    Input the sensor data in standard format and split them into lists.
    Tell the sensor or sensors you want with a list. What you can use are
    'acceleration', 'gyroscope' and 'gravity'.

    :param path: full path of the file containing sensor data
    :param sensor: the sensor or sensors you want
    :return: dict for sensor data like {'accelertaion':[],}
    """

    with open(path) as f:
        lines = f.readlines()
        f.close()

        acceleration = [[], [], []]
        gravity = [[], [], []]
        gyroscope = [[], [], []]

        for i in range(0, len(lines), 9):
            if 'acceleration' in sensor:
                acceleration[0].append(lines[i + 0])
                acceleration[1].append(lines[i + 1])
                acceleration[2].append(lines[i + 2])
            if 'gyroscope' in sensor:
                gyroscope[0].append(lines[i + 3])
                gyroscope[1].append(lines[i + 4])
                gyroscope[2].append(lines[i + 5])
            if 'gravity' in sensor:
                gravity[0].append(lines[i + 6])
                gravity[1].append(lines[i + 7])
                gravity[2].append(lines[i + 8])

    sensor_data = {}
    if 'acceleration' in sensor:
        sensor_data['acceleration'] = acceleration
    if 'gyroscope' in sensor:
        sensor_data['gyroscope'] = gyroscope
    if 'gravity' in sensor:
        sensor_data['gravity'] = gravity
    return sensor_data


def get_equal_value_info(sensor_data):
    """
    Input an array generated by the mothod 'tools.getSensorData' like below:
        s_d = getSensorData(full_path, 'acceleration', 'gravity', 'gyroscope')
        # key is sensor and value is sensor data
        for key, value in s_d.items():
            results = get_equal_value_info(value)
    Reture the position and the ratio of equal values in the array. The return
    is like below:
        {'x':{'position':[(position_start, length), ], 'ratio':0.01}, }


    :param sensor_data: format [[], [], []]
    :return:{'x':{'position':[(position_start, length), ], 'ratio':0.01}, }
    """

    result = {'x': {'position': [], 'ratio': .0},
              'y': {'position': [], 'ratio': .0},
              'z': {'position': [], 'ratio': .0}}

    for axis, item in enumerate(sensor_data):
        last = None
        start = 0
        length = 1
        number = 0
        for index, element in enumerate(item):
            # It's search problem.
            if last is None:
                # first one
                start = index
                last = element
                continue

            if element == last:
                length += 1
                if index == len(item) - 1:
                    if axis == 0:
                        result['x']['position'].append((start, length))
                    elif axis == 1:
                        result['y']['position'].append((start, length))
                    else:
                        result['z']['position'].append((start, length))
                    number += length
            else:
                last = element
                if not length == 1:
                    if axis == 0:
                        result['x']['position'].append((start, length))
                    elif axis == 1:
                        result['y']['position'].append((start, length))
                    else:
                        result['z']['position'].append((start, length))
                    number += length
                # refresh for new one
                start = index
                length = 1

        # update ratio
        if axis == 0:
            result['x']['ratio'] = float(number) / len(item)
        elif axis == 1:
            result['y']['ratio'] = float(number) / len(item)
        else:
            result['z']['ratio'] = float(number) / len(item)

    return result


def isEqualError(path, th):

    result = 0

    invalidation_count = 0
    match = {'x': 0, 'y': 1, 'z': 2}

    s_d = getSensorData(path, 'acceleration', 'gravity', 'gyroscope')
    # key is sensor and value is sensor data
    for key, value in s_d.items():
        # print(key, get_equal_value_info(value))
        results = get_equal_value_info(value)
        # print ('sensor: {0}'.format(key))
        # k is axis and v is result of this axis's detection
        valid = 0
        for k, v in results.items():
            # print ('sensor: {2} axis: {0} ratio: {1}'.format(k, v['ratio'], key))
            if float(v['ratio']) >= th:
                valid += 1
        if valid == 3:
            result += 1

    if result:
        # there exists equal value error
        return 1
    else:
        # good 
        return 0

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print 'Usage: python eqerr_check.py [-v] YOUR_PATH THRESHOLD'
        print "Return: Return 1 when one of sensors' three axes's equle value ratios are larger than THRESHOLD"
        exit(-1)

    # get parameters
    verbose = False
    if sys.argv[1].startswith('-'):
        option = sys.argv[1][1:]
        if option == 'v':
            verbose = True
        if len(sys.argv) != 4:
            print('Usage: python eqerr_check.py [-v] YOUR_PATH THRESHOLD')
            exit(-1)
    else:
        if len(sys.argv) != 3:
            print('Usage: python eqerr_check.py [-v] YOUR_PATH THRESHOLD')
            exit(-1)
    path = sys.argv[-2]
    th = float(sys.argv[-1])

    result = isEqualErro(path, th)

    print result
