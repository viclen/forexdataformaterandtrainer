<?php

$sma_period = 50;
$rsi_period = 50;

$prediction_period = 10;

$data = "";

for ($i = 1; $i <= 10; $i++) {
    if(file_exists("$i.csv")){
        $data .= file_get_contents("$i.csv") . PHP_EOL;
    }
}

$lines = explode(PHP_EOL, $data);

$sma_values = [];
$rsi_values = [];

$result = "Time,Max,Min,SMA,RSI,Value" . PHP_EOL;

$previous_value = 0;

echo "[";
$current_step = 0;

foreach ($lines as $i => $line) {
    if (!strpos($line, ":00,")) {
        continue;
    }

    $cells = explode(",", $line);
    $value = $cells[1];

    // Simple Moving Average Indicator (SMA)
    $sma = 0;
    $sma_count = 0;
    for ($j = 0; $j < $sma_period && $j < count($sma_values); $j++) {
        $sma += $sma_values[$j];
        $sma_count++;
    }
    if ($sma) {
        $sma = $sma / $sma_count;
    } else {
        $sma = $value;
    }
    if (count($sma_values) >= $sma_period + $prediction_period) {
        array_splice($sma_values, 0, 1);
    }
    $sma_values[] = $value;

    // Relative Strength Index (RSI)
    $avg_loss = 0;
    $avg_gain = 0;
    $gains = 0;
    $losses = 0;
    $rsi = 0;
    for ($j = 0; $j < $rsi_period && $j < count($rsi_values); $j++) {
        $val = $rsi_values[$j];
        if ($val < 0) {
            $losses++;
            $avg_loss += sqrt($val ** 2);
        } elseif ($val > 0) {
            $gains++;
            $avg_gain += $val;
        }
    }
    if ($gains) {
        $avg_gain = $avg_gain / $gains;
    }
    if ($losses) {
        $avg_loss = $avg_loss / $losses;

        $rs = $avg_gain / $avg_loss;
        $rsi = 100 - (100 / (1 + $rs));
    }
    if (count($rsi_values) >= $rsi_period + $prediction_period) {
        array_splice($rsi_values, 0, 1);
        // break;
    }
    if ($previous_value) {
        $rsi_values[] = $value - $previous_value;
    }

    // Put to the string that will be written to the file
    if ($value) {
        $result .= "$cells[0],$cells[2],$cells[3],$sma,$rsi,$value" . PHP_EOL;
    }

    $previous_value = $value;

    $step = round($i * 100 / count($lines));
    if ($step != $current_step) {
        echo "•";
    }
    $current_step = $step;
}
echo "] Complete!" . PHP_EOL;

file_put_contents("completehour-p10.csv", $result);
