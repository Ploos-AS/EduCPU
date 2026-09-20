# 13 — Objektfiler, relocations og linking

## Læringsmål

Etter denne leksjonen skal du kunne forklare hvorfor separat assemblerte kodebiter ikke alltid kjenner endelige adresser, lese de viktigste delene av en EduCPU-objektfil, forklare en `abs16le` relocation og beskrive hvordan linkeren løser et importert symbol.

## Adresseproblemet

Anta at én fil inneholder:

```asm
.export main
.import add_two

main:
    MOVI R0, 40
    CALL add_two
    HALT
```

og en annen:

```asm
.export add_two

add_two:
    ADDI R0, 2
    RET
```

Assembleren kan kode de fleste instruksjonene med en gang. Men mens den assemblerer den første filen vet den ennå ikke hvor `add_two` vil ligge i det ferdige programmet.

Det uløste spørsmålet må bevares.

## Objektfiler

EduASM kan produsere en EduCPU-objektfil i stedet for en ferdig binærfil.

v0-formatet lagrer blant annet:

- kodede data-bytes;
- eksporterte symboler;
- lokale symboler;
- importerte symboler;
- relocations.

En forenklet objektfil ser slik ut:

```json
{
  "format": "educpu-object-v0",
  "data": "...",
  "exports": {"main": 0},
  "imports": ["add_two"],
  "relocations": [
    {"offset": 4, "type": "abs16le", "symbol": "add_two"}
  ]
}
```

Den nøyaktige offseten avhenger av det kodede programmet. Hovedideen er at objektfilen sier:

> disse bytene trenger den endelige adressen til `add_two`.

## Exports og imports

En **export** gjør et symbol tilgjengelig for andre objekter.

En **import** erklærer at objektet trenger et symbol som leveres et annet sted.

Linkeren kobler de to sammen.

```text
main.eo                         math.eo
-------                         -------
imports add_two  ─────────────► exports add_two
exports main
```

Dermed kan filene assembleres uavhengig av hverandre.

## Relocations

En relocation beskriver et sted som må patches når den endelige adressen er kjent.

EduCPU v0 støtter relocation-typen `abs16le` for en 16-bits absolutt adresse lagret little-endian.

Hvis linkeren til slutt plasserer `add_two` på adresse `0x0010`, blir adressebytene:

```text
10 00
```

Low byte først, akkurat som ISA-kodingen krever.

> **Hvordan vet EduCPU at disse bytene en gang refererte til et symbol kalt `add_two`?**
>
> Det gjør den ikke. Symbolnavn og relocations er toolchain-begreper. Før kjøring har linkeren erstattet den uløste referansen med numeriske adressebytes. CPU-en ser bare den ferdige CALL-operanden.

## Hva linkeren gjør

For det enkle v0-formatet gjør linkeren følgende:

1. legger objektdata ut i det ferdige bildet;
2. beregner baseadressen til hvert objekt;
3. lager de endelige symboladressene;
4. løser lokale og importerte referanser;
5. anvender relocations;
6. skriver de endelige bytene.

Etter linking inneholder `CALL add_two` en konkret 16-bits adresse.

## Gjennomgått eksempel

Denne leksjonen bruker to CI-testede fixtures:

`course/examples/lesson13-main.eduasm`

```asm
.export main
.import add_two

main:
    MOVI R0, 40
    CALL add_two
    HALT
```

og `course/examples/lesson13-math.eduasm`

```asm
.export add_two

add_two:
    ADDI R0, 2
    RET
```

De assembleres uavhengig til to objekter.

Testen verifiserer at main-objektet inneholder en uløst `add_two`-import og relocation. Deretter linker den begge objektene, kontrollerer den løste symboladressen og kjører `main` på referanse-CPU-en.

Sluttresultatet er 42.

## Før og etter linking

Før linking:

```text
CALL add_two
     ^ symbolsk referanse
```

Objektfil:

```text
instruksjonsbytes + relocation("add_two")
```

Etter linking:

```text
CALL 0x....
     ^ numerisk adresse
```

Ved runtime gjøres ingen linker-oppslag. CPU-en følger adressen som allerede er kodet.

## Hvorfor separat kompilering er nyttig

Separate objekter gjør at større programmer kan bygges av deler som er oversatt uavhengig av hverandre.

En compiler kan generere ett objekt mens et bibliotek leverer et annet. Bare linkeren trenger å vite hvordan alle delene passer sammen i det endelige adresserommet.

EduCPU-formatet er bevisst lite, men demonstrerer det samme grunnleggende problemet som objektformater og linkere løser på større systemer.

## Oppgaver

### Forståelse

1. Hvorfor kan ikke assembleren alltid vite den endelige adressen til et CALL-target?
2. Hva er forskjellen mellom export og import?
3. Hvilken informasjon bevarer en relocation?
4. Hva betyr `abs16le`?
5. Kjenner CPU-en symbolnavn ved runtime?

### Praktisk

Legg til enda en eksportert funksjon i math-objektet og kall den fra main-objektet.

Før linking, forutsi hvilket objekt som får importen og hvor en ny relocation trengs.

### Utforsk selv

Bytt rekkefølgen på de to objektene som sendes til linkeren. Observer hvordan base- og symboladresser endrer seg mens programoppførselen forblir den samme.

Undersøk de endelige CALL-operandbytene og dekod little-endian target-adressen manuelt.

## Sjekk forståelsen

Fullfør kjeden:

```text
symbolsk CALL
→ objektbytes + ______
→ linker løser ______
→ numeriske adressebytes
→ CPU kjører CALL
```

Hvilken informasjon eksisterer bare under bygging?

## Linker-prediksjon

Før du kjører linkeren:

1. finn importen `add_two`;
2. finn relocationen som representerer den;
3. forutsi hvilket symbol som skal løse den;
4. forutsi at den ferdige CALL-operanden må være en numerisk little-endian-adresse.

Kjør deretter linkeren og kontroller hvert punkt. Dette skiller en **symbolsk byggereferanse** fra en **runtime-adresse**.

## Verktøy

Bruk den ekte kursfixturen: `course/examples/lesson13-main.eduasm + lesson13-math.eduasm`.

**EduGuide:** bruk dette verktøyet i observasjonsdelen.

Forutsi viktige endringer før du kjører fixturen, og sammenlign deretter med observasjonen.

## Neste

Neste leksjon setter alt sammen og følger **ett komplett program fra EduC-kildekode helt til kjøring**, med korrelasjon mellom kildekode, IR, generert assembly, bytes og CPU-tilstand.
