import os
import tools

filefilter = [
    '20170921072048',
]

def frequency_domain_wave(dir):
    files = os.listdir(dir)

    for file in files:
        if file in filefilter:
            print '# handle file', file
            data = tools.getSensorData(os.path.join(dir, file), 'acceleration', 'gravity', 'gyroscope')
            # data = tools.getSensorData(os.path.join(dir, file), 'gyroscope')
            # a = data['gyroscope']
            # tools.plot3axisWave('{0}_{1}'.format(file, 'gyroscope'), a[0][:], a[1][:], a[2][:], len(a[0]))
            a = data['acceleration']
            a = [tools.getFFT(a[i]) for i in range(0, len(a))]
            tools.plot3axisWave('{0}_{1}'.format(file, 'acceleration'), a[0][:], a[1][:], a[2][:], len(a[0]))
            # a = data['gravity']
            # tools.plot3axisWave('{0}_{1}'.format(file, 'gravity'), a[0][:], a[1][:], a[2][:], len(a[0]))


if __name__ == '__main__':
    dir_ = '/home/cyrus/Public/data_of_riskcog/data_of_huawei_by_28_11_2017/test_set_by_eed/861955030016110eed'
    frequency_domain_wave(dir_)
