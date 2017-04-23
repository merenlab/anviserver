#!/usr/bin/env python

import hashlib
import shutil
import glob
import anvio
import os
import re

parameter_name = "?hash="

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

html_files = []
html_files += glob.glob(os.path.join(os.path.dirname(anvio.__file__), "data/interactive/*.html"))

pattern = re.compile(".*(<script|<link).*(href|src)\=[\'\"]((?!http\:\/\/).+?)\".*")

for html_file in html_files:
    backup_file = os.path.join(os.path.dirname(html_file), "_" + os.path.basename(html_file))

    with open(html_file, "r") as f_input:
        with open(backup_file, "w") as f_output:
            for line in f_input.readlines():
                result = pattern.match(line)
                if result:
                    src = os.path.join(os.path.dirname(html_file), result.group(3))

                    if parameter_name in src:
                        src = src.split(parameter_name)[0]

                    checksum = md5(src)

                    pos = line.find(parameter_name)
                    if pos == -1:
                        line = line[:result.end(3)] + parameter_name + checksum + line[result.end(3):]
                    else:
                        line = line[:pos+len(parameter_name)] + checksum + line[pos+len(checksum)+len(parameter_name):]

                f_output.write(line)

    shutil.move(backup_file, html_file)
