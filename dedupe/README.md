## Dedupe grant dataset


This folder contains code aiming to create deduplicated
list of NSF and NIH investigators. See [README](https://github.com/titipata/grant_database)
in order to download cleaned grant dataset from Amazon S3. Here, we assume that you download
dataset from S3 to `data` folder (`data/grid`, `data/nih` and `data/nsf`) and
run the script in this folder.


- **NSF investigators dedupe:** dedupe NSF investigators is `dedupe_nsf_investigator.py`.
Run `python dedupe_nsf.py` in order to run active learning part.

- **Investigators linkage:** record linkage between NIH and NSF investigators is
located in `link_investigator.py`. We assume all NIH investigators have their
own unique applicants id, that is, we don't have to dedupe NIH investigators.

- **Affiliations dedupe:** run `python dedupe_affiliation.py` in order to dedupe
affiliation across NIH and NSF grants. Many parameters of the deduplication process
can be tweaked by looking at the parameters with `python dedupe_affiliation.py -h`.
For example, to skip the console labeling step, run `python dedupe_affiliation.py --skiplabel`.

- **Affiliations linkage:** record linkage script between deduped NIH and NSF
affiliations and GRID database is in `link_affiliation.py`.
