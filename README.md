# Grant database

We create a downloader, parser and database for NIH and NSF grant generating
from their website. The link for NSF awards data is [here](https://www.nsf.gov/awardsearch/download.jsp) and
for NIH award is [here](http://exporter.nih.gov/ExPORTER_Catalog.aspx).

Check out [`nih`](/nih) and [`nsf`](/nsf) folder, we provide bash and
python script to download and parse data into `csv` file. Also checkout
[`dedupe`](/dedupe) folder soon where we put script to deduplicate and link
NIH/NSF grant together.


## Download cleaned data from Amazon S3

First, you have to install `awscli` using `pip` (see this [instruction](http://docs.aws.amazon.com/cli/latest/userguide/installing.html)).
We now provide parsed data of NSF. You can use `awscli` to download as follows:

```bash
aws s3 cp s3://grant-dataset/ data/ --recursive --exclude dedupe/ --region us-west-2 # download nih, nsf, and grid data
```

This contains around 2M grants (1.7 Gb) from NIH and 500k grants from NSF (700 Mb).


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
