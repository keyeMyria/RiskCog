#!/usr/bin/env bash
export PATH=$PWD/bin:$PATH
find vw_train/  -name '*.cache' -or -name '*.vw' -or -name '*.arff' -or -name '*.libsvm'| xargs -i sudo rm {}
find vw_test/  -name '*.arff' -or -name '*.vw' | xargs -i sudo rm {}
