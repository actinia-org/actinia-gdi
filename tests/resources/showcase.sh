#!/bin/bash

#./showcase.sh local test postbody.processes.success.json

### Set variables
if [ $# = 0 ]
then
  echo "no profile specified";exit 0
fi

setlocal () {
    echo "using local profile"
    actinia_core_auth='actinia-gdi:actinia-gdi'
    actinia_core_baseUrl="127.0.0.1:8088"
    actinia_gdi_baseUrl="127.0.0.1:5000"
}

settest () {
    url="$actinia_gdi_baseUrl/processes/test/jobs"
}
sets1 () {
    url="$actinia_gdi_baseUrl/processes/sentinel1/jobs"
}


case $1 in
  local) setlocal;;
  *) echo -e "$1 not recognized as parameter. Aborting";exit 1;;
esac

case $2 in
  test) settest;;
  s1) sets1;;
  *) echo -e "$1 not recognized as parameter. Aborting";exit 1;;
esac

json=$3

if [ -z $json ]
then
    echo "no json file specified"
    exit 0
else
    echo "using json file: $json"
fi


### Start jobs
echo "Posting to $url..."

curl -X POST $url \
   -H 'accept: application/json' \
   -H 'Content-Type: application/json' \
   -d @${json} > \
   resp.json && cat resp.json

### Check status
# read ids from response
actinia_gdi_id=$(cat resp.json | json idpk_jobs)
actinia_core_id=$(cat resp.json | json actinia_core_jobid)

# check job status in actinia-gdi
if [ -z $actinia_gdi_id ]
then
    echo -e "\n no actinia-gdi id found..."
else
    curl -X GET "$url/$actinia_gdi_id"
    echo "curl -X GET \"$url/$actinia_gdi_id\""
fi


# check job status in actinia-core
if [ -z $actinia_core_id ]
then
    echo -e "\n no actinia-core id found... retrying"
    # this happens when using test endpoint, as no actinia-gdi id is created
    actinia_core_url=$(cat resp.json | json status)

    curl -u $actinia_core_auth -X GET \
      "$actinia_core_url"
    echo "curl -u $actinia_core_auth -X GET \
      \"$actinia_core_url\""
else
    curl -u $actinia_core_auth -X GET \
      "$actinia_core_baseUrl/api/v1/resources/actinia-gdi/$actinia_core_id"
    echo "curl -u $actinia_core_auth -X GET \
      \"$actinia_core_baseUrl/api/v1/resources/actinia-gdi/$actinia_core_id\""
fi


exit 0


##### Talk to actinia-core directly

url=$actinia_core_baseUrl/api/v1/locations/latlong/processing_async_export
json=../actinia_gdi/templates/actiniaCore/examples/pc_sleep.json

curl -X POST $url \
   -u $actinia_core_auth \
   -H 'accept: application/json' \
   -H 'Content-Type: application/json' \
   -d @${json} > \
   resp.json && cat resp.json

cat resp.json | json urls.status | xargs curl -L -u $actinia_core_auth -X GET
