"""
This Python 3 script reads the /etc/fstab file line by line
and writes a new file /tmp/fstab line by line.
If a line contains the string '/dev/xvdp', it replaces that
line with:
/dev/xvdp /data ext4 defaults,nofail,nobootwait 0 2
It then:
- moves /etc/fstab to /etc/old_fstab
- moves /tmp/fstab to /etc/fstab
"""

import shutil

with open('/tmp/fstab', 'a') as tmp_fstab:
    with open('/etc/fstab') as f:
        for line in f:
            if '/dev/xvdp' in line:
                tmp_fstab.write('/dev/xvdp /data ext4 defaults,nofail,nobootwait 0 2\n')
            else:
                tmp_fstab.write(line)

shutil.move('/etc/fstab', '/etc/old_fstab')
shutil.move('/tmp/fstab', '/etc/fstab')
