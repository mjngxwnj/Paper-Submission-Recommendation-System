#!/bin/bash

USER=admin
PGPASSWORD=admin
DB=rcm_papers

docker cp ./paper.csv postgres:/tmp/paper.csv
docker cp ./venue.csv postgres:/tmp/venue.csv
docker cp ./keyword.csv postgres:/tmp/keyword.csv
docker cp ./paper_keyword.csv postgres:/tmp/paper_keyword.csv

echo "CSV copied into postgres container."

docker exec -e PGPASSWORD=$PASSWORD -i postgres \
  psql -U $USER -d $DB <<EOF
COPY core.paper FROM '/tmp/paper.csv' CSV HEADER;
COPY core.venue FROM '/tmp/venue.csv' CSV HEADER;
COPY core.keyword FROM '/tmp/keyword.csv' CSV HEADER;
COPY core.paper_keyword FROM '/tmp/paper_keyword.csv' CSV HEADER;
EOF

echo "Done"
