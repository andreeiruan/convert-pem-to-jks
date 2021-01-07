import sys
import os
from chilkat import chilkat
import datetime
import json

class BotPemToJks:

  def __init__(self, tsPlusDir):
    self.tsPlusDir = tsPlusDir      

  def loadJsonLogs(self, dateLog):
    if not os.path.exists('./logs'):
      os.mkdir('./logs')
    try:
      with open(f'./logs/{dateLog}.json', 'r', encoding='utf-8') as jsonFile:
        logs = json.load(jsonFile)
      jsonFile.close()
      return logs    
    except FileNotFoundError:
      return False

  def createLog(self, message, typeLog = 'error'):
    dateLog = str(datetime.datetime.now()).replace(' ', '_').replace(':', '_')[0:10]
    timeLog = str(datetime.datetime.now())[11:19]
    log = { 'typeLog': typeLog, 'message': message, 'time': timeLog }  
    
    jsonLogs = self.loadJsonLogs(dateLog)
    if not jsonLogs:
      jsonLogs = []
    jsonLogs.append(log)

    with open(f'./logs/{dateLog}.json', 'w', encoding='utf-8') as fileLog:
      json.dump(jsonLogs, fileLog, indent=4, ensure_ascii=False)
    fileLog.close()

  def unlockChilkat(self):
    glob = chilkat.CkGlobal()
    success = glob.UnlockBundle('NFCAPB.CBX122020_whLMmkri37j2')
    if success != True:
        self.createLog(glob.lastErrorText())
        sys.exit()

    status = glob.get_UnlockStatus()  
    if status == 2:
        self.createLog('Unlocked using purchased unlock code', 'info')

  def loadContentPem(self, name):
    try:
      with open(f'{self.tsPlusDir}/{name}.pem', 'r') as file:
        pemContent = file.read()      
    except FileNotFoundError:
      self.createLog(f'pem file name {name} not found')      
    else:
      return pemContent
  
  def loadLastNumberFilesPem(self):
    listFiles = os.listdir(self.tsPlusDir)
    listFilesPem = []  
    biggerNumber = 0

    for file in listFiles:
      if '.pem' in file:      
        listFilesPem.append(file)

    for file in listFilesPem:
      if int(file[-5]) > biggerNumber:
        biggerNumber = int(file[-5])
    if biggerNumber == 0:
      return 0
    return biggerNumber

  def pemToJks(self, lastNumberFilesPem: int) -> bool:
    pem = chilkat.CkPem()
    password = ''

    success = pem.LoadPemFile(f'{self.tsPlusDir}/cert{lastNumberFilesPem}.pem', password)
    if success != True:     
      self.createLog(pem.lastErrorText())
      return False     

    success = pem.LoadPemFile(f'{self.tsPlusDir}/chain{lastNumberFilesPem}.pem', password)
    if success != True:     
      self.createLog(pem.lastErrorText())
      return False

    success = pem.LoadPemFile(f'{self.tsPlusDir}/fullchain{lastNumberFilesPem}.pem', password)
    if success != True:     
      self.createLog(pem.lastErrorText())
      return False     

    success = pem.LoadPemFile(f'{self.tsPlusDir}/privkey{lastNumberFilesPem}.pem', password)
    if success != True:     
      self.createLog(pem.lastErrorText())  
      return False    

    pemContent = ''
    pemContent += self.loadContentPem(f'cert{lastNumberFilesPem}') 
    pemContent += self.loadContentPem(f'chain{lastNumberFilesPem}') 
    pemContent += self.loadContentPem(f'fullchain{lastNumberFilesPem}') 
    pemContent += self.loadContentPem(f'privkey{lastNumberFilesPem}')

    success = pem.LoadPem(pemContent, password)
    if not success:
      self.createLog('error on load pem file')
      return False
    
    alias = ''

    jksPassword = 'secret'
    jks = pem.ToJks(alias, jksPassword)
    if pem.get_LastMethodSuccess() == False:    
      self.createLog(pem.lastErrorText())      
      return False

    if os.path.exists(f'{self.tsPlusDir}/cert.jks'):    
      datetimeRename = str(datetime.datetime.now()).replace(' ', '_').replace('-', '_').replace(':', '_')[0:19]
      if not os.path.exists(f'{self.tsPlusDir}/cert_{datetimeRename}.jks.bak'):
        os.rename(f'{self.tsPlusDir}/cert.jks', f'{self.tsPlusDir}/cert_{datetimeRename}.jks.bak')

    success = jks.ToFile(jksPassword,f'{self.tsPlusDir}/cert.jks')
    if success != True:
      self.createLog(jks.lastErrorText())
      return False

    if success == True:
      self.deleteFilesPem(f'cert{lastNumberFilesPem}') 
      self.deleteFilesPem(f'chain{lastNumberFilesPem}') 
      self.deleteFilesPem(f'fullchain{lastNumberFilesPem}') 
      self.deleteFilesPem(f'privkey{lastNumberFilesPem}')
      return True

  def deleteFilesPem(self, name):
    if os.path.exists(f'{self.tsPlusDir}/{name}.pem'):
      os.remove(f'{self.tsPlusDir}/{name}.pem')

  def loadCertNumberJson(self):
    try:
      with open('certNumber.json', 'r', encoding='utf-8') as jsonFile:
        certNumber = json.load(jsonFile)
      jsonFile.close()
      return certNumber['lastNumberCert']    
    except FileNotFoundError:
      return 0

  def updateCertNumber(self, number):
    with open('certNumber.json', 'w', encoding='utf-8') as fileLog:
      json.dump({ 'lastNumberCert': number}, fileLog, indent=4, ensure_ascii=False)
    fileLog.close()

  def converter(self):
    try:      
      biggerNumber = self.loadLastNumberFilesPem()      
      if biggerNumber != 0:        
        self.unlockChilkat()
        success = self.pemToJks(biggerNumber)

        if success == False:
          self.createLog('Error unexpected')

        if success == True:          
          os.system('taskkill /f /im HTML5service.exe')      
          os.system('cd C:\\Program Files (x86)\\TSplus\\Clients\\webserver & runwebserver.bat')      
    except:
      self.createLog('Error unexpected')
    else:
      self.createLog('Certificate successfully converted', 'info')


if __name__ == '__main__':
  prod = True
  if prod == True:
    tsPlusDir = r'C:\Program Files (x86)\TSplus\Clients\webserver'
  else: 
    tsPlusDir = 'C:\\Users\\andre\\Desktop\\ssl-converter\\pem'

  bot = BotPemToJks(tsPlusDir)
  if os.path.exists(tsPlusDir):
    bot.converter()
  else:
    bot.createLog('Directory ts plus not found')