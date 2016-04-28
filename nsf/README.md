# NSF Grants

All NSF award can be downloaded [here](https://www.nsf.gov/awardsearch/download.jsp).

Run

```bash
source dl_nsf.sh
```

This script will download all grant to `data` folder.
It will first run `python dl_nsf.py` to create `nsf_awards.txt` which contains
all links to zip files in NSF page. Then it downloads and unzips all downloaded
zip files into the `data` directory.

To parse all downloaded xml files in `data` folder, you have to run

```bash
python parse_nsf.py
```

This will generate `nsf_grant_info.csv` and `nsf_grant_investigators.csv` file.
