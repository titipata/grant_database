# NSF Grants

All NSF award can be downloaded [here](https://www.nsf.gov/awardsearch/download.jsp).

Run

```
./dl_nsf.sh
```

This will download all grant to `data` folder. If you are not able to run then do `chmod` first

```
chmod +x dl_nsf.sh
```

and run again

This script will run `python dl_nsf.py` to create `nsf_awards.txt` which contains
link to zip file. Then it downloads and unzips all those zip files into `data` directory.

To parse all downloaded xml file in `data` folder, run `python parse_nsf.py`
(right now, we run sample of 50k xml, you can modify in the file to parse all).
This will generate `grant_info.csv` and `grant_investigators.csv` file
