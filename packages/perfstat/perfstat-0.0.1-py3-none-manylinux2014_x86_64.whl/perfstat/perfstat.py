import sys
import os
import subprocess
from numpy import percentile
import pandas as pd
import math
from typing import List, Tuple

# Check if string can be converted to float
def isfloat(str):
    str = str.replace(',', '')
    try:
        float(str)
        return True
    except ValueError:
        return False

# Statistical t-value coeff for the first 30 deg. of freedom. 
# Index corresponds to num. deg. of freedom (that's why first and second valus are same).
tValue = {
    "90" : [6.313751514800932, 6.313751514800932,2.919985580355516,2.3533634348018264,2.13184678133629,2.015048372669157,1.9431802803927816,1.894578605061305,1.8595480375228424,1.8331129326536335,1.8124611228107335,1.7958848187036691,1.782287555649159,1.7709333959867988,1.7613101357748562,1.7530503556925547,1.74588367627624,1.7396067260750672,1.7340636066175354,1.729132811521367,1.7247182429207857,1.7207429028118775,1.717144374380242,1.7138715277470473,1.7108820799094275,1.7081407612518986,1.7056179197592727,1.7032884457221265,1.701130934265931,1.6991270265334972,1.6972608943617378],
    "95" : [12.706204736432095, 12.706204736432095,4.302652729911275,3.182446305284263,2.7764451051977987,2.5705818366147395,2.4469118487916806,2.3646242510102993,2.3060041350333704,2.2621571627409915,2.2281388519649385,2.200985160082949,2.1788128296634177,2.1603686564610127,2.1447866879169273,2.131449545559323,2.1199052992210112,2.1098155778331806,2.10092204024096,2.093024054408263,2.0859634472658364,2.079613844727662,2.0738730679040147,2.0686576104190406,2.0638985616280205,2.059538552753294,2.055529438642871,2.0518305164802833,2.048407141795244,2.045229642132703,2.0422724563012373],
    "99" : [63.65674116287399, 63.65674116287399,9.92484320091807,5.84090929975643,4.604094871415897,4.032142983557536,3.707428021324907,3.4994832973505026,3.3553873313333957,3.2498355440153697,3.169272667175838,3.105806513221101,3.0545395883368704,3.012275838207184,2.97684273411266,2.946712883338615,2.9207816223499967,2.8982305196347173,2.878440472713585,2.860934606449914,2.845339709776814,2.831359558017186,2.818756060596369,2.8073356837675227,2.796939504772804,2.787435813675851,2.7787145333289134,2.7706829571216756,2.763262455461066,2.756385903670335,2.7499956535670305],
}

zValue = { "90": 1.644854, "95": 1.95996, "99": 2.57583}

def multirun(
    runCmd: str = "", 
    runCnt: int = 10, 
    measure: str = "",
    separator: str = "",
    mementsFile: str = "",
    statsFile: str = "",
    floatFormat: str = "%.4e",
    printOutput: bool = True,
    printCmdOutput: bool = False,
    printCSV: bool = False) -> Tuple[pd.DataFrame, pd.DataFrame]:

    if runCnt < 2:
        return("Number of runs must be greater than 1")
    
    # If no runCmd given use default
    if runCmd == "":
        runCmd = "sudo likwid-perfctr -C 0 -g CLOCK ls"
        
    # Default measurements for likwid-perfctr
    if "likwid-perfctr" in runCmd and measure == "":
        keywords = ["Runtime (RDTSC) [s]", 
                    "Runtime unhalted [s]", 
                    "Clock [MHz]", 
                    "Uncore Clock [MHz]", 
                    "CPI",
                    "Energy [J]",
                    "Power [W]"]
        
    elif "perf stat" in runCmd and measure == "":        
        keywords = ["task-clock", 
                    "context-switches",
                    "cpu-migrations",
                    "page-faults",
                    "cycles",
                    "instructions", 
                    "branches", 
                    "branch-misses"]
    else:
        keywords = measure.split(',')
        
    if "likwid-perfctr" in runCmd and separator == "":
        separator = '|'
    elif "perf stat" in runCmd and separator == "":
        separator = ' '
        
    if printOutput:
        print(f"Run command: '{runCmd}'")
        print(f"Run count: {runCnt}")
        print(f"Measuring: {keywords}")
        print(f"Separator: '{separator}'")
        print(f"Measurements file: '{mementsFile}'")
        print(f"Statistics file: '{statsFile}'")
        print(f"Float format: '{floatFormat}'")

    mements = pd.DataFrame({key:[None]*runCnt for key in keywords}, dtype=float)
    stats = pd.DataFrame({key:[None] for key in keywords}, 
                        index=[ "Mean", 
                                "Std. dev.", 
                                "Std. error",
                                "Conf. inter. 90% (min)",
                                "Conf. inter. 90% (max)",
                                "Conf. inter. 95% (min)",
                                "Conf. inter. 95% (max)",
                                "Conf. inter. 99% (min)",
                                "Conf. inter. 99% (max)"], dtype=float)

    percentDone = 0
    for i in range(runCnt):
        if ((i+1)%(runCnt//10) == 0) and percentDone < 100 and printOutput:
            percentDone += 10
            stmp = f"Done: {percentDone}%"
            if percentDone == 100 or printCmdOutput:
                print(stmp)
            else:
                print(stmp, end='\r')
        p = subprocess.run(runCmd, capture_output=True, text=True, shell=True)
        sto = p.stdout + p.stderr

        if printCmdOutput:
            print(sto)
            
        for line in sto.split('\n'):
            val = None
            key = None
            for seg in line.split(separator):
                seg = seg.strip()
                if key == None and seg in keywords:
                    key = seg
                if isfloat(seg):
                    val = float(seg.replace(',',''))
                if key != None and val != None:
                    mements[key][i] = val
                    break            
                
    mements.index.name = "Run ID"

    for key in keywords:
        stats[key]["Mean"] = mements[key].mean()
        stats[key]["Std. dev."] = mements[key].std()
        stats[key]["Std. error"] = stats[key]["Std. dev."]/math.sqrt(runCnt)
        if runCnt < 31:
            stats[key]["Conf. inter. 90% (min)"] = stats[key]["Mean"] - tValue["90"][runCnt-1]*stats[key]["Std. error"]
            stats[key]["Conf. inter. 90% (max)"] = stats[key]["Mean"] + tValue["90"][runCnt-1]*stats[key]["Std. error"]
            stats[key]["Conf. inter. 95% (min)"] = stats[key]["Mean"] - tValue["95"][runCnt-1]*stats[key]["Std. error"]
            stats[key]["Conf. inter. 95% (max)"] = stats[key]["Mean"] + tValue["95"][runCnt-1]*stats[key]["Std. error"]
            stats[key]["Conf. inter. 99% (min)"] = stats[key]["Mean"] - tValue["99"][runCnt-1]*stats[key]["Std. error"]
            stats[key]["Conf. inter. 99% (max)"] = stats[key]["Mean"] + tValue["99"][runCnt-1]*stats[key]["Std. error"]
        else:
            stats[key]["Conf. inter. 90% (min)"] = stats[key]["Mean"] - zValue["90"]*stats[key]["Std. error"]
            stats[key]["Conf. inter. 90% (max)"] = stats[key]["Mean"] + zValue["90"]*stats[key]["Std. error"]
            stats[key]["Conf. inter. 95% (min)"] = stats[key]["Mean"] - zValue["95"]*stats[key]["Std. error"]
            stats[key]["Conf. inter. 95% (max)"] = stats[key]["Mean"] + zValue["95"]*stats[key]["Std. error"]
            stats[key]["Conf. inter. 99% (min)"] = stats[key]["Mean"] - zValue["99"]*stats[key]["Std. error"]
            stats[key]["Conf. inter. 99% (max)"] = stats[key]["Mean"] + zValue["99"]*stats[key]["Std. error"]
            
    if mementsFile != "":            
        mements.to_csv(mementsFile, float_format=floatFormat)
    if statsFile != "":            
        stats.to_csv(statsFile, float_format=floatFormat)
        
    if printCSV:
        print(mements)
        print(stats)
    
    return mements, stats

def main():
    flag = ""
    runCmd = ""
    mementsFile = ""
    statsFile = ""
    measure = ""
    separator = ""
    runCnt = 10
    floatFormat = "%.4e"
    printOuput = 1
    printCmdOutput = 0
    printCSV = 0
    for arg in sys.argv:
        if arg[0] == '-':
            flag = arg
            continue
        if flag == "-c":
            runCmd = arg
            flag = ""
        if flag == "-r":
            runCnt = int(arg)
            flag = ""
        if flag == "-s":
            separator = arg
            flag = ""
        if flag == "-fm":
            mementsFile = arg
            flag = ""
        if flag == "-fs":
            statsFile = arg
            flag = ""
        if flag == "-m":
            measure = arg
            flag = ""
        if flag == "-g":
            floatFormat = arg
            flag = ""
        if flag == "-po":
            printOuput = int(arg)
            flag = ""
        if flag == "-pc":
            printCmdOutput = int(arg)
            flag = ""
        if flag == "-pv":
            printCSV = int(arg)
            flag = ""
            
    multirun(runCmd = runCmd, 
             runCnt = runCnt, 
             measure=measure,
             separator=separator,
             mementsFile=mementsFile, 
             statsFile=statsFile,
             floatFormat=floatFormat,
             printOutput=printOuput,
             printCmdOutput=printCmdOutput,
             printCSV=printCSV)
    
if __name__ == "__main__":
    main()