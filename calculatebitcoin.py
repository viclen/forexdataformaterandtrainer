import os.path

sma_period = 20
rsi_period = 20

prediction_period = 0

header = "Time,EMA,SMA,RSI,HBB,LBB,Value\r\n"
data = ""

if os.path.exists("rates-p/bitcoin.txt"):
    f = open("rates-p/bitcoin.txt","r")
    data = f.read()
    f.close()
    
lines = data.splitlines()
lines.reverse()

sma_values = []
rsi_values = []

result = []

previous_value = 0
last_ema = 0

value = 0

last_line = ""

for line in lines:
    # Clear string
    if line.__contains__('"'):
        line = "{}{}".format(line.split('"')[0],line.split('"')[1].replace(',',''))

    # Cells in the line
    cells = line.split(",")

    # Time to calculate
    time = cells[0]

    # Set to datetime
    time = time.replace("Jan", "01")
    time = time.replace("Feb", "02")
    time = time.replace("Mar", "03")
    time = time.replace("Apr", "04")
    time = time.replace("May", "05")
    time = time.replace("Jun", "06")
    time = time.replace("Jul", "07")
    time = time.replace("Aug", "08")
    time = time.replace("Sep", "09")
    time = time.replace("Oct", "10")
    time = time.replace("Nov", "11")
    time = time.replace("Dec", "12")
    time = "20{}-{}-{} 00:00".format(time.split("-")[2], time.split("-")[1], time.split("-")[0])

    # Next value
    next_value = cells[1]

    # Only in the second run
    if last_line:
        value = float(last_line.split(",")[1])
    else:
        value = float(cells[1])

    # Simple Moving Average Indicator
    sma = 0
    sma_count = 0
    sum1 = 0
    smma = 0
    for val in sma_values:
        sum1 += val
        sma_count += 1
    if sma_count > 0:
        sma = sum1 / sma_count
        smma = (sum1 - sma + value) / sma_count
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
    if gains > 0:
        avg_gain = avg_gain / gains
    if losses > 0:
        avg_loss = avg_loss / losses

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
    if previous_value != 0:
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
    if sma_count > 0:
        sd = (sd / sma_count) ** 0.5
    # --

    # -- Higher band
    higher_band = sma + 2 * sd

    # -- Lower band
    lower_band = sma - 2 * sd
    ##########################################

    # Result array
    if time.__len__()>0 and value!=0 and rsi!=0 and sma!=0:
        result.append("{},{},{},{},{},{},{}\r\n".format(time,ema,sma,rsi,higher_band,lower_band,next_value))

    previous_value = value

    # Moving arrays
    if sma_values.__len__() >= sma_period:
        sma_values.__delitem__(0)
    if rsi_values.__len__() >= rsi_period:
        rsi_values.__delitem__(0)

    last_line = line

if result.__len__()>0:
    result.__delitem__(slice(0,sma_period))

info = ""
for line in result:
    info += line.replace("\ufeff", "")

f = open("rates-p/bitcoin.csv","w+")
f.write(header + info)
f.close()
