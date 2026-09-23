# Spostare theoasisproject.eu sul nuovo sito

Anteprima online: **https://oasis-project-eu.netlify.app**
Pannello: https://app.netlify.com/projects/oasis-project-eu

La posta del progetto (`info@theoasisproject.eu`) resta dov'è: **su Hostinger**.
I nameserver non si toccano, quindi MX, SPF e DKIM restano al loro posto e la
casella non può smettere di funzionare. Si cambia solo *dove punta il sito*.

---

## 1. Prima di iniziare — controlla l'anteprima

Apri https://oasis-project-eu.netlify.app e verifica con calma:

- le 28 pagine, il menu, il filtro per paese nelle Calls
- un invio di prova dal form contatti (deve arrivarti a info@theoasisproject.eu)
- il sito su telefono

Finché non tocchi il DNS, **il sito vecchio resta online e visibile a tutti**.
Non c'è fretta e non c'è rischio.

## 2. Aggancia il dominio su Netlify

Netlify deve sapere che risponderà anche per quel dominio, *prima* che il DNS
lo mandi lì. Pannello → **Domain management → Add a domain** →
`theoasisproject.eu`. Netlify dirà che il dominio non punta ancora a lui: è
normale, è esattamente il passo successivo.

## 3. Cambia i record nel DNS di Hostinger

hPanel → il dominio → **DNS / Nameservers → Gestisci record DNS**.
Non stai cambiando i nameserver: stai modificando singoli record.

### Da modificare

| Tipo | Nome | Valore nuovo | Nota |
|---|---|---|---|
| A | `@` | `75.2.60.5` | sostituisce gli A attuali di Hostinger |
| AAAA | `@` | **eliminare** | vedi avvertenza sotto |
| CNAME | `www` | `oasis-project-eu.netlify.app` | sostituisce il CNAME al CDN Hostinger |

> **L'errore che rovina la migrazione.** Il dominio ha anche record **AAAA**
> (IPv6) che puntano a Hostinger. Se cambi solo il record A, chi naviga in IPv6
> continua a vedere il **sito vecchio**, mentre tu dal tuo computer vedi quello
> nuovo. È il classico guasto che fa perdere giorni. Gli AAAA vanno eliminati.

### Da NON toccare, per nessun motivo

| Tipo | Valore | Perché |
|---|---|---|
| MX | `mx1.hostinger.com` (5), `mx2.hostinger.com` (10) | è la posta del progetto |
| TXT | `v=spf1 include:_spf.mail.hostinger.com ~all` | senza, le tue mail finiscono in spam |
| TXT | `google-site-verification=...` | verifica Search Console |
| CNAME | qualsiasi `..._domainkey...` | firma DKIM della posta |

Se il pannello propone di "spostare i nameserver" o di "usare il DNS di
Netlify": **rifiuta**. È esattamente la strada che spegne la posta.

## 4. Aspetta e verifica

La propagazione richiede da pochi minuti a qualche ora. Poi:

```bash
./verify-migration.sh
```

Lo script controlla che il sito risponda da Netlify, che il certificato HTTPS
sia attivo, e — soprattutto — **che MX e SPF siano ancora intatti**.

Netlify emette da solo il certificato Let's Encrypt quando vede il dominio
puntato. Se dopo un'ora HTTPS non funziona: Domain management → HTTPS →
**Verify DNS configuration** → **Renew certificate**.

## 5. Se qualcosa va storto

Rimetti nel DNS di Hostinger i record A/AAAA/CNAME originali (hPanel ha un
pulsante per ripristinare i record di default dell'hosting). Il sito vecchio
è ancora sul loro server, torna su in pochi minuti. La posta non si è mai
fermata, quindi non c'è nulla da recuperare.

Lo stato del DNS prima della migrazione è salvato in `dns-before.txt`.

---

## Dopo la migrazione

- **Disdetta Hostinger**: aspetta almeno due settimane prima di disattivare il
  piano hosting, e assicurati che il piano **email** resti attivo — sono due
  servizi distinti e la casella dipende dal secondo.
- **Le candidature** arrivano via mail e restano anche nel pannello Netlify,
  sotto Forms. Il piano gratuito copre 100 invii al mese: se una open call ne
  porta di più, si passa al livello a pagamento o si sposta il modulo su un
  servizio dedicato.
- **Aggiornare il sito**: `./oasis ...` per il contenuto, poi
  `python3 build.py` e `npx netlify-cli deploy --dir=site --prod`.
