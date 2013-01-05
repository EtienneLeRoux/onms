#!/usr/bin/python -tt
# Python Indentation: Google's 2 space

# Author: Etienne le Roux (etienne@linux.com) for ONMS.Net
# Address: PoBox 634, Menlyn Retail Park, Pretoria, South Africa, 0063

#
#    Copyright (C) 2012 Etienne le Roux
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Code Identation - ONMS uses the Google two space indentation code style for python
import os
import platform
import time

def getLinuxMemory():
  print ""
  if os.path.isfile("/proc/meminfo"):
    print "----- MEMORY ----"
    file = open("/proc/meminfo","r")
    for line in file.readlines():
      line_pieces = line.split()
      if line_pieces[0] == "MemTotal:":# Total usable physical memory
        print "Total Memory:", line_pieces[1], "KB"
      elif line_pieces[0] == "MemFree:":# LowFree + HighFree
        print "Memory Free:", line_pieces[1], "KB"
      elif line_pieces[0] == "Buffers:": # Raw disk blocks, mainly used in calculation accuracy in The NOC
        print "Memory Buffers:", line_pieces[1], "KB"
      elif line_pieces[0] == "Cached:": # Total Page Cache = Cached + SwapCached
        print "Memory Cached:", line_pieces[1], "KB"
      elif line_pieces[0] == "SwapCached:":
        print "Swap Cached:", line_pieces[1], "KB"
      elif line_pieces[0] == "SwapTotal:":
        print "Swap Total:", line_pieces[1], "KB"
      elif line_pieces[0] == "SwapFree:":
        print "Swap Free:", line_pieces[1], "KB"
    file.close()
  else: 
    print "Could not find /proc/meminfo file... skipping memory check..."

def getLinuxLoad():
  print ""
  if os.path.isfile("/proc/loadavg"):
    print "----- LOAD (CPU + IO Utilization) ----"
    file = open("/proc/loadavg","r")
    line = file.readline()
    line_pieces = line.split()
    #This part can also be gained through os.system.loadavg
    print "1 Minute Load:", line_pieces[0]
    print "5 Minute Load:", line_pieces[1]
    print "15 Minute Load:", line_pieces[2]
    process_pieces = line_pieces[3].split("/");
    print "Processes Actively Running:", process_pieces[0] #This script will count as 1 btw
    print "Processes Total:", process_pieces[1]
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
    print "Kernel mode:",list3[2]
    print "Idle:",list3[3]
    print "Waiting for IO:",list3[4]
    print "Hardware Interrupts:",list3[5]
    print "Software Interrupts:",list3[6]
    print "Context Switches:",list3[8]
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
  print ""
  if os.path.isfile("/proc/cpuinfo"):
    print "----- PROCESSORS ----"
    processors = 0
    sockets = 0
    file = open("/proc/cpuinfo","r")
    for line in file.readlines():
      line_pieces = line.split(":") 
      info = line_pieces[0].strip()
      if info == "processor":
        processors += 1
      elif info == "physical id":
        value = line_pieces[1].strip()
        if int(value) > sockets-1:
          sockets += 1
    print "Total Processors (Incl. Threaded):", processors
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
  print ""
  if os.path.isfile("/proc/uptime"):
    print "---- UPTIME ----"
    file = open("/proc/uptime","r")
    uptime = file.readline().split()
    print "Uptime since boot (seconds):",uptime[0]
    file.close()  
  else:
    print "Could not find /proc/cpuinfo file... skipping processor check..."


def getLinuxStats():
  print "Starting to gather stats for this machine..."
  getLinuxMemory()
  getLinuxLoad()
  getLinuxProcessorDetails()
  getLinuxProcessorUsage()
  getLinuxUptime()

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

