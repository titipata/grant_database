python dl_nsf.py # load to nsf

# check whether there is already data folder or not
if [ ! -d $PWD/data ]; then
  mkdir $PWD/data
fi

# download all
while read p; do
  # echo $p | egrep -o [0-9]+ # extract only number but there is also
  # https://www.nsf.gov/awardsearch/download?DownloadFileName=2009&All=true
  # echo grep -oP '(?<=DownloadFileName=).*?(?=&)' <<< "$p" # -P doesn't work on Mac anymore
  wget -O data/$(echo $p | awk -F'[=&]' '{print $2}').zip $p
done <nsf_awards.txt

# unzip all files
for z in $PWD/data/*
do
  unzip -q $z -d ${z%.*} # remove q for verbose output
  echo unzipped ${z##*/}
done

# to parse nsf data, run the follow
# python parse_nsf.py