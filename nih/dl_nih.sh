#!/bin/bash
# call this for everything if all files are already in place
# it will pass to nih_update.sh
# or nih_update can be called directly

# functions
getfilename() {
  if [[ $1 == project ]]; then echo 0; fi
  if [[ $1 == abstract ]]; then echo 1; fi
  if [[ $1 == publication ]]; then echo 2; fi
  if [[ $1 == patent ]]; then echo 3; fi
  if [[ $1 == clinical ]]; then echo 4; fi
  if [[ $1 == link ]]; then echo 5; fi
}

getlink() {
  if [[ $2 == new ]]; then
    filename=tempnew
  else
    filename=$1
  fi

  prefix="http://exporter.nih.gov/"
  wget http://exporter.nih.gov/ExPORTER_Catalog.aspx\?index\=$(getfilename $1) -O - | grep href=\"CSVs | sed -n 's/.*href="\([^"]*\).*/\1/p' | sed -e "s#^#$prefix#" >> $filename.txt
}

getalllink() {
  if [ ! -d $PWD/links ]; then
    mkdir $PWD/links
  fi
  cd links/
  getlink project; getlink abstract; getlink publication
  getlink patent; getlink clinical; getlink link
  cd ..
}

downloadzip() {
  if [ ! -d $PWD/data ]; then
    mkdir $PWD/data
  fi

  while read p; do
    foldername=$(echo $1 | awk -F'[/_]' '{print $2}')

    if [ ! -d data/$foldername ]; then
      mkdir data/$foldername
    fi

    wget -O data/$foldername/$(echo $p | awk -F'[/]' '{print $6}') $p
  done <$1.txt
}

downloadallzip() {
  for i in links/*.txt
  do
    # echo $i
    downloadzip ${i%.*}
  done
}

update() {
  cd links/
  if [[ -f tempnew.txt ]]; then rm tempnew.txt; fi
  if [[ -f sold.txt ]]; then rm sold.txt; fi
  if [[ -f snew.txt ]]; then rm snew.txt; fi
  filename=$1

  getlink $1 new

  sort tempnew.txt >> snew.txt
  sort $1.txt >> sold.txt

  notexist=$(comm -23 snew.txt sold.txt)

  if [ ! -z "${notexist}" ] # check if this variable empty or not
  then
    echo $(date +"%Y-%m-%d %H:%M:%S") >> new_$1.log
    echo $notexist | tr ' ' '\n' >> new_$1.log

    # go back one step
    cd ..
    echo $notexist | tr ' ' '\n' >> temp_$1.txt

    downloadzip temp_$1
    rm temp_$1.txt
    cd links/
  fi

  rm tempnew.txt sold.txt snew.txt
  cd ..
}

updateall() {
  update project; update abstract; update publication
  update patent; update clinical; update link
}

# unzip all files
unzipall() {
  for folder in $PWD/data/*/
  do
    echo $folder
    for file in $folder*.zip
    do
      if [[ ! -d ${file%.*} ]]
      then
        unzip -q $file -d ${file%.*} # remove q for verbose output
        echo unzipped ${file##*/}
      else
        echo already unzip ${file##*/}..
      fi
    done
  done
}

# call arguments verbatim:
"$@"
