#!/bin/bash
chmod a-x */*.emProject
chmod a-x */*.emSession
chmod a-x */*.c
chmod a-x */*.h
chmod a-x */*.txt
chmod a-x */*.xml
chmod a-x */config/*.h
git rm -r --cached *.emSession
