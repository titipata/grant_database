# Grant database

We create a downloader, parser and database for NIH and NSF grant generating
from their website. The link for NSF awards data is [here](https://www.nsf.gov/awardsearch/download.jsp) and
for NIH award is [here](http://exporter.nih.gov/ExPORTER_Catalog.aspx).

Check out [`nih`](/nih) and [`nsf`](/nsf) folder, we provide bash and
python script to download and parse data into `csv` file.


## Download cleaned data from Amazon S3

First, you have to install `awscli` using `pip` (see this [instruction](http://docs.aws.amazon.com/cli/latest/userguide/installing.html)).
We now provide parsed data of NSF. You can use `awscli` to download as follows:

```
aws s3 cp s3://grant-dataset/nih . --recursive --region us-west-2 # for nih grant dataset
aws s3 cp s3://grant-dataset/nsf . --recursive --region us-west-2 # for nsf grant dataset
```


## Install dependencies

We have `pandas` and `lxml` as an dependencies provided in `requirements.txt`.
You can install the dependencies using `pip`.

```
pip -r install requirements.txt
```


## Members

- [Titipat Achakulvisut](http://titipata.github.io/)
- [Tulakan Ruangrong](http://bluenex.github.io/)
- [Daniel Acuna](http://www.scienceofscience.org/)
