from pyspark.sql import *
from pyspark.sql.functions import *

class VantageCareSettings:
  def __init__(self, mountedJsonFileLocation):
    self.mountedFileLocation = mountedJsonFileLocation
    
  ###################################################### 
  # Get VC app setting by name, returns None if setting does not exist
  ###################################################### 
  def getSetting(self, nameOfSetting):
    # DISCLAIMER: Spark 2.3+ considers each newline character to be another json file. Make sure your json file is saved as a minified file before reading it by spark or use the option: multiline to parse the full json file
    # read json file into dataframe
    eventConfigJsonDf = spark.read.option("multiline","true").json(self.mountedFileLocation)
    dfSetting = None

    # this will only work if we have a schema that is NOT nested
    if nameOfSetting.upper() in (name.upper() for name in eventConfigJsonDf.columns):
      dfSetting = eventConfigJsonDf.select(first(nameOfSetting))
      return dfSetting.collect()[0][0]
    return None
   