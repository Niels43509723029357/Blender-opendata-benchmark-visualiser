# Het idee
Het idee is om een visualisatie tool te maken voor het visualiseren van de blender opendata dataset, te vinden op opendata.blender.org. Mijn plan is om dit via een command line te doen, maar als ik nog tijd over heb zal ik mogelijk nog een GUI wrapper hiervoor maken


## Must have
  * Het importeren en parsen van het JSON-bestand
  * Een CLI die d.m.v. argumenten een aantal soorten grafieken kan maken, met output in de vorm van een vector bestand
  * Het filteren van specifieke devices, besturingssystemen, benchmarks etc.
## Should have
  * Naast het JSON-bestand ook het .zip-bestand supporten zoals je het krijgt van de site.
  * Enigszins zuinig zijn met systeembronnen, vooral het werkgeheugen, aangezien de opendata blender snapshot rond de 1.1 GiB aan tekst is.
  * Over tijd lijngrafieken maken
## Could have
  * Waarschuwen wanneer de data oud is
  * Support voor andere formaten als .PNG en .JPEG

## Won't have
  * Automatisch de nieuwe dataset ophalen
  * Realtime data via een API oid
  * Een interactieve GUI wrapper
