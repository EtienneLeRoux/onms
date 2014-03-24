#!/usr/bin/python -tt

# Description: Checks TCP ports and returns time taken to connect, note that UDP port checking isn't viable due to the connectionless nature of UDP
# Output: Returns the seconds taken in floating point format, this can be captured by another script and fed into monitman.com
# Initial Release: 2012
# Python Identation: Google's 2 space

#Copyright (C) 2014 Etienne le Roux - monitman.com
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import sys
import socket
import time
import urllib2

if len(sys.argv) != 5:
 print "Usage: ./port_check.py update_id key hostname port"
 sys.exit(1)

update_id = sys.argv[1]
key = sys.argv[2]
host = sys.argv[3]
port = int(sys.argv[4])

start = time.time()

try:
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.settimeout(10)
  s.connect((host,port))
  s.close()
  end = time.time()
  elapsed = end - start
except:
  elapsed = 0

print "Time taken to connect (0 - timeout): %s" % elapsed

url="https://monitman.com/update.php?update_id=%s&key=%s&value=%s" % (update_id, key, elapsed)
req = urllib2.Request(url)
try:
  urllib2.urlopen(req)
  print "Delivered key/value pair to server"
except:
  print "Could not deliver key/value pair to server"









