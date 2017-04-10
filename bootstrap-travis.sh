#!/bin/sh
# script used by travis


# see https://community.plone.org/t/not-using-bootstrap-py-as-default/620
`./bootstrap-"$PLONE_VERSION".x.sh`
./bootstrap-base.sh
