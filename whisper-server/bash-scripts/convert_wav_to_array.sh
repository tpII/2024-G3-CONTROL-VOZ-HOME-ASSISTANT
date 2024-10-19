#!/bin/bash

# Extraer datos numéricos usando sox
data=$(sox $1 -t dat - | grep -v '^;' | awk '{printf "%.10f\n", $2}')

# Convertir los datos a un array en formato [a,b,c,d]
array="["
for value in $data; do
  # Convertir el valor a número flotante, multiplicar por 10, y redondear
  rounded=$(awk -v val="$value" 'BEGIN { printf "%.0f", val * 10 }')
  array+="$rounded,"
done

# Remover la última coma y cerrar el array
array="${array%,}]"

# Mostrar el array
echo $array > output.txt
