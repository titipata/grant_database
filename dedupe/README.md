## Dedupe grant data

This folder contains code aiming to create deduplicated
list of NSF and NIH investigators. See [README](https://github.com/titipata/grant_database)
in order to download cleaned grant dataset.

- `dedupe_nsf.py` and `nsf_training.json` are files for dedupe NSF grant dataset.
run `python dedupe_nsf.py` in order to do active learning (type `f` to finish).
we can save `nsf_settings` file at the end of the training,
however, we are currently training `nsf_training.json`.

- we assume all NIH investigators have their own unique applicants id.

- `link_grant.py` and `link_grant_training.json` are files for doing
record linkage between NIH and NSF database. `fields` using for records linkage
includes `full name`, `organization name`, `organization city`
