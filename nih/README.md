# NIH Grant

All file from NIH grant can be downloaded [here](http://exporter.nih.gov/ExPORTER_Catalog.aspx).
We create bash to load and unzip all files from NIH website.

First we will download all the available links and save into `txt` files.

```
./dl_nih.sh getalllink
```

Then we will download all the zip files from those links.

```
./dl_nih.sh downloadallzip
```

And we can now unzip all those downloaded zip files.

```
./dl_nih.sh unzipall
```

If you need to update the data you can run:

```
./dl_nih.sh updateall && ./dl_nih.sh unzipall
```

To create investigators dataset which contain PIs name, ID, Application ID, run
`python parse_pi.py`, this will create `nih_grant_investigators.csv` file
