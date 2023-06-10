import numpy as np

##### Variable definitions #####
numOfDays       = 300
DailyIncrement  = 3600
Balance         = float(300000)
Prices          = np.array([(6000.0 + float(i)*1000.0) for i in range(0,20)])
PricesCS        = np.cumsum(Prices)
Tickets         = np.zeros(20,dtype=int)

##### Checking conditions #####
if(Balance < 6000.0):
    print("insufficient funds, exiting program")
    exit()

##### Main Loop #####
for i in range(0,20):
    dailyBoughtP = PricesCS[i]
    
    ##### How many whole days can be bought with the current setup #####
    CurrentBalance = Balance
    # Days = 0
    ExtraTixEnable = False
    for day in range(1,numOfDays):
        CurrentBalance += DailyIncrement - dailyBoughtP  # Total daily changes
        if(CurrentBalance < 0.0):
            CurrentBalance += dailyBoughtP
            continue
        # Days += 1
        Tickets[i] += i + 1

    ##### How many tickets can be bought with the remaining balance #####
    if(CurrentBalance > 0.0):
        ExtraTix = np.sum(CurrentBalance >= PricesCS)
        Tickets[i] += ExtraTix

MaxTix = np.max(Tickets)
MaxTix_daily = np.argmax(Tickets) + 1
print(f"cumulative sums: {PricesCS}")
print(f"Tickets: {Tickets}")
print(f"Max tickets - {MaxTix}")
print(f"for {MaxTix_daily} bought a day for {numOfDays} days (including paying the excess on the last day)")