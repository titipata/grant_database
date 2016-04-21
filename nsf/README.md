# NSF Grants

All NSF award can be downloaded [here](https://www.nsf.gov/awardsearch/download.jsp).

Run

```
source dl_nsf.sh
```

This will download all grant to `data` folder.

This script will also run `python dl_nsf.py` to create `nsf_awards.txt` which contains
the links to zip files. Then it downloads and unzips all those zip files into the `data` directory.

To parse all downloaded xml files in `data` folder, run `python parse_nsf.py`.
This will generate `nsf_grant_info.csv` and `nsf_grant_investigators.csv` file
