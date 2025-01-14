# Blender visualisatie tool
Deze tool is gemaakt om benchmarks van blender's opendata project te parsen en te visualiseren als lijn- of staafdiagram.

## Inhoudsopgaven
* [Installatie](#Installatie)
* [Gebruik](#Gebruik)
* [Features](#Features)
* [Bijdragen](#Bijdragen)
* [Licentie](#Licentie)



## Installatie
1. Clone de repository
    ```bash
   git clone https://github.com/Niels43509723029357/Blender-opendata-benchmark-visualiser
   ```
2. Ga naar de project folder
    ```bash
   cd Blender-opendata-benchmark-visualiser
   ```
3. Installeer de dependencies
    ```bash
   pip install -r requirements.txt
   ```
4. Installeer de laatste snapshot van [blender's opendata dataset](https://opendata.blender.org/snapshots/opendata-latest.zip), en unzip deze.
    De exacte stappen voor het unzippen liggen aan het OS dat je gebruikt, maar in windows gebruik je je rechtermuisknop en klik je op extract all.
5. Ga naar [Gebruik](#Gebruik) om het programma te gebruiken


## Gebruik
Na het installeer process, kan je de tool gebruiken met de volgende opties:

* Het input bestand. Dit is een pad naar een bestaand .jsonl bestand, wat je bij installatie hebt gekregen na het unzippen. Als je linux gebruikt kan je ook ~ gebruiken voor je home folder. Dit is verplicht om op te geven
* Het output bestand. Dit is het een pad naar de plek waar het programma het .svg aanmaakt. Ook hier kan je als je linux gebruikt ~ gebruiken voor je home folder. Deze is ook verplicht om op te geven
* De grootte van de chunks kan je opgeven door middel van ```--chunksize``` of ```-cs```. Deze grootte bepaald hoeveel regels het programma tegelijk inlaadt. Dit is belangrijk aangezien het programma anders alles inlaadt en erg veel systeemgeheugen gebruikt. Standaard is deze waarde 30.000 regels.
* De soort grafiek kan je opgeven met ```--plot```, of ```-p```. Je kan hier kiezen tussen ```line``` voor een lijngrafiek, waarbij het de performance over een tijdsperiode laat zien, of ```bar``` voor een staafdiagram. Bij het staafdiagram kan je verschillende devices makkelijker vergelijken met elkaar.
* Je kan het programma instellen om verboos te zijn met ```-v```, zodat het meer uitprint terwijl het bezig is.
* Je kan met ```--devices``` of ```-d``` filteren voor bepaalde devices, bijvoorbeeld een ```GeForce GTX 1660 SUPER``` of een ```AMD Ryzen 9 3900XT 12-Core Processor```. Let op dat je de devices omringt met aanhalingstekens omdat deze spaties bevatten. Je kan met een spatie ertussen meerdere devices selecteren
* Je kan met ```--scene``` of ```-s``` filteren voor de scene die gebenchmarked wordt. Bijvoorbeeld ```bmw27```. Dit helpt omdat de verschillende scenes erg kunnen verschillen in performance, en dit de scores kan beïnvloeden als je dit niet doet.
* Je kan ook nog met ```-os``` filteren voor het gebruikte besturingssysteem, omdat dit, voornamelijk bij de CPU tests, de scores soms nog wat kan beïnvloeden. Let op dat Apple devices hier als Darwin aangegeven staan. Je kan hier kiezen tussen ```Windows```, ```Linux```, en ```Darwin```

Een voorbeeld van hoe je dit programma gebruikt staat hieronder aangegeven
```bash
python main.py -s "bmw27" ~/python/opendataset.jsonl ~/python/output.svg -os Linux --plot bar -d "GeForce GTX 1660 SUPER" "Radeon RX 580 Series"
```
## Features
- Creëert een .svg met de grafiek
- Kan staafdiagram of lijngrafiek maken
- Mogelijkheid om te filteren op specifieke apparaten, scènes en besturingssystemen
- Instelbare grootte van chunks, om geheugengebruik te minimaliseren
- Opties voor meer inzicht tijdens de uitvoer van de applicatie

## Bijdragen

Bijdragen en pull requests worden altijd gewaardeerd, volg deze stappen om te kunnen bijdragen:

1. Clone deze repository als je dit nog niet hebt gedaan:
```bash
git clone https://github.com/Niels43509723029357/Blender-opendata-benchmark-visualiser
```
2. Maak een branch aan voor je aanpassingen:
```bash
git checkout -b mijn-nieuwe-tak
```
3. Maak jouw aanpassingen 
4. Maak deze aanpassingen zichtbaar voor anderen
```bash
git push origin mijn-nieuwe-tak
```
5. Open een Pull Request op github.com.

## Licentie

Dit project valt onder het GPLv2, ook wel het GNU Public License versie 2. Zie [Licentie](Documentatie/LICENSE.txt) voor de licensie
