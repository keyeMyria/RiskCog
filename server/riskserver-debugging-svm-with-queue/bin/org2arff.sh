#!/bin/bash

BASEDIR=$(dirname "$0")

if [ $# -ne 2 ]
then
	echo make_arff.sh path target_path
 	exit
fi

path=$1
target_path=$2

#check data is lie 


#check sit or walk
echo "checking sit or walk..."
find $path -maxdepth 1 -type f   |  xargs -i check_sit_or_walk.exe {} | cat > files
cat files | awk -F/ '{print $0 , "imei"}' > log
determine.exe 0.5
if [ ! -d "$target_path" ]
then 
	mkdir -p $target_path
fi

mkdir $target_path/walk
mkdir $target_path/sit

while read file  state
do
        echo "make arff..."
	filename=`basename $file`
	$BASEDIR/make_arff.exe $file 1 $state > $target_path/$state/$filename.arff
done < out

rm log
rm out
rm files
#start make arffs
#echo "starting make arffs"
#mkdir arffs
#ls imei/ > files
#cat files | xargs -i mkdir arffs/{}
#cp tools/make_arff.exe .
#find imei/ -type f | grep dataset > files
#cat files | awk -F/ '{print "./make_arff.exe",$0,$2,$4,">" , "arffs/"$2"/"$5$4 }' | parallel
#grep "\-nan" -rl arffs > files
#cat files | xargs -i sed -i "s/\-nan/0/g" {}


#echo "origin arffs maked"

#find . -type d -empty | xargs -i rm -r {}

