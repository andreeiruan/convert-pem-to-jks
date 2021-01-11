import sys
import os
from chilkat import chilkat
import datetime
import json


class BotPemToJks:

  def __init__(self, tsPlusDir, certBotDir):
    self.tsPlusDir = tsPlusDir
    self.certBotDir = certBotDir    

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
      with open(f'{self.certBotDir}/{name}.pem', 'r') as file:
        pemContent = file.read()      
    except FileNotFoundError:
      self.createLog(f'pem file name {name} not found')      
    else:
      return pemContent
  
  def loadLastNumberFilesPem(self):
    listFiles = os.listdir(self.certBotDir)
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

    success = pem.LoadPemFile(f'{self.certBotDir}/cert{lastNumberFilesPem}.pem', password)
    if success != True:     
      self.createLog(pem.lastErrorText())
      sys.exit()      

    success = pem.LoadPemFile(f'{self.certBotDir}/chain{lastNumberFilesPem}.pem', password)
    if success != True:     
      self.createLog(pem.lastErrorText())
      sys.exit()

    success = pem.LoadPemFile(f'{self.certBotDir}/fullchain{lastNumberFilesPem}.pem', password)
    if success != True:     
      self.createLog(pem.lastErrorText())
      sys.exit()     

    success = pem.LoadPemFile(f'{self.certBotDir}/privkey{lastNumberFilesPem}.pem', password)
    if success != True:     
      self.createLog(pem.lastErrorText())  
      sys.exit()    

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
      sys.exit()

    if os.path.exists(f'{self.tsPlusDir}/cert.jks'):    
      datetimeRename = str(datetime.datetime.now()).replace(' ', '_').replace('-', '_').replace(':', '_')[0:19]
      if not os.path.exists(f'{self.tsPlusDir}/cert_{datetimeRename}.jks.bak'):
        os.rename(f'{self.tsPlusDir}/cert.jks', f'{self.tsPlusDir}/cert_{datetimeRename}.jks.bak')

    success = jks.ToFile(jksPassword,f'{self.tsPlusDir}/cert.jks')
    if success != True:
      self.createLog(jks.lastErrorText())
      sys.exit()
 
    return success

  def deleteFilesPem(self, name):
    if os.path.exists(f'{self.tsPlusDir}/{name}.pem'):
      os.remove(f'{self.tsPlusDir}/{name}.pem')

  def loadCertNumberJson(self):
    try:
      with open('./certNumber.json', 'r', encoding='utf-8') as jsonFile:
        certNumber = json.load(jsonFile)
      jsonFile.close()
      return certNumber['lastNumberCert']    
    except FileNotFoundError:
      return 0

  def updateCertNumber(self, number):
    with open('./certNumber.json', 'w', encoding='utf-8') as fileLog:
      json.dump({ 'lastNumberCert': number}, fileLog, indent=4, ensure_ascii=False)
    fileLog.close()

  def converter(self):
    try:      
      biggerNumber = self.loadLastNumberFilesPem()  
      lastCertNumber = self.loadCertNumberJson()   
      if biggerNumber > lastCertNumber:        
        self.unlockChilkat()
        success = self.pemToJks(biggerNumber)

        if success != True:
          self.createLog(f'Error unexpected on convert files pem to jks {sys.exc_info()[0]}')       
        

        if success == True:  
          self.updateCertNumber(biggerNumber)        
          self.createLog('Certificate successfully converted', 'info')
          os.system('background.vbs')            

    except Exception:
      self.createLog(f'Error unexpected {Exception.args}')   


def getPasteServer(certBotDir: str) -> str:
  if not os.path.exists(certBotDir):  
    return 'no\\found\\paste\\server'

  pastes = os.listdir(certBotDir)
  for paste in pastes:
    if 'corpnuvem' in paste:
      return paste

  return 'no\\found\\paste\\server'


if __name__ == '__main__':
  prod = True
  if prod == True:
    tsPlusDir = r'C:\Program Files (x86)\TSplus\Clients\webserver'
    certBotDir = r'C:\Certbot\archive'
    certBotDir += f'\\{getPasteServer(certBotDir)}'
  else: 
    tsPlusDir = 'C:\\Users\\andre\\Desktop\\ssl-converter\\tsplus'
    certBotDir = 'C:\\Users\\andre\\Desktop\\ssl-converter\\certBot'
    certBotDir += f'\\{getPasteServer(certBotDir)}' 

  bot = BotPemToJks(tsPlusDir, certBotDir)
  if os.path.exists(tsPlusDir) and os.path.exists(certBotDir):
    bot.converter()
  else:
    bot.createLog(f'Directory ts plus ({tsPlusDir}) or cert bot {(certBotDir)} not found')
