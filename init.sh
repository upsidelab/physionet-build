#!/bin/sh

createdb -U physionet physionet_dev -O physionet
createdb -U physionet physionet_test -O physionet
