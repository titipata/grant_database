# http://exporter.nih.gov/XMLData/final/RePORTER_PRJABS_X_FY2016_026.zip
#
#   wget http://exporter.nih.gov/ExPORTER_Catalog.aspx\?index\=4 -O data/cli.html
#
# $(cat data/${file##*/} | grep href=\"CSVs | sed -n 's/.*href="\([^"]*\).*/\1/p')
#
# a=$(wget http://exporter.nih.gov/ExPORTER_Catalog.aspx\?index\=4 -O -)
# b=$(echo $(wget http://exporter.nih.gov/ExPORTER_Catalog.aspx\?index\=4 -O -) | grep href=\"CSVs | sed -n 's/.*href="\([^"]*\).*/\1/p')
#
# b=$(wget http://exporter.nih.gov/ExPORTER_Catalog.aspx\?index\=4 -O - | grep href=\"CSVs | sed -n 's/.*href="\([^"]*\).*/\1/p')
#
# wget http://exporter.nih.gov/ExPORTER_Catalog.aspx\?index\=4 -O - | grep href=\"CSVs | sed -n 's/.*href="\([^"]*\).*/\1/p'
#
# mydate=$(date)
# awk -v d="$inp" -F"," 'BEGIN { OFS = "," } {$2=d; print}' test.csv > output.csv

# 0 project
# 1 abstract
# 2 publication
# 3 patent
# 4 clinical
# 5 link

# rm *.txt

getfilename() {
  # if [[ $1 == 0 ]]; then echo project; fi
  # if [[ $1 == 1 ]]; then echo abstract; fi
  # if [[ $1 == 2 ]]; then echo publication; fi
  # if [[ $1 == 3 ]]; then echo patent; fi
  # if [[ $1 == 4 ]]; then echo clinical; fi
  # if [[ $1 == 5 ]]; then echo link; fi
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
  # echo $filename

  prefix="http://exporter.nih.gov/"
  wget http://exporter.nih.gov/ExPORTER_Catalog.aspx\?index\=$(getfilename $1) -O - | grep href=\"CSVs | sed -n 's/.*href="\([^"]*\).*/\1/p' | sed -e "s#^#$prefix#" >> $filename.txt
}

# getlink project
# getlink abstract
# getlink publication
# getlink patent
# getlink clinical
# getlink link

downloadzip() {
  if [ ! -d $PWD/data ]; then
    mkdir $PWD/data
  fi

  while read p; do
    # echo $1 # full path
    foldername=$(echo $1 | awk -F'[_]' '{print $2}')
    # echo $foldername
    # echo ${p%.*} # filename
    # echo ${p##*/} # full path without extension
    # filename="${file##*/}"
    # foldername="${filename%.*}"
    # echo $filename # doing this file
    #
    # check whether there is already data folder or not
    if [ ! -d data/$foldername ]; then
      mkdir data/$foldername
    fi

    # echo $p | awk -F'[/ ]' '{print $6}'
    wget -O data/$foldername/$(echo $p | awk -F'[/]' '{print $6}') $p
    #
    # loop through html file and search for pattern starts with href=\"CSVs
    # for i in $(cat data/${file##*/} | grep href=\"CSVs | sed -n 's/.*href="\([^"]*\).*/\1/p')
    # do
    #   # echo data/$foldername/$(echo $i | awk -F'[/]' '{print $3}')
    #   wget -O data/$foldername/$(echo $i | awk -F'[/]' '{print $3}') $prefix$i
    # done
  done <$1.txt
}

# downloadzip new_project

checkdiff() {
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
    # echo $(date +"%Y-%m-%d %H:%M:%S") >> new_$(getfilename $1).log
    # echo $notexist | tr ' ' '\n' >> new_$1.log
    echo $notexist | tr ' ' '\n' >> temp_$1.txt
    downloadzip temp_$1
    # rm temp_$1.txt
  fi
  # echo $(getfilename $1).txt
  # echo $notexist

  # rm tempnew.txt, sold.txt, snew.txt
  cd ..
}

checkdiff project

# notexist=$(comm -2 -3 <(sort abstract.txt) <(sort old_abstract.txt))

# if [ -z "${k}" ]; then
#     echo "VAR is unset or set to the empty string"
# fi

# ## download all
# getlink 0 project
# getlink 1 abstract
# getlink 2 publication
# getlink 3 patent
# getlink 4 clinical
# getlink 5 link
