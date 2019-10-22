import os.path

sma_period = 20
rsi_period = 20

prediction_period = 0

header = "Time,EMA,SMA,RSI,HBB,LBB,Value\r\n"
data = ""

if os.path.exists("rates-p/complete15min.txt"):
    f = open("rates-p/complete15min.txt","r")
    data = f.read()
    f.close()
else:
    for i in range(12):
        f = open("rates/{}.csv".format(i-2),"r")
        for line in f.readlines():
            minutes = line.split(":")[1].split(",")[0]
            if int(minutes) % 15 == 0:
                data = data + line

    f = open("rates-p/complete15min.txt","w+")
    f.write(data)
    f.close()
    
lines = data.splitlines()

sma_values = []
rsi_values = []

result = []

previous_value = 0
last_ema = 0

value = 0

last_line = ""

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

    # Simple Moving Average Indicator
    sma = 0
    sma_count = 0
    for val in sma_values:
        sma += val
        sma_count += 1
    if sma:
        sma = sma / sma_count
    else:
        sma = value
    sma_values.append(value)
    #####################################

    # Relative Strength Index
    avg_loss = 0
    avg_gain = 0
    gains = 0
    losses = 0
    rsi = 0
    for val in rsi_values:
        if val < 0:
            losses += 1
            avg_loss += val * -1
        elif val > 0:
            gains += 1
            avg_gain += val
    if gains:
        avg_gain = avg_gain / gains
    if losses:
        avg_loss = avg_loss / losses

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
    if previous_value:
        rsi_values.append(value - previous_value)
    #########################################

    # Exponencial Moving Average (EMA)
    weighted_multiplier = 2 / (sma_period + 1)

    ema = value * weighted_multiplier + last_ema * (1 - weighted_multiplier)

    last_ema = ema
    #########################################

    # Bollinger Bands
    # -- Standard deviation
    sd = 0
    for val in sma_values:
        sd += (val - sma) ** 2
    if sma_count:
        sd = (sd / sma_count) ** 0.5
    # --

    # -- Higher band
    higher_band = sma + 2 * sd

    # -- Lower band
    lower_band = sma - 2 * sd
    ##########################################

    # Result array
    if time.__len__() and value and rsi and sma:
        result.append("{},{},{},{},{},{},{}\r\n".format(time,ema,sma,rsi,higher_band,lower_band,next_value))

    previous_value = value

    # Moving arrays
    if sma_values.__len__() >= sma_period:
        sma_values.__delitem__(0)
    if rsi_values.__len__() >= rsi_period:
        rsi_values.__delitem__(0)

    last_line = line

if result.__len__():
    result.__delitem__(slice(0,sma_period))

info = ""
for line in result:
    info += line

f = open("rates-p/complete15min.csv","w+")
f.write(header + info)
f.close()
