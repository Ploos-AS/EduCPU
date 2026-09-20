# 06 — EduASM og hva en assembler gjør

## Læringsmål

Etter denne leksjonen skal du kunne:

- forklare hvorfor assembly finnes;
- skrive enkle EduASM-instruksjoner;
- bruke registre, tallverdier, kommentarer og labels;
- forklare hvorfor labels krever at assembleren beregner adresser;
- beskrive grunnideen i en to-pass assembler.

## Hva er assembly?

Maskinkode passer perfekt for CPU-en, men er upraktisk for mennesker. Assembly gir lesbare navn til operasjonene og operandene som kodes i disse bytene.

I stedet for:

```text
11 00 2A
```

kan vi skrive:

```asm
MOVI R0, 42
```

EduASM er assembly-språket og assembleren som brukes med EduCPU.

## Hvorfor trenger vi en assembler?

CPU-en trenger fortsatt maskinbytes. En **assembler** oversetter assembly-kildekode til disse bytene.

Den løser også oppgaver som ellers ville vært kjedelige og feilutsatte. Det viktigste eksemplet er en **label**.

I stedet for å beregne adressen til en løkke manuelt:

```asm
JNZ 0x0006
```

kan vi gi stedet et navn:

```asm
loop:
    SUBI R0, 1
    JNZ loop
```

Assembleren beregner adressen for oss.

## Grunnleggende EduASM

### Instruksjoner og registre

```asm
MOVI R0, 42
MOV R1, R0
ADD R0, R1
HALT
```

EduCPU har R0–R7.

### Tallformater

EduASM godtar flere skrivemåter for samme verdi:

```asm
MOVI R0, 42
MOVI R1, 0x2A
MOVI R2, $2A
MOVI R3, 0b00101010
```

Alle fire immediate-verdiene representerer samme byte.

### Kommentarer

Kommentarer kan starte med `;` eller `#`:

```asm
MOVI R0, 3      ; løkketeller
# Dette er også en kommentar
```

Kommentarer er for mennesker. De produserer ingen maskinkodebytes.

### Labels

En label gir en adresse et navn:

```asm
again:
    SUBI R0, 1
    JNZ again
```

Navnet `again` finnes ikke i CPU-en. EduASM erstatter det med riktig adresse når programmet assembleres.

> **Hvordan vet EduCPU det?**
>
> Den kjenner ikke labels, kommentarer eller skrivemåten `R0`. Dette er hjelpemidler i assembly-språket. Når CPU-en mottar programmet, har EduASM oversatt dem til instruksjonsbytes, registernumre og adresser.

## Hvorfor to pass?

Se på:

```asm
JMP later
MOVI R0, 99
later:
HALT
```

Når assembleren leser `JMP later`, har den ennå ikke sett `later:`.

Dette kalles en **forward reference**.

EduASM løser dette med to konseptuelle pass:

1. **Pass 1:** finn instruksjonsstørrelser og samle label-adresser.
2. **Pass 2:** kod instruksjonene når label-adressene er kjent.

For eksemplet over:

```text
0x0000  JMP later       3 bytes
0x0003  MOVI R0,99      3 bytes
0x0006  later: HALT     1 byte
```

Dermed betyr `later` adresse `0x0006`, og hoppet kan kodes riktig.

## Gjennomgått eksempel

Leksjonsfixturen inneholder:

```asm
MOVI R0, 3
loop:
    SUBI R0, 1
    JNZ loop
HALT
```

Før du assemblerer den, beregn:

1. adressen til `loop`;
2. bytene for `MOVI R0,3`;
3. adressen som kodes av `JNZ loop`;
4. sluttverdien til R0.

Sammenlign deretter med EduASM og referanse-CPU-en.

## Kjør og observer

Den CI-testede fixturen er:

`course/examples/lesson06-eduasm.eduasm`

Testene verifiserer både de assemblerte bytene og kjøringsresultatet. Dermed kontrolleres leksjonens forklaring av labels mot den virkelige assembleren.

EduASM kan også produsere en listing. Den er nyttig fordi den viser kildeinstruksjonene sammen med adresser og kodede bytes.

## Forklar resultatet

Assembly er en representasjon for mennesker som fortsatt ligger nær maskinen.

En label viser dette spesielt tydelig:

```text
menneskelig idé:  loop
assembler:        beregn adressen
maskinkode:       kodet 16-bits adresse
CPU:              legg adressen i PC når hoppet tas
```

Hvert lag fjerner litt bekvemmelighet helt til bare arkitektonisk tilstand og bytes står igjen.

## Oppgaver

### Forståelse

1. Hvorfor er assembly enklere for mennesker enn rå maskinkode?
2. Lager en kommentar noen maskinkodebytes?
3. Kjenner CPU-en navnet på en label?
4. Hva er en forward reference?
5. Hvorfor bruker EduASM to pass?

### Praktisk

Skriv et EduASM-program som:

1. legger 5 i R0;
2. trekker fra 1 gjentatte ganger;
3. stopper løkken når R0 blir null;
4. halter.

Forutsi label-adressen og de assemblerte branch-bytene før du kjører assembleren.

### Utforsk selv

Endre antallet instruksjoner før en label.

Forutsi hvordan adressen endres. Assembler deretter på nytt og undersøk listingen.

Legg merke til at navnet i kildekoden er det samme selv om maskinadressen endres.

## Sjekk forståelsen

1. Hva produserer en assembler?
2. Hvilke registernavn er gyldige i EduASM?
3. Nevn tre måter å skrive desimaltallet 42 som literal.
4. Hva skjer med labels under assemblering?
5. I hvilket pass kan adressen til en forward label først være kjent?

Løsningene oppbevares separat fra leksjonen.


## Verktøy

Bruk den ekte kursfixturen: `course/examples/lesson06-eduasm.eduasm`.

**EduVis:** bruk nettleservisualiseringen for å stege gjennom CPU-tilstanden. **eduguide:** bruk den guidede PREDICT → OBSERVE → EXPLAIN-flyten.

Forvent viktige tilstands- eller compiler-endringer før du kjører fixturen, og sammenlign deretter med resultatet.

## Neste

Nå kan vi skrive lesbare programmer nær maskinnivået. Neste leksjon handler om **aritmetikk, FLAGS og branches**, der CPU-en begynner å ta valg basert på tidligere resultater.
