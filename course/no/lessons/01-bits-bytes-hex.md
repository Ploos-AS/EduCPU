# 01 — Bits, bytes, binært og heksadesimalt

## Læringsmål

Etter denne leksjonen skal du kunne:

- forklare hva en bit og en byte er;
- lese et 8-bits binært tall;
- konvertere små verdier mellom binært, desimalt og heksadesimalt;
- forklare hvorfor heksadesimale tall er nyttige når vi arbeider med datamaskiner;
- knytte en 8-bits verdi til EduCPU-registre og minne.

## Hva er det?

En datamaskin lagrer informasjon ved hjelp av **bits**. En bit har bare to mulige verdier: `0` eller `1`.

Åtte bits danner en **byte**. EduCPU har en 8-bits datapath, og de generelle registrene R0–R7 lagrer én byte hver. En 8-bits byte har 256 mulige bitmønstre, fra `00000000` til `11111111`.

Det samme bitmønsteret kan skrives med forskjellige tallsystemer:

| Binært | Desimalt | Heksadesimalt |
| --- | ---: | ---: |
| `00000000` | 0 | `0x00` |
| `00000001` | 1 | `0x01` |
| `00001010` | 10 | `0x0A` |
| `00101010` | 42 | `0x2A` |
| `11111111` | 255 | `0xFF` |

Dette er ikke forskjellige verdier. Det er forskjellige måter å skrive den samme verdien på.

## Hvorfor trenger vi det?

Binært viser de enkelte bitene tydelig, men lange binære tall er vanskelige for mennesker å lese. Desimalt er kjent, men passer ikke like naturlig sammen med grupper av bits.

Heksadesimalt bruker seksten sifre: `0`–`9` og `A`–`F`. Ett heksadesimalt siffer representerer nøyaktig fire bits. Dermed kan én byte alltid skrives med nøyaktig to heksadesimale sifre.

For eksempel:

```text
0010 1010
  2    A
   0x2A
```

Derfor er heksadesimale tall spesielt praktiske for maskinkode, minneadresser og registerverdier.

## Hvordan gjør EduCPU det?

EduCPU vet ikke om du tenkte på en verdi som binær, desimal eller heksadesimal. Inne i maskinen er verdien bare et mønster av bits.

Når R0 inneholder `00101010`, kan en debugger vise mønsteret som desimalt `42` eller heksadesimalt `0x2A`. Bitene i R0 har ikke forandret seg.

> **Hvordan vet EduCPU det?**
>
> Den vet ikke at `42`, `0x2A` og `00101010` er tre menneskelige representasjoner av samme tall. EduCPU har bare de åtte lagrede bitene. Assembleren, simulatoren og visualiseringsverktøyet velger nyttige representasjoner for oss.

## Gjennomgått eksempel

Se på denne binære byten:

```text
00101010
```

Posisjonene i en 8-bits verdi representerer toerpotenser:

```text
128 64 32 16  8  4  2  1
 0   0  1  0  1  0  1  0
```

Bitene som er satt gir:

```text
32 + 8 + 2 = 42
```

Deler vi samme byte i grupper på fire:

```text
0010 1010
```

er `0010` heksadesimalt `2`, mens `1010` er heksadesimalt `A`. Dermed:

```text
00101010 = 42 = 0x2A
```

## Kjør og observer

EduASM godtar flere tallformater. Disse instruksjonene laster alle den samme verdien inn i R0:

```asm
MOVI R0, 42
MOVI R0, 0x2A
MOVI R0, 0b00101010
```

Prøv hver form separat i et lite program som avsluttes med `HALT`. Repoet inneholder også den CI-testede fixturen `course/examples/lesson01-number-formats.eduasm`, som laster de tre skrivemåtene inn i R0, R1 og R2. Før du assemblerer programmet, forutsi hvilken byteverdi R0 vil inneholde.

Se deretter på de assemblerte bytene og CPU-tilstanden med EduCPU-verktøyene. Notasjonen i kildekoden endres, men verdien som lastes inn i R0 er identisk.

## Forklar resultatet

Assembleren oversetter den menneskevennlige tallverdien til en 8-bits verdi. Når CPU-en utfører `MOVI`, finnes ikke lenger den opprinnelige skrivemåten.

Dette er vårt første eksempel på et viktig tema i kurset: **menneskevennlig notasjon oversettes til enklere maskininformasjon**.

## Oppgaver

### Forståelse

1. Hvor mange forskjellige verdier kan åtte bits representere?
2. Konverter `00001111` til desimalt og heksadesimalt.
3. Konverter desimalt `42` til binært og heksadesimalt.
4. Konverter `0xFF` til desimalt og binært.
5. Hvorfor er heksadesimale tall praktiske når vi undersøker bytes?

### Praktisk

Skriv følgende verdier binært, desimalt og heksadesimalt:

- 0
- 1
- 16
- 42
- 127
- 128
- 255

Skriv deretter tre EduASM-`MOVI`-instruksjoner som alle laster desimalverdien 42 inn i R3, med henholdsvis desimal, heksadesimal og binær notasjon.

### Utforsk selv

Lag tre minimale EduASM-programmer som bare skiller seg fra hverandre i hvordan verdien 42 er skrevet.

Før du assemblerer dem, forutsi:

1. om R0 vil være forskjellig etter kjøring;
2. om immediate-verdien i den genererte maskinkoden vil være forskjellig.

Assembler og kjør programmene. Sammenlign resultatet med det du forutsa.

## Sjekk forståelsen

1. Hva er den minste informasjonsenheten vi har introdusert?
2. Hvor mange bits er det i et generelt EduCPU-register?
3. Hvilken heksadesimal verdi tilsvarer binært `11110000`?
4. Husker CPU-en om en verdi ble skrevet desimalt eller heksadesimalt i kildekoden?

Løsningene oppbevares separat fra leksjonen.

## Neste

Bits blir langt mer interessante når maskinvare kan **lagre, kombinere og endre** dem. Neste leksjon introduserer logikk og lagring og gir oss byggesteinene vi trenger for å forstå hva en CPU faktisk er.
