#!/bin/bash
#############################################################################################################
#### Proyecto creado por Claudio Quevedo Gallardo, estudiante de Ing. Civil en Bioinformática, Utal 2020.####
#33##########################################################################################################
rm info/*
rm csv/*
rm output/*
rm producto*
#CASOS CONFIRMADOS
#descarga producto2
wget https://github.com/MinCiencia/Datos-COVID19/tree/master/output/producto2
grep 'CasosConfirmados.csv\">' producto2 |awk 'BEGIN{FS=OFS=">"}{print $3}'|awk 'BEGIN{OFS=FS="<"}{print $1}' |tail -1 > files_confirmados.txt
while IFS= read -r line; do   wget https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/output/producto2/"$line"; done < files_confirmados.txt
#procesamiento
while IFS= read -r line; do   tail -n +2 $line| awk 'BEGIN{OFS=FS=","}{region=$1;gsub(" ","_",region);print region"\t"$3"\t"$5"\t"$6}'|sort -k1 > info/datos_casos_confirmados_"$line";
tail -n +2 $line|awk 'BEGIN{OFS=FS=","}{region=$1;gsub(" ","_",region);print region}'|sort|uniq > info/regiones_"$line";
tail -n +2 $line|awk 'BEGIN{OFS=FS=","}{comuna=$3;gsub(" ","_",comuna);print comuna}'|sort|uniq > info/comunas_"$line";done < files_confirmados.txt
#REGIONES
while IFS= read -r line; do IFS=$'\n';for line2 in $(cat info/regiones_"$line");do echo "procesando regiones: ""$line"; grep "^$line2" info/datos_casos_confirmados_"$line" > info/"$line2"_region_"$line";done;done < files_confirmados.txt
#COMUNAS
while IFS= read -r line; do for line2 in $(cat info/comunas_"$line");do echo "procesando comunas: ""$line";awk 'BEGIN{OFS=FS="\t"}($2=="'$line2'"){print $0}' info/datos_casos_confirmados_"$line" > info/"$line2"_comuna_"$line"; done;done < files_confirmados.txt
#eliminar archivo sin información importante, esto es debido al formato de información.
#rm info/Desconocido*
#CASOS FALLECIDOS
#descarga producto4
wget https://github.com/MinCiencia/Datos-COVID19/tree/master/output/producto4
grep 'CasosConfirmados-totalRegional.csv\">' producto4 |awk 'BEGIN{FS=OFS=">"}{print $3}'|awk 'BEGIN{OFS=FS="<"}{print $1}'|tail -1 > files_fallecidos.txt
while IFS= read -r line; do   wget https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/output/producto4/"$line"; done < files_fallecidos.txt
while IFS= read -r line; do tail -n +2 $line|awk 'BEGIN{OFS=FS=","}{region=$1;gsub("  ","_",region);print region"\t"$5}'|head -n 16|sort -k1 > info/fallecidos_por_region_"$line";echo "procesando fallecidos: ""$line"; done < files_fallecidos.txt
#calcular cantidad de comunas por region
while IFS= read -r line; do awk 'BEGIN{OFS=FS="\t"}{print $1}' info/datos_casos_confirmados_"$line" |uniq -c|awk '{print $2"\t"$1}'|sort -k1 > info/comunas_por_region.info;done < files_confirmados.txt
#obtener d por cantidad de comunas por region
while IFS= read -r line; do paste info/fallecidos_por_region_"$line" info/comunas_por_region.info |awk 'BEGIN{OFS=FS="\t"}{print $3,$2/$4}' > info/fallecidos_por_comunas_de_region_"$line";done < files_fallecidos.txt
#CASOS DE RECUPERADOS POR COMUNA
wget https://raw.githubusercontent.com/MinCiencia/Datos-COVID19/master/output/producto15/FechaInicioSintomas.csv
awk 'BEGIN{OFS=FS=","}{$NF="0";$(NF-1)="0";$(NF-2)="0";print $0}' FechaInicioSintomas.csv |tail -n +2|sort -k1|awk 'BEGIN{OFS=FS=","}{suma=0;for(i=6; i<NF-2; ++i) {printf "%d\t",$i;suma+=$i;};comuna=$3;gsub(" ","_",comuna);print comuna"\t"suma;}'|awk 'BEGIN{OFS=FS="\t"}{print $(NF-1),$NF}' > info/Recuperados_por_comuna.info
for region in $(cat info/fallecidos_por_comunas_de_region_*|awk '{print $1}');do d=$(grep "$region" info/fallecidos_por_comunas_de_region_*|awk '{print $2}');awk 'BEGIN{OFS=FS="\t"}($1=="'$region'"){print $0,"'$d'"}' info/datos_casos_confirmados*;done > output/datos_comunas.almost
paste output/datos_comunas.almost info/Recuperados_por_comuna.info |awk 'BEGIN{OFS=FS="\t"}{print $1,$2,$3,$4,$5,$7}'> output/datos_comuna.ready
rm output/datos_comunas.almost
#inserción de las tasas de emigración por comuna
for region in $(cat Documents/tasas_emigracion_censo2017.info|awk '{print $1}');do tasa=$(grep "$region" Documents/tasas_emigracion_censo2017.info|awk '{print $2}');awk 'BEGIN{OFS=FS="\t"}($1=="'$region'"){print $0,"'$tasa'"}' output/datos_comuna.ready;done > output/datos_comunas.ready
rm output/datos_comuna.ready
grep -v "Desconocido" output/datos_comunas.ready > output/datos_final.ready
rm output/datos_comunas.ready
#mover los csv
mv *.csv csv/
