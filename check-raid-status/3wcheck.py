# /usr/bin/python

import sys
import logging
import subprocess
import shlex

logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.DEBUG)


class Utils:
  @staticmethod
  def hardwareDetected():
    p1 = subprocess.Popen(shlex.split('lspci'),stdout=subprocess.PIPE)
    p2 = subprocess.Popen(shlex.split('grep -i 3ware'), stdin=p1.stdout,
                                                        stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    p1.stdout.close()
    out, err = p2.communicate()
    retcode = p2.returncode

    if retcode == 0:
      logging.debug('RAID hardware detected: ' + out)
      return True
    else:
      logging.error('Hardware detection error ' + err)
      return False

  @staticmethod
  def softwareDetected():
    p = subprocess.Popen(shlex.split('whereis tw-cli'), stdout=subprocess.PIPE)
    out, err = p.communicate()
    retcode = p.returncode
    path = out.split()[1]

    if path != '':
      # Sorry
      global twcli
      twcli = path
      logging.debug('RAID software detected: ' + path)
      return True
    else:
      logging.error('Software not detected ' + err + out)
      return False

  @staticmethod
  def removeHeaders(output):
    if isinstance(output, str):
      output = output.split('\n')

    for index, line in enumerate(output):
      if line[0:4] == '----':
        output.pop(index)
        output.pop(index-1)
    return output

  @staticmethod
  def parseCommand(param):
    cmdoutput = []
    p = subprocess.Popen(shlex.split(twcli + ' ' + param), stdout=subprocess.PIPE)
    logging.debug('Exec: twcli ' + param)
    out, err = p.communicate()
    retcode = p.returncode

    if retcode == 0:
      return out
    else:
      logging.error('ERROR: ' + err)

    return cmdoutput

class Raid:
  controllers = []

  #def __init__(self):
  #  self.controllers = getControllers()

  def getControllers(self):
    output = Utils.parseCommand('show')

    # Remove header and separator
    out = Utils.removeHeaders(output)
    #print out
    for line in out:
      if line is not '':
        cname = line.split()[0]
        if len(self.controllers) > 0:
          if getController(cname) is None:
            self.controllers.append(Raid.Controller(cname))
        else:
          self.controllers.append(Raid.Controller(cname))
    return self.controllers

    def getController(self, name):
      for c in self.controllers:
        if c.getName == name:
          return c

  class Controller:
    name = ''
    model = ''
    units = []

    def __init__(self, name):
      if self.name == '':
        self.name = name

    def getName(self):
      return self.name

    def getModel(self):
      if self.model == '':
        self.model = 'TODO'
      return self.model

    def getUnits(self):
      c = self
      output = Utils.parseCommand('/' + self.getName() + ' show')
      output = Utils.removeHeaders(output)
      # Get only Unit list
      for index,line in enumerate(output):
        if line is '':
          if len(output[:index]) > 0:
            output = output[:index]
      for line in output:
        if line is not '':
          uname = line.split()[0]
          if len(self.units) > 0:
            if getUnit(uname) is None:
              self.units.append(Raid.Controller.Unit(c, uname))
          else:
            self.units.append(Raid.Controller.Unit(c, uname))
      return self.units

    def getUnit(self, name):
      for u in self.units:
        if u.getName == name:
          return u

    class Unit:
      name = ''
      utype = ''
      status = ''
      size = 0
      ports = []
      controller = ''

      def __init__(self, c, uname):
        if self.name == '':
          self.name = uname
        if self.controller == '':
          self.controller = c.getName()

      def getName(self):
        return self.name

      def getPorts(self):
        c = Raid.Controller(self.controller)
        # FIX IT, c0 hardcoded :S
        output = Utils.parseCommand('/' + 'c0' + ' show')
        output = Utils.removeHeaders(output)
        for line in output:
          if len(line.split()) > 2 and line.split()[2] == self.getName():
            pname = line.split()[0]
            if self.getPort(pname) is None:
              self.ports.append(Raid.Controller.Unit.Port(c, pname))
        return self.ports

      def getPort(self, name):
        for p in self.ports:
          if p.getName == name:
            return p

      class Port:
        name = ''
        status = ''
        size = 0
        serial = ''
        unit = ''
        controller = ''

        def __init__(self, c, pname):
          if self.name == '':
            self.name = pname
          if self.controller == '':
            self.controller = c.getName()

        def getName(self):
          return self.name

        def getReallocatedSectors(self):
          rasect = None
          pname = self.name
          output = Utils.parseCommand('/' + self.controller + '/' + pname + ' show rasect')
          rasect = int(output.split('=')[1].strip())
          # rasect > 0   # WARNING
          # rasect > 10  # CRITICAL
          return rasect

        def getPowerOnHours(self):
          pohrs = 0
          pname = self.name
          output = Utils.parseCommand('/' + self.controller + '/' + pname + ' show pohrs')
          pohrs = int(output.split('=')[1].strip())
          return pohrs


twcli = None

def main():
  # Hardware detection
  if Utils.hardwareDetected():
    logging.debug('3ware hardware detected')
  else:
    logging.error('3ware hardare not detected')
    sys.exit()

  # Software detection
  if Utils.softwareDetected():
    logging.debug('3ware software detected')
  else:
    logging.error('3ware software not detected')
    sys.exit()

  # Raid controller detection
  r = Raid()
  controllers = r.getControllers()
  for c in controllers:
    logging.debug('Controller: ' + c.getName())
    units = c.getUnits()
    for u in units:
      logging.debug('Unit: ' + u.getName())
      ports = u.getPorts()
      for p in ports:
        pname = p.getName()
        rasect = p.getReallocatedSectors()
        pohrs = p.getPowerOnHours()
        logging.debug('Port %s: %i/%i' % (pname, rasect, pohrs))
        if rasect > 10:
          print 'CRITICAL Disk %s Reallocated Sectors: %i' % (pname, rasect)
        elif rasect > 0:
          print 'WARNING Disk %s Reallocated Sectors: %i' % (pname, rasect)

if __name__ == "__main__":
  main()
