import json
import time
from MCP3008 import MCP3008

class MQ():
    #mq2---------
    MQ2_PIN   = 0
    #mq135-------
    MQ135_PIN = 1
    #mq4---------
    MQ4_PIN   = 2
    
    RL_VALUE_MQ2 = 5
    RL_VALUE_MQ4 = 20
    RL_VALUE_MQ135 = 20
    
    def __init__(self):
        self.adc = MCP3008()  # Initialize adc as an instance variable
        self.Ro = self.mq_calibrations()  # Perform calibration in the constructor
        
    def MQResistanceCalculation(self, raw_adc, RL_VALUE):
        if raw_adc == 0:
            return float(1)
        else:
            return float(RL_VALUE*(2048.0-raw_adc)/float(raw_adc))

    def mq_calibrations(self):
        #mq2---------
        RO_CLEAN_AIR_FACTOR_MQ2   = 9.83
        #mq135-------
        RO_CLEAN_AIR_FACTOR_MQ135 = 3.6
        #mq4---------
        RO_CLEAN_AIR_FACTOR_MQ4   = 4.45
        
        #constant value
        CALIBRATION_SAMPLE_TIMES     = 50  # Corrected typo
        CALIBRATION_SAMPLE_INTERVAL  = 500
        
        val = {
            "mq2": 0.0,
            "mq4": 0.0,
            "mq135": 0.0
        }
        
        for i in range(CALIBRATION_SAMPLE_TIMES):          # take multiple samples
            val["mq2"] += self.MQResistanceCalculation(self.adc.read(self.MQ2_PIN), self.RL_VALUE_MQ2)
            val["mq4"] += self.MQResistanceCalculation(self.adc.read(self.MQ4_PIN), self.RL_VALUE_MQ4)
            val["mq135"] += self.MQResistanceCalculation(self.adc.read(self.MQ135_PIN), self.RL_VALUE_MQ135)
            time.sleep(CALIBRATION_SAMPLE_INTERVAL/1000.0)
        
        val["mq2"] = (val["mq2"]/CALIBRATION_SAMPLE_TIMES)/ RO_CLEAN_AIR_FACTOR_MQ2
        val["mq4"] = (val["mq4"]/CALIBRATION_SAMPLE_TIMES)/ RO_CLEAN_AIR_FACTOR_MQ4
        val["mq135"] = (val["mq135"]/CALIBRATION_SAMPLE_TIMES)/ RO_CLEAN_AIR_FACTOR_MQ135
        
        return val

    def read_mq(self):
        # Read constants
        READ_SAMPLE_INTERVAL         = 50
        READ_SAMPLE_TIMES            = 5
        
        def mq_read():
            rs = {
                "mq2": 0.0,
                "mq4": 0.0,
                "mq135": 0.0
            }

            for i in range(READ_SAMPLE_TIMES):          # take multiple samples
                rs["mq2"] += self.MQResistanceCalculation(self.adc.read(self.MQ2_PIN), self.RL_VALUE_MQ2)
                rs["mq4"] += self.MQResistanceCalculation(self.adc.read(self.MQ4_PIN), self.RL_VALUE_MQ4)
                rs["mq135"] += self.MQResistanceCalculation(self.adc.read(self.MQ135_PIN), self.RL_VALUE_MQ135)
                time.sleep(READ_SAMPLE_INTERVAL/1000.0)

            rs["mq2"] = rs["mq2"]/READ_SAMPLE_TIMES
            rs["mq4"] = rs["mq4"]/READ_SAMPLE_TIMES
            rs["mq135"] = rs["mq135"]/READ_SAMPLE_TIMES
            
            return rs
        
        rs = mq_read()
        
        #put value to dictionary
        mq_sensor = {
            "ro": self.Ro,
            "rs": rs
        }

        #dumps by json to return value
        return mq_sensor