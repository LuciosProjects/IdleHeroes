import time
import numpy as np
import numpy.random as rnd
import colorama
from colorama import Fore
import matplotlib.pyplot as plt

# Tier chances dictionary
TiersNPA = np.array(["E-", "E", "E+", "D-", "D", "D+", "C-", "C", "C+", "B-", "B", "B+", "A-", "A", "A+", "S", "SS", "SSS"])
Distrib = {
    "E-": .043,     "E": .198,     "E+": .288,
    "D-": .2,       "D": .092,     "D+": .048,
    "C-": .044,     "C": .043,     "C+": .0213,
    "B-": .0162,    "B": .0055,    "B+": .000745,
    "A-": .00015,   "A": .000065,  "A+": .000025,
    "S" : .000005, "SS": .000005, "SSS": .000005
}
#                        E-     E    E+   D-    D    D+    C-     C     C+     B-      B       B+      A-        A       A+        S       SS      SSS
DistribVec = np.array([.043, .198, .288, .2, .092, .048, .044, .043, .0213, .0162, .0055, .000745, .00015, .000065, .000025, .000005, .000005, .000005])
CumulativeDist = np.cumsum(DistribVec)

# Return values dictionary
ReturnValues = {
    "E-":   10,  "E":     15,  "E+":     20,
    "D-":   30,  "D":     50,  "D+":     70,
    "C-":  100,  "C":    150,  "C+":    200,
    "B-":  300,  "B":    600,  "B+":   1800,
    "A-": 8000,  "A":  15000,  "A+":  25000,
    "S": 50000, "SS": 100000, "SSS": 200000
}
#                             E-   E  E+  D-   D  D+   C-    C   C+   B-    B    B+    A-      A     A+      S      SS     SSS
ReturnedValuesVec = np.array([10, 15, 20, 30, 50, 70, 100, 150, 200, 300, 600, 1800, 8000, 15000, 25000, 50000, 100000, 200000])

# Gala individual scores dictionary 
GalaIndividualScore = {
    "E-":  3,  "E":  4,  "E+":  5,
    "D-":  6,  "D":  7,  "D+":  8,
    "C-":  9,  "C": 10,  "C+": 11,
    "B-": 12,  "B": 13,  "B+": 14,
    "A-": 15,  "A": 16,  "A+": 17,
    "S" : 18, "SS": 19, "SSS": 20
}
#                                   E-  E  E+  D-  D  D+  C-   C  C+  B-   B  B+  A-   A  A+   S  SS  SSS
GalaIndividualScoreVec = np.array([  3, 4,  5,  6, 7,  8,  9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19,  20])

AwCost = 100

def GalaSession(R_init: int = 0, Starlights: int = 0, RefundTierLimit: str = "E-",
                EnableRecycling: bool = False, PrintResult: bool = False):
    # NOTE: Assuming there's enough hero copies to support the whole session

    # Settings
    Resources   = R_init
    RefundLimit = ReturnValues[RefundTierLimit]
    Valuables   = np.array([],dtype='<U3')
    GalaScore   = int(0)
    NAwakenings = int(0)

    # Starlight crystals segment
    RefundBank = 0
    NAwakenings += Starlights
    Roll_val = rnd.random(Starlights)
    Roll_mat = np.array([Roll_val for _ in range(18)]).T
    Position = Roll_mat < CumulativeDist
    SumOfTrues = np.sum(Position,axis=1)
    Label_indices = 18 - SumOfTrues

    GalaScore += np.sum(GalaIndividualScoreVec[Label_indices.astype(int)])

    ToKeep = ReturnedValuesVec[Label_indices.astype(int)] > RefundLimit
    Valuables = np.concatenate((Valuables,TiersNPA[Label_indices.astype(int)][ToKeep]))
    
    if(EnableRecycling):
        RefundBank += np.sum(ReturnedValuesVec[Label_indices.astype(int)][~ToKeep])

    # Starry gems segment
    Resources += RefundBank
    Done = False
    while(not Done):
        NAw = int(Resources/AwCost) # Number of awakenings in the current session
        Resources -= NAw*AwCost
        RefundBank = 0

        # Starry gems awakening session
        NAwakenings += NAw
        Roll_val = rnd.random(NAw)
        Roll_mat = np.array([Roll_val for _ in range(18)]).T
        Position = Roll_mat < CumulativeDist
        SumOfTrues = np.sum(Position,axis=1)
        Label_indices = 18 - SumOfTrues

        GalaScore += np.sum(GalaIndividualScoreVec[Label_indices.astype(int)])

        ToKeep = ReturnedValuesVec[Label_indices.astype(int)] > RefundLimit
        Valuables = np.concatenate((Valuables,TiersNPA[Label_indices.astype(int)][ToKeep]))
        
        if(EnableRecycling):
            RefundBank += np.sum(ReturnedValuesVec[Label_indices.astype(int)][~ToKeep])

        Resources += RefundBank

        if(Resources < AwCost):
            Done = True

    if(PrintResult):
        print(f"# of starlight crystals - {Starlights}")
        print(f"initial starry gems balance {R_init}")
        print(f"Total Gala score: {GalaScore}")
        print(f"# of awakenings: {NAwakenings}")
        print(f"Valuable awakenings:\n {Valuables}")

    return GalaScore, NAwakenings, Valuables

def RecyclingEnableMultipleChoice():
    EnableStr = input("Enable lower tier awakening recycling? (yes/no) default is yes (press enter)\n")

    if(EnableStr in ["yes", "YES", "Yes", "yEs", "yeS", "YEs", "yES", "YeS", "y", "Y", "ye", "YE", "Ye", "yE", ""]):
        Enable = True
        print("Recycling enabled\n")
    else:
        Enable = False
        print("Recycling disabled\n")

    if(not Enable):
        ValThresh = "E-"
    else:
        ValThresh = input("What is the maximal tier for which you permit recycling? (tiers E- to SS), default is E-\n")

        if(ValThresh not in ["E-", "E", "E+", "D-", "D", "D+", "C-", "C", "C+", "B-", "B", "B+", "A-", "A", "A+", "S", "SS"]):
            if(ValThresh in ["e-", "e", "e+", "d-", "d", "d+", "c-", "c", "c+", "b-", "b", "b+", "a-", "a", "a+", "s", "ss"]):
                ValThresh = ValThresh.upper()
            else:
                ValThresh = "E-"
        print(f"Threshold - {ValThresh}\n")

    return Enable, ValThresh

def GetTime(tStart: float) -> str:
    ExecTime = time.time() - tStart

    if(ExecTime > 3600):
        return f"{ExecTime/3600} hours"
    elif(ExecTime > 60):
        return f"{ExecTime/60} minutes"
    else:
        return f"{ExecTime} seconds"

if __name__ == "__main__":
    colorama.init()
    N_Iterations = 0

    while True:
        Session_tstart = time.time()
        N_Iterations += 1
        print( Fore.LIGHTCYAN_EX + "---------------------------------------------------------------------------")
        print(f"------------------------------ Iteration #{N_Iterations} -------------------------------")
        print( "---------------------------------------------------------------------------")
        print(Fore.RESET)

        # Main settings
        NStarlights                 = int(input("How many starlight crystals will be used?\n")) # Number of starting stalights
        InitialBalance              = int(input("What is your starry gems initial balance?\n")) # Awakening session begins with this amount of starry gems

        if(NStarlights + InitialBalance <= 0):
            print("No resources provided")
            exit()

        EnableRecycling, ValueThreshold = RecyclingEnableMultipleChoice()                       # Enable recycling of low tier awakened heroes

        N_Experiments               = int(input("How many experiments to do? (recommended amount is 10,000, higher numbers will produce more accurate results but will take longer to compute)\n"))
        GalaScores                  = np.zeros(N_Experiments)                                   # Allocating memory for Gala score statistics
        Awakenings                  = np.zeros(N_Experiments)                                   # Allocating memory for # of awakenings atatistics

        # Number of pulls for every letter category init
        N_Cm_pulls, N_C_pulls, N_Cp_pulls  = int(0), int(0), int(0)
        N_Bm_pulls, N_B_pulls, N_Bp_pulls  = int(0), int(0), int(0)
        N_Am_pulls, N_A_pulls, N_Ap_pulls  = int(0), int(0), int(0)
        N_S_pulls, N_SS_pulls, N_SSS_pulls = int(0), int(0), int(0)

        print("\nCode is running...\n")
        for i in range(N_Experiments):
            GalaScore, NAwakenings, Valuables = GalaSession(InitialBalance, Starlights=NStarlights, RefundTierLimit=ValueThreshold,
                                                            EnableRecycling=EnableRecycling, 
                                                            PrintResult=False)

            GalaScores[i] = GalaScore
            Awakenings[i] = NAwakenings

            # Checking existence of C rank awakenigns
            if ["C-"] in Valuables:
                N_Cm_pulls += 1

            if ["C"] in Valuables:
                N_C_pulls += 1

            if ["C+"] in Valuables:
                N_Cp_pulls += 1

            # Checking existence of B rank awakenigns
            if ["B-"] in Valuables:
                N_Bm_pulls += 1

            if ["B"] in Valuables:
                N_B_pulls += 1

            if ["B+"] in Valuables:
                N_Bp_pulls += 1

            # Checking existence of A rank awakenigns
            if ["A-"] in Valuables:
                N_Am_pulls += 1

            if ["A"] in Valuables:
                N_A_pulls += 1

            if ["A+"] in Valuables:
                N_Ap_pulls += 1

            # Checking existence of S rank awakenigns
            if ["S"] in Valuables:
                N_S_pulls += 1

            if ["SS"] in Valuables:
                N_SS_pulls += 1

            if ["SSS"] in Valuables:
                N_SSS_pulls += 1

        Above100total = np.sum(GalaScores >= 100)
        Above150Total = np.sum(GalaScores >= 150)

        print(  Fore.LIGHTGREEN_EX + "--------------------------------- Summary ---------------------------------\n",
                f"Execution time: " + GetTime(Session_tstart) + "\n",
                f"Data obtained from simulating {N_Experiments} experiments.\n",
                Fore.LIGHTRED_EX + "ASSUMING ENOUGH HERO COPIES ARE AVAILABLE!\n\n",

                Fore.LIGHTGREEN_EX + f"Given an initial balance of {InitialBalance} starry gems & {NStarlights} starlight crystals\n",
                "Recycling" + [" enabled\n" if(EnableRecycling) else " disabled\n"][0],
                [f"Recycling threshold - \"{ValueThreshold}\"\n" if(EnableRecycling) else ""][0])

        print(  Fore.RESET + "Results:\n"
                f"Mean # of awakenings - {np.floor(np.mean(Awakenings))}\n",
                f"Mean Gala score - {np.floor(np.mean(GalaScores))} \n\n",

                f"Probability to score at or higher than 100 points in gala - {Above100total/N_Experiments}\n",
                f"Probability to score at or higher than 150 points in gala - {Above150Total/N_Experiments}\n\n",

                f"Probability for \"C-\"  tier awakenings - {N_Cm_pulls/N_Experiments}\n",
                f"Probability for \"C\"   tier awakenings - {N_C_pulls/N_Experiments}\n",
                f"Probability for \"C+\"  tier awakenings - {N_Cp_pulls/N_Experiments}\n",
                f"Probability for \"B-\"  tier awakenings - {N_Bm_pulls/N_Experiments}\n",
                f"Probability for \"B\"   tier awakenings - {N_B_pulls/N_Experiments}\n",
                f"Probability for \"B+\"  tier awakenings - {N_Bp_pulls/N_Experiments}\n",
                f"Probability for \"A-\"  tier awakenings - {N_Am_pulls/N_Experiments}\n",
                f"Probability for \"A\"   tier awakenings - {N_A_pulls/N_Experiments}\n",
                f"Probability for \"A+\"  tier awakenings - {N_Ap_pulls/N_Experiments}\n",
                f"Probability for \"S\"   tier awakenings - {N_S_pulls/N_Experiments}\n",
                f"Probability for \"SS\"  tier awakenings - {N_SS_pulls/N_Experiments}\n",
                f"Probability for \"SSS\" tier awakenings - {N_SSS_pulls/N_Experiments}\n")

        # Plot histograms
        plt.figure("Histograms")

        ax1 = plt.subplot(1,2,1)
        ax1.set_title("Awakenings")
        ax1.grid(True)
        plt.hist(Awakenings)
        ax1.set_xlabel("# of awakenings")
        ax1.set_ylabel("# of runs")

        ax2 = plt.subplot(1,2,2)
        ax2.set_title("Gala scores")
        ax2.grid(True)
        plt.hist(GalaScores)
        ax2.set_xlabel("Score values")
        ax2.set_ylabel("# of runs")
        plt.show()
