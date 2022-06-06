_Containersec_
==============
Automated cloud-native AI container security monitoring and
intrusion/hacking/threat detection/response system.

**This software is strictly in a _proof-of-concept_ stage.**
It comes with no code quality assurances, and it has been tested only
on the provided _Dockerfile_ (see section _Usage_ below).

Welcome to play with it and report your findings!

Installation
------------
```shell
$ sudo apt install sysdig python3-pip

$ pip install -r requirements.txt
```

Usage
-----
Basic mode of operation:
```shell
# Run the observer daemon with an sysdig filter appropriate for your
# program/app and collect events into a training file.  While step 1 is
# executing, run your program/app's test suite or stress-test it with
# other valid (expected) traffic/payload/syscalls.
$ ./sysdig.sh "proc.apid in (SOME_PID, ...) or container.id in (SOME_ID, ...)" | tee train.tsv

# After collection, build a statistical model based on your training data.
$ ./train.py train.tsv model.pickle

# Re-run ./sysdig.sh with the same filter, but this time pipe its output
# through ./detect.py and provide the trained model file.  The latter script
# will print on stdout only events that are considered an anomaly (e.g. an attack),
# and the rest to stderr.
$ ./sysdig.sh ... | ./detect.py - model.pickle 2>/dev/null
```
That's it.

In general, and for arbitrary data sources (e.g. logs):
```shell
$ TSV_SOURCE | ./train.py - model.pickle
$ TSV_SOURCE | ./detect.py - model.pickle 2>/dev/null
```
Note, **first column is reserved for the _line source identifier_**
(PID, container id etc.) and is ignored in the model.
