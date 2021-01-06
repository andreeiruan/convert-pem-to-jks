import os
from time import sleep
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler, FileSystemEventHandler
from toJks import BotPemToJks


class FileChangeHandler(FileSystemEventHandler):

  def __init__(self, bot: BotPemToJks):
      super().__init__()
      self.bot = bot


  def loadFilesPem(self, number):
    listFiles = os.listdir(self.bot.tsPlusDir)
    listFilesPem = []      

    for file in listFiles:
      if f'{number}.pem' in file:      
        listFilesPem.append(file)

    return listFilesPem

  
  def getExtension(self, event):
    return event.src_path[event.src_path.rindex('.') + 1:].lower()
  
  def on_created(self, event):
    pass

  def on_modified(self, event):    
    extension = self.getExtension(event)    
    if extension == 'pem':    
      try:
        number = int(event.src_path[event.src_path.rindex('.pem') - 1 :event.src_path.rindex('.pem')])        
        listFilesPem = self.loadFilesPem(number)                         
        if f'cert{number}.pem' in listFilesPem and f'chain{number}.pem' in listFilesPem and f'fullchain{number}.pem' in listFilesPem and f'privkey{number}.pem' in listFilesPem:          
          self.bot.converter()    
      except ValueError:        
        pass
   
  def on_deleted(self, event):
      pass


  def on_moved(self, event):
      pass      
      

class ObserverTsPlusDir:

  def __init__(self, fileHandler: FileChangeHandler, tsPlusDir: str) -> None:
    self.tsPlusDir = tsPlusDir
    self.fileChangeHandler = fileHandler    
  
  def run(self) -> None:
    observer = Observer()            
    observer.schedule(self.fileChangeHandler, self.tsPlusDir, recursive=False)
    observer.start()

    try:
      while True:                
        sleep(1)
        
    except KeyboardInterrupt:
      observer.stop()

    observer.join()