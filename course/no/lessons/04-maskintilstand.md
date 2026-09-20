# 04 — Maskintilstand

## Læringsmål

Etter denne leksjonen skal du kunne:

- forklare hva **maskintilstand** betyr;
- identifisere rollene til R0–R7, PC, SP, FLAGS og minnet;
- beskrive hvordan én instruksjon endrer én tilstand til en ny;
- skille CPU-registre fra minne;
- undersøke EduCPU på et nøyaktig tidspunkt under kjøring.

## Hva er det?

På ethvert tidspunkt har en CPU informasjon som beskriver hvor den er og hva den inneholder. Dette kaller vi maskinens **tilstand**.

For EduCPU omfatter den viktige arkitektoniske tilstanden:

- **R0–R7** — åtte generelle 8-bits registre;
- **PC** — den 16-bits programtelleren;
- **SP** — den 16-bits stackpekeren;
- **FLAGS** — et 8-bits statusregister;
- **minnet** — 65 536 byteplasser;
- om CPU-en er **halted** eller har gått inn i en **trap**.

Hvis vi kjenner hele tilstanden og maskinens regler, kan vi resonnere oss fram til hva neste instruksjon vil gjøre.

## Hvorfor trenger vi det?

Programmer virker ved å endre tilstand.

Se på:

```asm
MOVI R0, 10
ADDI R0, 5
HALT
```

Kildekoden beskriver operasjoner, men kjøringen er en sekvens med tilstandsendringer:

```text
R0 = 0
   ↓ MOVI R0,10
R0 = 10
   ↓ ADDI R0,5
R0 = 15
   ↓ HALT
halted = true
```

Debugging blir langt enklere når vi ikke bare tenker på kodelinjer, men spør:

**Hva var maskintilstanden før denne instruksjonen, og hva endret seg etterpå?**

## Hvordan gjør EduCPU det?

### R0–R7

Dette er generelle 8-bits registre. Hvert register lagrer én byte.

De kan inneholde tall, mellomresultater, adresser brukt av enkelte instruksjoner, funksjonsargumenter eller andre 8-bits mønstre programmet trenger.

### PC — programteller

PC er 16 bits og peker ut hvor instruksjonshentingen fortsetter.

Vanlig instruksjonshenting øker PC når instruksjons- og operandbytes leses. Branches, jumps, calls og returns kan endre den med vilje.

### SP — stackpeker

SP er 16 bits. Etter reset:

```text
SP = 0xFF00
```

Stacken vokser nedover mot lavere adresser. Vi studerer stacken grundig senere.

### FLAGS

De fire nederste flaggbitene i EduCPU er:

| Bit | Navn | Betydning |
| ---: | --- | --- |
| 0 | Z | zero |
| 1 | N | negative/høyeste bit satt |
| 2 | C | carry / ingen borrow ved subtraksjon |
| 3 | V | signed overflow |

Bit 4–7 er reserverte og leses som null i ISA v0.

Ikke alle instruksjoner endrer FLAGS. `MOVI` lar dem for eksempel være uendret, mens aritmetiske instruksjoner oppdaterer dem.

### Minne

EduCPU har et flatt 16-bits adresserom:

```text
0x0000 ... 0xFFFF
```

Det gir 65 536 byte-adresserbare plasser.

Programbytes og data kan begge ligge i dette adresserommet. Området `0xFF00–0xFFFF` er reservert for fremtidig I/O/systembruk, og reset setter SP til `0xFF00`.

> **Hvordan vet EduCPU det?**
>
> Den vedlikeholder ikke en menneskelig beskrivelse som «R0 er svaret». Den har arkitektoniske lagringsplasser med bitmønstre. Instruksjonene definerer hvilke plasser som leses, hvilke som skrives og hvordan PC og FLAGS endres.

## Gjennomgått eksempel

Vi bruker:

```asm
MOVI R0, 10
MOVI R1, 20
ADD R0, R1
HALT
```

Rett etter reset, før kjøring:

```text
R0 = 0
R1 = 0
PC = 0x0000
SP = 0xFF00
FLAGS = 0
halted = false
```

Etter `MOVI R0,10`:

```text
R0 = 10
PC = 0x0003
```

Etter `MOVI R1,20`:

```text
R1 = 20
PC = 0x0006
```

Etter `ADD R0,R1`:

```text
R0 = 30
R1 = 20
PC = 0x0009
FLAGS = 0
```

Etter `HALT`:

```text
PC = 0x000A
halted = true
```

Programmet kan dermed forstås som en sekvens med nøyaktig definerte tilstandsoverganger.

## Kjør og observer

Den CI-testede fixturen er:

`course/examples/lesson04-machine-state.eduasm`

Den lager med vilje flere synlige tilstandsendringer, blant annet et nullresultat slik at Z-flagget blir satt.

Før du kjører den, lag en tabell med én rad per instruksjon og kolonner for R0, R1, PC, SP og FLAGS.

Fyll først inn det du tror vil skje. Kjør deretter programmet steg for steg i EduCPU-simulatoren og sammenlign hver tilstand.

## Forklar resultatet

CPU-en kjører ikke et helt program som én konseptuell handling. Hver instruksjon omformer den nåværende arkitektoniske tilstanden til den neste.

Dette gir oss en kraftig måte å forstå datamaskiner på:

```text
nåværende tilstand + instruksjon → neste tilstand
```

Senere, når vi studerer branches, stack, funksjoner og kompilatorer, blir maskinen mer kompleks — men dette prinsippet forblir det samme.

## Oppgaver

### Forståelse

1. Hvor mange generelle registre har EduCPU?
2. Hvor mange bits er PC?
3. Hva er SP etter reset?
4. Hvilket flagg angir et nullresultat?
5. Endrer `MOVI` FLAGS?

### Praktisk

For:

```asm
MOVI R0, 5
MOVI R1, 5
SUB R0, R1
HALT
```

forutsi R0, R1, PC, SP og FLAGS etter hver instruksjon.

Kjør deretter programmet én instruksjon om gangen.

### Utforsk selv

Kjør et lite program og stopp etter hver instruksjon.

Skriv først bare ned de delene av tilstanden som endret seg. Gjenta deretter øvelsen og skriv ned hele den arkitektoniske tilstanden.

Hvilken framstilling gjør det enklest å oppdage endringer? Hvilken er best dersom du skal rekonstruere et nøyaktig tidspunkt i kjøringen?

## Sjekk forståelsen

1. Hva mener vi med maskintilstand?
2. Hvorfor er PC en del av tilstanden?
3. Er registre og minne det samme?
4. Hvilken tilstandsendring fører `HALT` til?
5. Fullfør ideen: nåværende tilstand + instruksjon → ______.

Løsningene oppbevares separat fra leksjonen.

## Neste

Nå kan vi beskrive maskinen på et nøyaktig tidspunkt. Dermed kan vi se nærmere på hva CPU-en faktisk leser fra minnet. Neste: **instruksjoner og maskinkode**.
