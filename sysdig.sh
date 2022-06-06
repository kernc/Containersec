#!/bin/sh

set -eu
#set -x

str_strip() { sed -E 's/(^\s+|\s+$)//g'; }
strip_comments() { sed '/^#/d'; }
str_as_single_line() { echo "$@" | strip_comments | tr '\n' '\t' | str_strip; }

show_buffer_len=200
out_format="$(str_as_single_line '
*%proc.pid %container.id %container.image
%proc.name
%evt.dir%evt.type
%evt.res
%fd.name
%proc.cmdline
%evt.info
%syslog.severity.str
%syslog.message
')"

# Filter expressions can use one of these comparison operators: =, !=, <, <=, >, >=,
# `contains`, `icontains`, `in` and `exists`. Multiple checks can be combined through
# brackets and the following boolean operators: `and`, `or`, `not`.
# The list of available fields can be obtained with 'sysdig -l'.
filter="$(str_as_single_line "
( (evt.dir = > and
   evt.type in ( syscall, getrlimit, setrlimit, prlimit, socket, fcntl ) )
 or (evt.dir = < and
     evt.type in ( open, openat, creat, connect ) )
 or evt.type in ( bind, listen, getpeername, getcwd, chdir,
                  fchdir, mkdir, rmdir, signalfd, kill, tkill, tgkill, signaldeliver,
                  rename, renameat, symlink, symlinkat, procexit, quotactl,
                  setresuid, setresgid, setuid, setgid, clone, fork, vfork, execve,
                  mount, umount, chroot, container, notification, seccomp, link,
                  chmod, fchmod )
)
" | sed 's/[\t ]+/ /')"

[ "$*" ] && filter="$filter and ($*)"

sysdig \
    --print-ascii \
    --resolve-ports \
    --unbuffered \
    --print "$out_format" \
    --snaplen "$show_buffer_len" \
    "$filter" \
    | sed --unbuffered -e 's/<NA>//g'
