import os.path

# Periods to be calculated
short_sma_period = 24
long_sma_period = 168
short_rsi_period = 12
long_rsi_period = 84

# How many periods will be predicted?
prediction_period = 0

# Header for the file
header = "Time,shortEMA,shortSMA,shortRSI,longEMA,longSMA,longRSI,HBB,LBB,Previous,Value\r\n"
data = ""

# Get the raw data to be used to do the math
if os.path.exists("rates-p/completehour.txt"):
    f = open("rates-p/completehour.txt","r")
    data = f.read()
    f.close()
else:
    for i in range(12):
        f = open("rates/{}.csv".format(i-2),"r")
        for line in f.readlines():
            minutes = line.split(":")[1].split(",")[0]
            if int(minutes) % 60 == 0:
                data = data + line

    f = open("rates-p/completehour.txt","w+")
    f.write(data)
    f.close()
    
# Split it to lines to be read
lines = data.splitlines()

# Arrays with the values while running the for loop
short_sma_values = []
long_sma_values = []
short_rsi_values = []
long_rsi_values = []

# Result lines to be written to the file
result = []

# Set some upfront previous data
previous_value = 0
last_short_ema = 0
last_long_ema = 0
value = 0
last_line = ""

# Process starts
for line in lines:
    # Cells in the line
    cells = line.split(",")

    # Time and value to calculate
    time = cells[0]
    next_value = cells[1]

    # Only in the second run
    if last_line:
        value = float(last_line.split(",")[1])
    else:
        value = float(cells[1])

    # SHORT Simple Moving Average Indicator
    short_sma = 0
    short_sma_count = 0
    short_sum1 = 0
    short_smma = 0
    for val in short_sma_values:
        short_sum1 += val
        short_sma_count += 1
    if short_sma_count > 0:
        short_sma = short_sum1 / short_sma_count

        short_smma = (short_sum1 - short_sma + value) / short_sma_count
    else:
        short_sma = value
    short_sma_values.append(value)
    #####################################

    # LONG Simple Moving Average Indicator
    long_sma = 0
    long_sma_count = 0
    long_sum1 = 0
    long_smma = 0
    for val in long_sma_values:
        long_sum1 += val
        long_sma_count += 1
    if long_sma_count > 0:
        long_sma = long_sum1 / long_sma_count

        long_smma = (long_sum1 - long_sma + value) / long_sma_count
    else:
        long_sma = value
    long_sma_values.append(value)
    #####################################

    # SHORT Relative Strength Index
    short_avg_loss = 0
    short_avg_gain = 0
    short_gains = 0
    short_losses = 0
    short_rsi = 0
    for val in short_rsi_values:
        if val < 0:
            short_losses += 1
            short_avg_loss += val * -1
        elif val > 0:
            short_gains += 1
            short_avg_gain += val
    if short_gains > 0:
        short_avg_gain = short_avg_gain / short_gains
    if short_losses > 0:
        short_avg_loss = short_avg_loss / short_losses

        rs = short_avg_gain / short_avg_loss
        short_rsi = 100 - (100 / (1 + rs))
    if previous_value != 0:
        short_rsi_values.append(value - previous_value)
    #########################################

    # LONG Relative Strength Index
    long_avg_loss = 0
    long_avg_gain = 0
    long_gains = 0
    long_losses = 0
    long_rsi = 0
    for val in long_rsi_values:
        if val < 0:
            long_losses += 1
            long_avg_loss += val * -1
        elif val > 0:
            long_gains += 1
            long_avg_gain += val
    if long_gains > 0:
        long_avg_gain = long_avg_gain / long_gains
    if long_losses > 0:
        long_avg_loss = long_avg_loss / long_losses

        rs = long_avg_gain / long_avg_loss
        long_rsi = 100 - (100 / (1 + rs))
    if previous_value != 0:
        long_rsi_values.append(value - previous_value)
    #########################################

    # SHORT Exponencial Moving Average (EMA)
    weighted_multiplier = 2 / (short_sma_period + 1)

    short_ema = value * weighted_multiplier + last_short_ema * (1 - weighted_multiplier)

    last_short_ema = short_ema
    #########################################

    # SHORT Exponencial Moving Average (EMA)
    weighted_multiplier = 2 / (long_sma_period + 1)

    long_ema = value * weighted_multiplier + last_long_ema * (1 - weighted_multiplier)

    last_long_ema = long_ema
    #########################################

    # SHORT Bollinger Bands
    # -- Standard deviation
    sd = 0
    for val in short_sma_values:
        sd += (val - short_sma) ** 2
    if short_sma_count > 0:
        sd = (sd / short_sma_count) ** 0.5
    # --

    # -- Higher band
    higher_band = short_sma + 2 * sd

    # -- Lower band
    lower_band = short_sma - 2 * sd
    ##########################################

    # Result array
    if time.__len__() and value!=0 and short_rsi!=0 and long_rsi!=0 and short_sma!=0 and long_sma!=0:
        result.append("{},{},{},{},{},{},{},{},{},{},{}\r\n".format(time,short_ema,long_ema,short_sma,long_sma,short_rsi,long_rsi,higher_band,lower_band,previous_value,next_value))

    # Moving arrays - deleting the first item so it's always the same sizes
    if short_sma_values.__len__() >= short_sma_period:
        short_sma_values.__delitem__(0)
    if short_rsi_values.__len__() >= short_rsi_period:
        short_rsi_values.__delitem__(0)
    if long_sma_values.__len__() >= long_sma_period:
        long_sma_values.__delitem__(0)
    if long_rsi_values.__len__() >= long_rsi_period:
        long_rsi_values.__delitem__(0)

    # Previous values to be uses in the next runs
    previous_value = value
    last_line = line

# If there is a result, take the first lines to make sure the next ones are right
if result.__len__()>0:
    result.__delitem__(slice(0,long_sma_period))

# All the data that will be stored to the file
info = ""
for line in result:
    info += line

# Write it to the file
f = open("rates-p/completehour.csv","w+")
f.write(header + info)
f.close()
