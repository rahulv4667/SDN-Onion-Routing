counter=6633
countend=6640
while [ "$counter" -le "$countend" ]
do

	sudo fuser -n tcp -k $counter
	((counter++))
done
sudo mn -c

