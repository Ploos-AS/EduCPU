# 07 — Aritmetikk, FLAGS og hopp

## Læringsmål

Etter denne leksjonen skal du kunne forklare hvordan aritmetikk oppdaterer FLAGS, bruke Z/N/C/V til å beskrive resultater, skille ADD/SUB fra CMP og følge betingede hopp gjennom et program.

## Aritmetikk endrer mer enn et register

I EduCPU produserer aritmetiske instruksjoner et 8-bits resultat og oppdaterer fire statusflagg:

| Flagg | Betydning |
| --- | --- |
| Z | resultatet er null |
| N | bit 7 i resultatet er satt |
| C | carry fra addisjon, eller ingen borrow ved subtraksjon |
| V | signed overflow |

Verdier lagres alltid som åtte bits, så aritmetikken wrapper modulo 256.

For eksempel gir `255 + 1` resultatet `0`. Resultatet alene mister informasjon om hva som skjedde; FLAGS bevarer nyttige egenskaper ved operasjonen.

> **Hvordan vet EduCPU det?**
>
> ALU-en produserer både resultatbitene og informasjon om betingelser. Instruksjonsdefinisjonen sier hvilke flaggbits som oppdateres. Et senere hopp tester disse lagrede bitene; CPU-en forstår ikke begreper som «lik» eller «overflow».

## ADD og subtraksjon

```asm
MOVI R0, 255
ADDI R0, 1
```

Etter addisjonen er R0 `0`, Z er satt og C er satt.

Ved subtraksjon bruker EduCPU C som **ingen borrow**. Dermed:

```asm
MOVI R0, 5
SUBI R0, 5
```

gir null med både Z og C satt.

Denne konvensjonen er viktig når vi leser resultatene fra subtraksjon og sammenligning.

## CMP: subtraksjon uten å beholde resultatet

`CMP` og `CMPI` oppdaterer FLAGS som om en subtraksjon hadde blitt utført, men lagrer ikke subtraksjonsresultatet.

```asm
MOVI R0, 10
CMPI R0, 10
JZ equal
```

R0 forblir 10. Z blir satt fordi sammenligningsresultatet ville vært null.

Dermed kan programmet stille et spørsmål om to verdier uten å ødelegge noen av dem.

## Betingede hopp

EduCPU ISA v0 har:

| Instruksjon | Betingelse |
| --- | --- |
| JZ | Z = 1 |
| JNZ | Z = 0 |
| JC | C = 1 |
| JNC | C = 0 |
| JN | N = 1 |
| JP | N = 0 |

`JMP` er ubetinget.

Et hopp erstatter enten PC med den kodede måladressen, eller lar kjøringen fortsette på neste instruksjon.

## Gjennomgått eksempel

```asm
MOVI R0, 3
loop:
    SUBI R0, 1
    JNZ loop
HALT
```

Hver subtraksjon oppdaterer Z. Så lenge R0 ikke er null, legger `JNZ` adressen til `loop` i PC. Når R0 blir null, blir Z=1 og hoppet tas ikke.

Den samme mekanismen gir oss løkker, valg og etter hvert høynivå-konstruksjoner som `if` og `while`.

## Kjør og observer

Den CI-testede fixturen er `course/examples/lesson07-flags-branches.eduasm`.

Forutsi R0, R1 og FLAGS ved hver aritmetiske instruksjon eller sammenligning, og forutsi om hvert hopp blir tatt. Kjør deretter programmet steg for steg.

## Unsigned og signed tolkning

CPU-en lagrer bare bitmønstre. Den samme byten kan tolkes forskjellig av programmereren.

`0xFF` kan representere unsigned 255 eller signed -1 med two's-complement-tolkning. N registrerer bare om bit 7 er satt. V registrerer signed overflow ved aritmetikk.

Flaggene erklærer ikke at en verdi «er signed» eller «er unsigned». Instruksjonssekvensen avgjør hvordan programmet tolker dem.

## Oppgaver

### Forståelse

1. Hva gjør at Z blir 1?
2. Hva betyr C etter en EduCPU-subtraksjon?
3. Endrer CMP registeroperandene?
4. Hva tester JNZ?
5. Hvorfor kan `255 + 1` gi null i et 8-bits register?

### Praktisk

Skriv en løkke som teller R0 fra 4 ned til 0. Forutsi nøyaktig hvor mange ganger det betingede hoppet tas før du kjører programmet.

Skriv deretter en sammenligning som velger mellom to veier ved hjelp av `CMPI` og `JZ`.

### Utforsk selv

Prøv addisjoner rundt `0x7F`, `0x80`, `0xFF` og `0x00`. Registrer Z, N, C og V.

Finn tilfeller der C og V er forskjellige. Forklar hvorfor de beskriver ulike tolkninger av de samme åtte resultatbitene.

## Sjekk forståelsen

Fullfør kjeden:

```text
aritmetikk → FLAGS → betinget hopp → PC → neste instruksjon
```

Hvilken del av kjeden gjør et valg på høyt nivå mulig uten at CPU-en forstår betydningen av programmet?

## Neste

Neste leksjon introduserer **stacken**: en disiplinert bruk av minnet styrt av SP som lar programmer lagre verdier midlertidig og senere støtte funksjonskall.
