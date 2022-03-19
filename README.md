_Containersec_
==============
Automated cloud-native AI container security and intrusion/hacking/threat detection system.

Installation
------------
```shell
$ pip install -r requirements.txt
```

Usage
-----
```shell
$ ./sysdig.sh "proc.apid=SOME_PID or container.id=SOME_ID ..." | tee train.tsv

$ ./train.py train.tsv model.pickle

$ ./sysdig.sh ... | ./detect.py - model.pickle 2>/dev/null
```
For _arbitrary_ data sources (e.g. logs):
```shell
$ TSV_STREAM | ./train.py - model.pickle
$ TSV_STREAM | ./detect.py - model.pickle 2>/dev/null
```
Note, first column is reserved for the line identifier (PID, container id etc.)
and is dropped from the model.
