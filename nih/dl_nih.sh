# example link
# http://exporter.nih.gov/XMLData/final/RePORTER_PRJABS_X_FY2016_026.zip

# check whether there is already data folder or not
if [ ! -d $PWD/data ]; then
  mkdir $PWD/data
fi

## download html files if not exist
if [[ ! -f data/proj.html ]]; then
  wget http://exporter.nih.gov/ExPORTER_Catalog.aspx\?index\=0 -O data/proj.html
fi
if [[ ! -f data/abs.html ]]; then
  wget http://exporter.nih.gov/ExPORTER_Catalog.aspx\?index\=1 -O data/abs.html
fi
if [[ ! -f data/pub.html ]]; then
  wget http://exporter.nih.gov/ExPORTER_Catalog.aspx\?index\=2 -O data/pub.html
fi
if [[ ! -f data/pat.html ]]; then
  wget http://exporter.nih.gov/ExPORTER_Catalog.aspx\?index\=3 -O data/pat.html
fi
if [[ ! -f data/cli.html ]]; then
  wget http://exporter.nih.gov/ExPORTER_Catalog.aspx\?index\=4 -O data/cli.html
fi
if [[ ! -f data/link.html ]]; then
  wget http://exporter.nih.gov/ExPORTER_Catalog.aspx\?index\=5 -O data/link.html
fi

# set prefix for download links
prefix="http://exporter.nih.gov/"

for file in $PWD/data/*.html
do
  # echo $file # full path
  # echo ${file%.*} # filename
  # echo ${file##*/} # full path without extension
  filename="${file##*/}"
  foldername="${filename%.*}"
  echo $filename # doing this file

  # check whether there is already data folder or not
  if [ ! -d data/$foldername ]; then
    mkdir data/$foldername
  fi

  # loop through html file and search for pattern starts with href=\"CSVs
  for i in $(cat data/${file##*/} | grep href=\"CSVs | sed -n 's/.*href="\([^"]*\).*/\1/p')
  do
    # echo data/$foldername/$(echo $i | awk -F'[/]' '{print $3}')
    wget -O data/$foldername/$(echo $i | awk -F'[/]' '{print $3}') $prefix$i
  done
done

# unzip all files
for folder in $PWD/data/*/
do
  echo $folder
  for file in $folder*
  do
  unzip -q $file -d ${file%.*} # remove q for verbose output
  # echo unzipped ${z##*/}
  echo $file
  done
done

# rm cli.html link.html proj.html abs.html pat.html pub.html
