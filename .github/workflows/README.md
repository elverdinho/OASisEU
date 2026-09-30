# Aggiornamento automatico delle call

`aggiorna-call.yml` gira ogni mattina alle 07:30 italiane.

Ricostruisce il sito: il generatore legge la deadline dalla didascalia di ogni
card e, se e passata, sposta la call dalla home e dalla sezione open call
all'archivio, che e gia ordinato per data decrescente.

Pubblica su Netlify **solo se qualcosa e cambiato davvero**, per non fare
deploy a vuoto ogni giorno.

## Cosa serve

Un unico segreto nel repository, in Settings -> Secrets and variables -> Actions:

| Segreto | Dove prenderlo |
|---|---|
| `NETLIFY_AUTH_TOKEN` | Netlify -> User settings -> Applications -> Personal access tokens |

## Lanciarlo a mano

Tab **Actions** -> *Aggiorna le call scadute* -> **Run workflow**.
