# 02 — Logikk og lagring av informasjon

## Læringsmål

Etter denne leksjonen skal du kunne:

- forklare grunnideen bak NOT, AND, OR og XOR;
- skille mellom kombinatorisk logikk og lagret tilstand;
- forklare hvorfor en CPU trenger registre og minne;
- bruke EduCPUs logiske instruksjoner og observere resultatene;
- beskrive hvorfor et bitmønster først får mening gjennom hvordan det brukes.

## Hva er det?

Bits blir nyttige når en maskin kan **endre** og **huske** dem.

Logiske operasjoner endrer bitmønstre. Fire viktige operasjoner er:

| A | B | A AND B | A OR B | A XOR B |
| - | - | ------- | ------ | ------- |
| 0 | 0 | 0 | 0 | 0 |
| 0 | 1 | 0 | 1 | 1 |
| 1 | 0 | 0 | 1 | 1 |
| 1 | 1 | 1 | 1 | 0 |

**NOT** bruker én inngang og snur den: 0 blir 1 og 1 blir 0.

Disse reglene brukes uavhengig på hver bit i en byte.

En maskin trenger også **tilstand**: informasjon som fortsatt finnes etter at den aktuelle operasjonen er ferdig. Registre og minne gir oss slik tilstand.

## Hvorfor trenger vi det?

En krets som bare beregner et resultat fra inngangene den har akkurat nå, kan ikke huske hva som skjedde tidligere. En nyttig datamaskin må kunne beholde instruksjoner, data og mellomresultater.

Vi får dermed to viktige ideer:

- **logikk** endrer informasjon;
- **lagring** beholder informasjon.

En CPU kombinerer begge.

## Hvordan gjør EduCPU det?

EduCPU har åtte generelle 8-bits registre, R0–R7, og 64 KiB byte-adresserbart minne.

ISA-en inneholder `AND`, `OR`, `XOR` og `NOT`. For operasjonene med to registre erstatter resultatet innholdet i det første registeret.

For eksempel:

```asm
MOVI R0, 0b11001100
MOVI R1, 0b10101010
AND R0, R1
HALT
```

Etter `AND` inneholder R0 `10001000`.

> **Hvordan vet EduCPU det?**
>
> Den vet ikke om bitene representerer et tall, en maske, tegn eller noe annet. Instruksjonsdekoderen forteller CPU-en hvilken operasjon som skal utføres. ALU-en utfører operasjonen på bitmønstrene, og et register lagrer resultatet.

## Gjennomgått eksempel

Vi starter med:

```text
R0 = 11001100
R1 = 10101010
```

For AND blir en resultatbit 1 bare når begge inngangsbitene er 1:

```text
  11001100
& 10101010
----------
  10001000
```

De samme inngangene gir forskjellige resultater med forskjellige operasjoner:

```text
AND = 10001000 = 0x88
 OR = 11101110 = 0xEE
XOR = 01100110 = 0x66
```

Og:

```text
NOT 11001100 = 00110011 = 0x33
```

## Kjør og observer

Repoet inneholder den CI-testede fixturen:

`course/examples/lesson02-logic.eduasm`

Den beregner AND, OR, XOR og NOT med ekte EduCPU-instruksjoner. Før du kjører den, beregn forventede registerverdier selv.

Assembler og kjør deretter programmet med EduCPU-verktøyene og sammenlign maskintilstanden med det du forutsa.

## Forklar resultatet

Verdiene som legges i registrene blir der til en senere instruksjon endrer dem. Denne varigheten er **tilstand**.

Den logiske instruksjonen husker ikke inngangene permanent. Den beregner et nytt bitmønster. Et målregister lagrer resultatet.

Forskjellen mellom **å gjøre noe** og **å huske noe** er en av grunnidéene vi trenger før vi bygger en mental modell av en CPU.

## Oppgaver

### Forståelse

1. Hva er `1 AND 0`?
2. Hva er `1 OR 0`?
3. Hva er `1 XOR 1`?
4. Hva gjør NOT med en bit?
5. Hvorfor trenger en datamaskin lagring?

### Praktisk

Beregn dette uten å kjøre simulatoren:

1. `10101010 AND 11110000`
2. `10101010 OR 00001111`
3. `10101010 XOR 11111111`
4. `NOT 00001111`

Skriv deretter EduASM som utfører hver operasjon.

### Utforsk selv

Velg to byteverdier og legg dem i R0 og R1.

Forutsi resultatene av AND, OR og XOR. Kjør hver operasjon og sammenlign det du forutsa med den observerte tilstanden.

Still så et annet spørsmål: Kan du se på de endelige bitene alene om de var ment som et tall eller som en bitmaske?

## Sjekk forståelsen

1. Hva er forskjellen mellom logikk og tilstand?
2. Hvor kan EduCPU lagre en 8-bits mellomverdi?
3. Hvilken operasjon gir 1 når de to inngangsbitene er forskjellige?
4. Må en ALU forstå den menneskelige betydningen av bitene den behandler?

Løsningene oppbevares separat fra leksjonen.

## Neste

Vi har nå bits, operasjoner på bits og steder som kan huske bits. I neste leksjon kombinerer vi disse ideene og svarer på et sentralt spørsmål: **Hva er en CPU?**
