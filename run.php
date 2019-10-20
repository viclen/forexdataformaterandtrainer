<?php

$jsonurl = "http://data.fixer.io/api/latest?access_key=ef70ac307fa622227ac13b8fc9e74610&symbols=USD,AUD,CAD,PLN,MXN&format=1";

while (true) {
    $oldData = file_get_contents('lastest_rates.json');
    $json = file_get_contents($jsonurl);
    file_put_contents('lastest_rates.json', $oldData . $json . ",");
    echo "Written!" . PHP_EOL;
    sleep(3600);
}