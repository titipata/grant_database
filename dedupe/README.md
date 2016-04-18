## Dedupe grant dataset

This folder contains code aiming to create deduplicated
list of NSF and NIH investigators. See [README](https://github.com/titipata/grant_database)
in order to download cleaned grant dataset. Here, we assume that
you put `nih_grant_investigators.csv` and `nih_grant_info.csv` in `nih` folder and
`nsf_grant_info.csv` and `nsf_grant_investigators.csv` in `nsf` folder.


- **nsf investigators dedupe:** `dedupe_nsf.py` and `nsf_training.json` are files for dedupe NSF grant dataset.
run `python dedupe_nsf.py` in order to do active learning (type `f` to finish).
we can save `nsf_settings` file at the end of the training,
however, we are currently training `nsf_training.json`.

- **investigators linkage:** `link_grant.py` and `link_grant_training.json`
are files for doing record linkage between NIH and NSF database.
`fields` using for records linkage includes `full name`, `organization name`,
`organization city`. **note** we assume all NIH investigators have their
own unique applicants id.

- **affiliation dedupe:** run `python dedupe_affiliation.py` in order to train dedupe model.
By default, the settings will be saved in `affiliation_settings` and the training data will be saved in 
`affiliation_training.json`. Many parameters of the deduplication process can be tweaked by looking
at the parameters with `python dedupe_affiliation.py -h`. For example, to skip the console labeling step, run
`python dedupe_affiliation.py --skiplabel`.