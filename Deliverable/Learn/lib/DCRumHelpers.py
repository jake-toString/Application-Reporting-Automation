#!/usr/bin/python

import Helpers
import datetime

def Tokenize_3(source_, iteration): #ex: DCRumHelpers.Tokenize_3(DCRumHelpers.parseDataSet(DCRumHelpers.handle(DCRumAPI.GET_Top_Ten_Slow_Ban()), 0)); 
        temp = ['-1', '-1', '-1']
        
        temp[0] = source_['formattedData'][iteration][0];
        temp[1] = source_['formattedData'][iteration][3];
        temp[2] = source_['formattedData'][iteration][4];

        return temp;
