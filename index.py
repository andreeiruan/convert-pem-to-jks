import os
from toJks import BotPemToJks
from Observer import FileChangeHandler, ObserverTsPlusDir

# tsPlusDir = r'C:\Users\andre\Desktop\ssl-converter\pem'
# tsPlusDir = r'C:\Program Files (x86)\TSplus\Clients\webserver'

tsPlusDir = 'C:\\Users\\andre\\Desktop\\ssl-converter\\pem'


bot = BotPemToJks(tsPlusDir)

if os.path.exists(tsPlusDir):
  fileChangeHandler = FileChangeHandler(bot)
  observerTsPlusDir  = ObserverTsPlusDir(fileChangeHandler, tsPlusDir)

  observerTsPlusDir.run()
else:
  bot.createLog('ts plus directory not found')  