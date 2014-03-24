#!/usr/bin/python -tt
# Python Indentation: Google's 2 space

#Monitoring script for Linux - monitman.com
#Copyright (C) 2014 Etienne le Roux - leroux.etienne@drakepeak.net
#ToDo: Finish RAID checking, Add memory checking
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

# Code uses the Google two space indentation code style for python
import os
import platform
import time
import subprocess
import re
import sys
import socket
import time
import urllib2

#Configure the base URL the data should be sent to
url="https://monitman.com/update.php?"

#Array to store all results, used in sendResults()
results=[]

#Array to store and track all drive serial numbers
serials=[]

#Add any custom code into getCustom to feed it through...
def getCustom():
  print ""
  #Checking a host/port example:
  host = "google.com"
  port = 80
  portCheck(host, port)

#Check a host/port for connect time
def portCheck(host, port):
  elapsed = -1
  if host and port:
    start = time.time()
    try:
      s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      s.settimeout(10)
      s.connect((host,port))
      s.close()
      end = time.time()
      elapsed = end - start
    except:
      elapsed = -1
  elapsed = round(elapsed, 2)
  print "Seconds taken to connect to " + host + " on port " + str(port) + " (-1 = timeout/failure): " + str(elapsed) + "\n"
  results.extend(["Connect time to " + host + " on port " + str(port), str(elapsed)])

#Start of standard checks/balances :-)
def getLinuxMemory():
  if os.path.isfile("/proc/meminfo"):
    print "\n----- MEMORY ----"
    file = open("/proc/meminfo","r")
    for line in file.readlines():
      line_pieces = line.split()
      if line_pieces[0] == "MemTotal:":# Total usable physical memory
        print "Total Memory:", line_pieces[1], "KB"
        results.extend(["Total Memory", line_pieces[1]])
      elif line_pieces[0] == "MemFree:":# LowFree + HighFree
        print "Memory Free:", line_pieces[1], "KB"
        results.extend(["Free Memory", line_pieces[1]])
      elif line_pieces[0] == "Buffers:": # Raw disk blocks, mainly used in calculation accuracy in The NOC
        print "Memory Buffers:", line_pieces[1], "KB"
        results.extend(["Memory Buffers", line_pieces[1]])
      elif line_pieces[0] == "Cached:": # Total Page Cache = Cached + SwapCached
        print "Memory Cached:", line_pieces[1], "KB"
        results.extend(["Memory Cached", line_pieces[1]])
      elif line_pieces[0] == "SwapCached:":
        print "Swap Cached:", line_pieces[1], "KB"
        results.extend(["Swap Cached", line_pieces[1]])
      elif line_pieces[0] == "SwapTotal:":
        print "Swap Total:", line_pieces[1], "KB"
        results.extend(["Swap Total", line_pieces[1]])
      elif line_pieces[0] == "SwapFree:":
        print "Swap Free:", line_pieces[1], "KB"
        results.extend(["Swap Free", line_pieces[1]])
    file.close()
  else: 
    print "Could not find /proc/meminfo file... skipping memory check..."

def getLinuxLoad():
  if os.path.isfile("/proc/loadavg"):
    print "\n----- LOAD (CPU + IO Utilization) ----"
    file = open("/proc/loadavg","r")
    line = file.readline()
    line_pieces = line.split()
    #This part can also be gained through os.system.loadavg
    print "1 Minute Load:", line_pieces[0]
    print "5 Minute Load:", line_pieces[1]
    print "15 Minute Load:", line_pieces[2]
    process_pieces = line_pieces[3].split("/");
    print "Processes Actively Running:", process_pieces[0] #This script will count as 1 btw :-)
    print "Processes Total:", process_pieces[1]
    #Push vars to results array
    results.extend(["1 Minute Load",line_pieces[0],"5 Minute Load",line_pieces[1],"15 Minute Load",line_pieces[2],"Processes Running",process_pieces[0],"Processes Total",process_pieces[1]])
    file.close()
  else:
    print "Could not find /proc/loadavg file... skipping load average check..."


def getLinuxProcessUsageList():
  list = [0] * 9  
  file = open("/proc/stat","r")
  for line in file.readlines():
    line_pieces = line.split() 
    if line_pieces[0] == "cpu":
      #Below measured time taken in Jiffies...
      list[0] = int(line_pieces[1]) # User - Normal processes
      list[1] = int(line_pieces[2]) # Nice - Niced processes
      list[2] = int(line_pieces[3]) # System - Kernel mode processes
      list[3] = int(line_pieces[4]) # Idle
      list[4] = int(line_pieces[5]) # Waiting for I/O    
      list[5] = int(line_pieces[6]) # Hardware Interrupts
      list[6] = int(line_pieces[7]) # Software Interrupts
      list[7] = list[0] + list[1] + list[2] + list[3] # Total Usage = User + Nice + System + Idle
    elif line_pieces[0] == "ctxt":# Context switches
      list[8] += int(line_pieces[1]) # Context switch value
  file.close() # close the special file before next reading
  #print "List:",list
  return list


def getLinuxProcessorUsage():
  #/proc/stat - CPU line aggregrates CPUx lines, columns mean:
  if os.path.isfile("/proc/stat"):
    print "\n----- OVERALL PROCESSOR USAGE (2 second average with 10 samples) ----"
    list1 = getLinuxProcessUsageList()
    time.sleep(1) # wait a second between readings
    list2 = getLinuxProcessUsageList()
    list3 = [list2 - list1 for list2, list1 in zip(list2, list1)]
    perc = 100 * (list3[7] - list3[3]) / list3[7] # 7 - total usage, 3 - total idle
    print "CPU Usage %:",perc
    print "Normal processes:",list3[0]
    print "Niced processes:",list3[1]
    print "Kernel mode processes:",list3[2]
    print "Idle processes:",list3[3]
    print "Processes Waiting for IO:",list3[4]
    print "Hardware Interrupts:",list3[5]
    print "Software Interrupts:",list3[6]
    print "Context Switches:",list3[8]
    #Add to the array
    results.extend(["CPU Usage",perc,"Normal Processes",list3[0],"Niced Processes",list3[1]])
    results.extend(["Kernel Mode Processes:",list3[2],"Idle processes:",list3[3],"Processes Waiting for IO:",list3[4]])
    results.extend(["Hardware Interrupts:",list3[5],"Software Interrupts:",list3[6],"Context Switches:",list3[8]])
  else:
    print "Could not find /proc/stat file... skipping overall processor usage check..."

def getLinuxProcessorCores(sockets):
  total_cores = 0
  for a in range(0, sockets):
    current_socket = -1
    cores = 0
    print "Details for Socket Number:",(a+1)
    file = open("/proc/cpuinfo","r")
    for line in file.readlines():
      line_pieces = line.split(":")
      info = line_pieces[0].strip()
      if info == "physical id":
        current_socket = line_pieces[1].strip()
      elif info == "core id":
        if int(current_socket) == a:
          cores += 1
    if cores == 0:
      cores = 1
    total_cores += cores
    print "Core for Socket:",cores
    file.close();
  return total_cores 

def getLinuxProcessorDetails():
  if os.path.isfile("/proc/cpuinfo"):
    print "\n----- PROCESSORS ----"
    processors = 0
    sockets = 0
    file = open("/proc/cpuinfo","r")
    for line in file.readlines():
      line_pieces = line.split(":") 
      info = line_pieces[0].strip()
      if info == "processor" or info == "Processor":
        processors += 1
      elif info == "physical id":
        value = line_pieces[1].strip()
        if int(value) > sockets-1:
          sockets += 1
    print "Total Processors (Incl. Threaded):", processors
    results.extend(["Total Processors (Incl. Threaded)", processors]);
    if sockets == 0:
      sockets = 1 # For single processor systems without the physical id field
    print "Physical Sockets:", sockets
    total_cores = getLinuxProcessorCores(sockets)
    print "Total Cores for All Sockets:",total_cores
    threaded = processors - total_cores
    print "Total Threaded Processors:",threaded
    file.close()
  else:
    print "Could not find /proc/cpuinfo file... skipping processor check..."

def getLinuxUptime():
  if os.path.isfile("/proc/uptime"):
    print "\n---- UPTIME ----"
    file = open("/proc/uptime","r")
    uptime = file.readline().split()
    print "Uptime since boot (seconds):",uptime[0]
    results.extend(["Uptime", uptime[0]]);
    file.close()  
  else:
    print "Could not find /proc/cpuinfo file... skipping processor check..."

def cmd_exists(cmd):
    return subprocess.call("type " + cmd, shell=True, 
        stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0

def getIPMI():
  if cmd_exists("dmidecode"):
    p = os.popen("`which dmidecode` | grep -i ipmi | awk '{ print $1 }'","r")
    line = p.readline()
    if line:
      print "\n---- IPMI ----"
      if cmd_exists("ipmi-sensors"):
        print "May time a few seconds to fetch information..."
        i = os.popen("`which ipmi-sensors` --quiet-cache --comma-separated-output | grep -v 'N/A' | grep -v 'ID,Name'")
        while 1:
          line = i.readline()
          if line:
            line = line.replace("\n", "")
            line = line.split(',')
            print line[1] + ": " + line[3] + " " +line[4]
            results.extend([line[1], line[3]]);
          else:
            break
      else:
        print "Your system does have IPMI available"
        print "For more IPMI information, please install package providing command: impi-sensors"
        print "For Debian/Ubuntu try: apt-get install freeipmi-tools"
    else:
      #No IPMI so failover to LM sensors
      print "\n---- LM SENSORS ----"
      if cmd_exists("sensors"):
        print "May time a few seconds to fetch information..."
        cnt=0
        i = os.popen("`which sensors` -u | grep 'input' | sed 's/_input://g'")
        while 1:
          line = i.readline()
          if line:
            line = line.replace("\n", "")
            line = line.split(' ')
            print line[2] + ": " + line[3]
            results.extend([line[2], line[3]]);
            cnt+=1
          else:
             break
        if cnt <= 0:
          print "Note - you may need to run sensors-detect if this stage doesn't detect anything, try also running 'sensors' manually"
      else:
        print "For more sensor information, please install lm-sensors"
        print "For Debian/Ubuntu try: apt-get install lm-sensors"
    p.close()

def getSmartDetails(drive):
  if cmd_exists("smartctl"):
    se = os.popen("`which smartctl` --all "+drive+" | grep -i 'serial number' | awk '{ print $3 }'")
    se_line = se.readline()
    se_line = se_line.replace("\n", "")
    if se_line in serials:
      print "Drive already checked, more than one file may point to the same device"
    elif se_line:
      serials.append(se_line);
      s = os.popen("`which smartctl` --all "+drive+" | grep 0x00 | grep -")
      while 1:
        line = s.readline()
        if line:
          line = line.replace("\n", "")
          line = line.strip()
          line = re.sub(' +',' ',line)
          line = line.split(' ')
          if line[9] != "0":
            line[1] = line[1].replace("_"," ");
            print line[1]+" - "+line[9]
            results.extend([line[1]+" "+drive,line[9]]);
        else:
          break
      s.close()
      so = os.popen("`which smartctl` --all "+drive+" | grep -E 'SMART Health Status: OK|test result: PASSED'")
      so_line = so.readline()
      so_failed = "1"
      if so_line:
       so_failed = "0"
      print "SMART device result (0 - Passed, 1 - failure or undetected): " + so_failed + "\n"
      results.extend(["SMART result",so_failed]);
      so.close()
    else:
      print "Drive is not SMART enabled or does not support it..."
    se.close()     
  else:
    print "For more drive information, please install smartmontools"
    print "For Debian/Ubuntu try: apt-get install smartmontools\n"

def getRAID():
  print "\n---- RAID DEVICE STATS ----"
  #Checking for software RAID

  r = os.popen("/bin/ls /dev/sg*")
  while 1:
    line = r.readline()
    if line:
     line = line.replace("\n", "")
     line = line.strip()
     print "Checking for SMART on device:", line
     getSmartDetails(line)
    else:
      break
  r.close()
  

def getSmartMon():
  print "\n---- HARD DRIVE STATS ----"
  i = os.popen("/bin/cat /proc/partitions | awk '{ print $4 }' | grep -v name | grep -v '^$'")
  while 1:
    line = i.readline()
    if line:
      if "sr" not in line and "dm-" not in line and "loop" not in line:
        line = line.replace("\n", "")
        line = line.strip()
        #Determine disk/partition type
        if any(char.isdigit() for char in line):
          print "Found partition:", line
          #Fetch space of drive/partition
          d = os.popen("df | grep '/dev/"+line+" '")
          disk_line = d.readline()
          if disk_line:
            disk_line = disk_line.replace("\n", "")
            disk_line = re.sub(' +',' ',disk_line)
            disk_line = disk_line.split(' ')
            print "Size KB:", disk_line[1]
            print "Available KB:", disk_line[2]
            print "Used KB:", disk_line[3], "\n"
            results.extend(["Size /dev/"+line,disk_line[1],"Available /dev/"+line,disk_line[2],"Used /dev/"+line,disk_line[3]]);
          else:
            print "Not mounted\n"
        else:
          print "Found drive:", line
          line = "/dev/"+line
          getSmartDetails(line)
    else:
      break

def getSerials():
  #Serial tracking, add additional serial numbers
  if cmd_exists("dmidecode"):
    i = os.popen("`which dmidecode` | grep -i 'serial number'")
    while 1:
      line = i.readline()
      if line:
        line = line.replace("\n", "")
        line = re.sub(' +',' ',line)
        line = line.split(':')
        line[1] = line[1].strip()
        if line[1] and line[1] not in serials:
          serials.append(line[1]);
      else:
        break

def sendResults():
  print "Sending results..."
  print "URL: ", url
  print results

def sendSerials():
  print "Sending serials..."
  print "URL: ", url
  print serials

def getLinuxStats():
  print "Starting to gather stats for this machine..."
  getLinuxMemory()
  getLinuxLoad()
  getLinuxProcessorDetails()
  getLinuxProcessorUsage()
  getLinuxUptime()
  getIPMI()
  getSmartMon()
  getRAID()
  getSerials()
  getCustom()
  sendResults()
  sendSerials()

def main():
  system = platform.system()
  release = platform.release()

  if system == "Linux":
    #os.system('clear')
    print "Running for Linux with Kernel release", release
    getLinuxStats()
  else:
    print "Your OS is not yet supported... please e-mail support@drakepeak.net for more details or to request support..."


if __name__ == '__main__':
  main()


