# Grant Summary

We put all summarize function in this folder. First, you can download
deduped affiliation dataset of NIH and NSF grants from Amazon S3 as follows:

```bash
aws s3 cp s3://grant-dataset/dedupe/deduped_grants.csv ../data/.
aws s3 cp s3://grant-dataset/dedupe/deduped_affiliations.csv ../data/.
```

**note** `deduped_grants.csv` size is 4.6 GB

Run `python summarize_grants.py --index 2854 --type 'nsf'` in order to plot number
of NSF grants per year of institution that has `dedupe_id = 2854` to `grant_summary.html`
using [`bokeh`](http://bokeh.pydata.org/en/latest/)
