from time import sleep
from chilkat import chilkat
from datetime import datetime
import sys
import os
import json


class Logger:
  def __init__(self):
      self.path = 'c:\\toJks\\logs'
      self.pathCertNumber = 'c:\\toJks\\certNumber.json'
  
  def loadJsonLogs(self, dateLog):
    if not os.path.exists(self.path):      
      os.mkdir(self.path)
    try:
      with open(f'{self.path}/{dateLog}.json', 'r', encoding='utf-8') as jsonFile:
        logs = json.load(jsonFile)
      jsonFile.close()
      return logs    
    except FileNotFoundError:
      return False
    
  def createLog(self, message, typeLog = 'error'):
    dateLog = str(datetime.now()).replace(' ', '_').replace(':', '_')[0:10]
    timeLog = str(datetime.now())[11:19]
    log = { 'typeLog': typeLog, 'message': message, 'time': timeLog }  
    
    jsonLogs = self.loadJsonLogs(dateLog)
    if not jsonLogs:
      jsonLogs = []
    jsonLogs.append(log)

    with open(f'{self.path}/{dateLog}.json', 'w', encoding='utf-8') as fileLog:
      json.dump(jsonLogs, fileLog, indent=4, ensure_ascii=False)
    fileLog.close()
  
  def loadCertNumberJson(self):
    try:
      with open(self.pathCertNumber, 'r', encoding='utf-8') as jsonFile:
        certNumber = json.load(jsonFile)
      jsonFile.close()
      return certNumber['lastNumberCert']    
    except FileNotFoundError:
      return 0

  def updateCertNumber(self, number):
    with open(self.pathCertNumber, 'w', encoding='utf-8') as fileLog:
      json.dump({ 'lastNumberCert': number}, fileLog, indent=4, ensure_ascii=False)
    fileLog.close()


class PemToJks:

  def __init__(self, logger: Logger):

    self.logger = logger

  def unlockChilkat(self):
    glob = chilkat.CkGlobal()
    success = glob.UnlockBundle('NFCAPB.CBX122020_whLMmkri37j2')
    if success != True:
        self.logger.createLog(glob.lastErrorText())
        sys.exit()

    status = glob.get_UnlockStatus()  
    if status == 2:
        self.logger.createLog('Unlocked using purchased unlock code', 'info')

  def loadContentPem(self, certBotDir, name,):
    try:
      with open(f'{certBotDir}/{name}.pem', 'r') as file:
        pemContent = file.read()      
    except FileNotFoundError:
      self.logger.createLog(f'pem file name {name} not found')      
    else:
      return pemContent
  
  def loadLastNumberFilesPem(self, certBotDir):
    listFiles = os.listdir(certBotDir)
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

  def converter(self, lastNumberFilesPem: int, certBotDir, tsPlusDir) -> bool:
    pem = chilkat.CkPem()
    password = ''

    success = pem.LoadPemFile(f'{certBotDir}/cert{lastNumberFilesPem}.pem', password)
    if success != True:     
      self.logger.createLog(pem.lastErrorText())
      sys.exit()      

    success = pem.LoadPemFile(f'{certBotDir}/chain{lastNumberFilesPem}.pem', password)
    if success != True:     
      self.logger.createLog(pem.lastErrorText())
      sys.exit()

    success = pem.LoadPemFile(f'{certBotDir}/fullchain{lastNumberFilesPem}.pem', password)
    if success != True:     
      self.logger.createLog(pem.lastErrorText())
      sys.exit()     

    success = pem.LoadPemFile(f'{certBotDir}/privkey{lastNumberFilesPem}.pem', password)
    if success != True:     
      self.logger.createLog(pem.lastErrorText())  
      sys.exit()    

    pemContent = ''
    pemContent += self.loadContentPem(certBotDir, f'cert{lastNumberFilesPem}') 
    pemContent += self.loadContentPem(certBotDir, f'chain{lastNumberFilesPem}') 
    pemContent += self.loadContentPem(certBotDir ,f'fullchain{lastNumberFilesPem}') 
    pemContent += self.loadContentPem(certBotDir, f'privkey{lastNumberFilesPem}')

    success = pem.LoadPem(pemContent, password)
    if not success:
      self.logger.createLog('error on load pem file')
      return False
    
    alias = ''

    jksPassword = 'secret'
    jks = pem.ToJks(alias, jksPassword)
    if pem.get_LastMethodSuccess() == False:    
      self.logger.createLog(pem.lastErrorText())      
      sys.exit()

    if os.path.exists(f'{tsPlusDir}/cert.jks'):    
      datetimeRename = str(datetime.now()).replace(' ', '_').replace('-', '_').replace(':', '_')[0:19]
      if not os.path.exists(f'{tsPlusDir}/cert_{datetimeRename}.jks.bak'):
        os.rename(f'{tsPlusDir}/cert.jks', f'{tsPlusDir}/cert_{datetimeRename}.jks.bak')

    success = jks.ToFile(jksPassword,f'{tsPlusDir}/cert.jks')
    if success != True:
      self.logger.createLog(jks.lastErrorText())
      sys.exit()
 
    return success


class Main:

  def __init__(self, pemtoJks: PemToJks, logger: Logger):
    self.pemtoJks = pemtoJks
    self.logger = logger
  
  def getPasteServer(self, certBotDir: str) -> str:
    if not os.path.exists(certBotDir):  
      return 'no\\found\\paste\\server'

    pastes = os.listdir(certBotDir)
    for paste in pastes:
      if 'corpnuvem' in paste:
        return paste

    return 'no\\found\\paste\\server'

  def getDaysAgoMotification(self, path: str) -> int:
    dateModification = os.path.getmtime(path)
    dateModification = datetime.fromtimestamp(dateModification)
    now = datetime.now()
    delta = now - dateModification
    return delta.days 
      
  def main(self, certBotDir, tsPlusDir):
    try:
      if os.path.exists(tsPlusDir) and os.path.exists(certBotDir):
        certBotDir += f'\\{self.getPasteServer(certBotDir)}'
        daysAgoModificationCert = self.getDaysAgoMotification(f'{tsPlusDir}\\cert.jks')           
        if daysAgoModificationCert > 86:
          os.system(r'cd c:\Program Files (X86)\bin')
          os.system('certbot renew')
          sleep(1)
        
        biggerNumber = self.pemtoJks.loadLastNumberFilesPem(certBotDir)
        lastCertNumber = self.logger.loadCertNumberJson()   
        if biggerNumber > lastCertNumber:        
          self.pemtoJks.unlockChilkat()
          success = self.pemtoJks.converter(biggerNumber, certBotDir, tsPlusDir)

          if success != True:
            self.logger.createLog(f'Error unexpected on convert files pem to jks {sys.exc_info()[0]}')            

          if success == True:  
            self.logger.updateCertNumber(biggerNumber)        
            self.logger.createLog('Certificate successfully converted', 'info')    
            os.system('taskkill /f /im HTML5service.exe')     
            os.system('cd C:\\Program Files (x86)\\TSplus\\Clients\\webserver & start /b runwebserver.bat')    
      else:
        self.logger.createLog(f'Directory ts plus ({tsPlusDir}) not found or directory certbot ({certBotDir}) not found')
    except Exception:
      self.logger.createLog(f'Error unexpected {Exception}')   


if __name__ == '__main__':
  prod = True
  if prod == True:
    tsPlusDir = r'C:\Program Files (x86)\TSplus\Clients\webserver'
    certBotDir = r'C:\Certbot\archive'
  else: 
    tsPlusDir = 'C:\\Users\\andre\\Desktop\\ssl-converter\\tsplus'
    certBotDir = 'C:\\Users\\andre\\Desktop\\ssl-converter\\certBot'

  logger = Logger()
  pemToJks = PemToJks(logger)
  main = Main(pemToJks, logger)
  main.main(certBotDir, tsPlusDir)
