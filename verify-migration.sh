#!/usr/bin/env bash
# Controlla che il dominio sia passato a Netlify E che la posta sia intatta.
set -u
D=theoasisproject.eu
echo "== Dove punta il sito =="
A=$(dig +short A $D | tr '\n' ' ')
AAAA=$(dig +short AAAA $D | tr '\n' ' ')
echo "  A     : ${A:-nessuno}"
echo "  AAAA  : ${AAAA:-nessuno}"
case "$A" in *75.2.60.5*) echo "  -> OK: punta a Netlify";;
             *) echo "  -> non ancora su Netlify (o DNS non propagato)";; esac
[ -n "${AAAA// }" ] && echo "  !! ATTENZIONE: ci sono ancora record AAAA: chi naviga in IPv6 vede il SITO VECCHIO"

echo "== La posta (non deve essere cambiata) =="
MX=$(dig +short MX $D | sort | tr '\n' ' ')
SPF=$(dig +short TXT $D | grep -c 'v=spf1' || true)
echo "  MX    : ${MX:-NESSUNO}"
case "$MX" in *hostinger*) echo "  -> OK: la casella e ancora servita da Hostinger";;
             *) echo "  !! ALLARME: gli MX non puntano piu a Hostinger. LA POSTA E GIU.";; esac
[ "$SPF" -ge 1 ] && echo "  -> OK: SPF presente" || echo "  !! ALLARME: SPF sparito, le mail in uscita finiranno in spam"

echo "== HTTPS e contenuto =="
for u in "https://$D/" "https://www.$D/" "https://$D/cc-second-call"; do
  printf "  %-46s %s\n" "$u" "$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 "$u" 2>/dev/null || echo ERR)"
done
SERVER=$(curl -sI --max-time 15 "https://$D/" 2>/dev/null | grep -i '^server:' | tr -d '\r')
echo "  ${SERVER:-server sconosciuto}"
