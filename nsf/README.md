# NSF Grants

All NSF award can be downloaded [here](https://www.nsf.gov/awardsearch/download.jsp).

Run

```
./dl_nsf.sh
```

If you are not able to run then do `chmod` first

```
chmod +x dl_nsf.sh
```

and run again

This script will run `python download_award_links.py` to create `nsf_awards.txt` which contains
link to zip file. Then it downloads and unzips all those zip files into `data` directory.
