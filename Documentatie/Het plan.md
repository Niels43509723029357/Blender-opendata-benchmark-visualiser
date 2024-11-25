# Het idee
Het idee is om een visualisatie tool te maken voor het visualiseren van de blender opendata dataset, te vinden op opendata.blender.org. Mijn plan is om dit via een command line te doen


## Must have
  * Het importeren en parsen van het JSON-bestand
  * Een CLI die d.m.v. argumenten een aantal soorten grafieken kan maken, met output in de vorm van een vector bestand
  * Het filteren van specifieke devices, besturingssystemen, scenes etc.
## Should have
  * Enigszins zuinig zijn met systeembronnen, vooral het werkgeheugen, aangezien de opendata blender snapshot rond de 1.1 GiB aan tekst is.
  * Over tijd lijngrafieken maken
## Could have
  * Waarschuwen wanneer de data oud is
  * Support voor andere formaten als .PNG en .JPEG
## Won't have
  * Automatisch de nieuwste dataset ophalen
  * Realtime data via een API oid
  * Een interactieve GUI wrapper
