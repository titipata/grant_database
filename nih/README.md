# NIH Grant

All file from NIH grant can be downloaded [here](http://exporter.nih.gov/ExPORTER_Catalog.aspx).
We create bash to load and unzip all files from NIH website.

Run

```
./dl_nih.sh
```

This will download all grant to `data` folder. If you are not able to run then do `chmod` first

```
chmod +x dl_nih.sh
```

and run again

To create investigators dataset which contain PIs name, ID, Application ID, run
`python parse_pi.py`, this will create `nih_grant_investigators.csv` file
