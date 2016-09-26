
# commands to run experiments

for i in `cat list-small`;
   do echo $i;
   ./src/test.py $i;
done  > lfs-small-dp1exact.txt 

for i in `cat list-med`;
   do echo $i;
   ./src/test.py $i;
done  > lfs-med.txt

