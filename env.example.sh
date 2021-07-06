# this file contains the environment variables used to execute
# the gis function application locally

export ENV=local
export LOCAL=true

export HOST=localhost
export PORT=3000

# GEMFURY_TOKEN is used to configure the pip to retrieve 
# python package from gemfury's index
export GEMFURY_TOKEN="__EMPTY__"

# GCP_CREDENTIALS holds the service account token that allows
# to use the services hosted by GCP
export GCP_PROJECT="__EMPTY__"
export GCP_CREDENTIALS_B64="__EMPTY__"
