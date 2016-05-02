# Loading grant data into an ElasticSearch index

We use `logstash` to insert the CSV fields into ES.

First, download CSV files from S3 using

```bash
aws s3 cp s3://grant-dataset/dedupe/deduped_grants.csv ../data/dedupe/
```

Then, convert CSV files into JSON format with the following script

```bash
python convert_to_json.py
```

Then, you need to replace `SERVER` in the *logstash* script
 `grantviewer_to_elasticsearch.conf`. Finally, run

 ```
 logstash -f grantviewer_to_elasticsearch.conf
 ```

This should take around 4 hours.
