# 05 — Instruksjoner og maskinkode

## Læringsmål

Etter denne leksjonen skal du kunne:

- skille en assembly-instruksjon fra maskinkodebytene dens;
- identifisere opcodes og operander i enkle EduCPU-instruksjoner;
- forklare hvorfor EduCPU-instruksjoner har forskjellig lengde;
- dekode enkle instruksjonsbytes ved hjelp av ISA-en;
- forklare hvordan EduCPU lagrer en 16-bits adresse i little-endian-rekkefølge.

## Hva er det?

CPU-en kjører ikke assembly-tekst. Den kjører **maskinkode**: bytes der bitmønstrene har betydninger definert av instruction set architecture, eller ISA.

Assembly gir mennesker lesbare navn på disse instruksjonene.

For eksempel:

```asm
MOVI R0, 42
```

kodes av EduASM som:

```text
11 00 2A
```

Den første byten er **opcoden**. Den velger operasjonen. De neste bytene er **operander**, kodet i formatet som denne opcoden krever.

## Hvorfor trenger vi det?

En CPU trenger en entydig representasjon som kan lagres i minnet og hentes som bytes.

Mennesker foretrekker:

```asm
ADD R0, R1
```

EduCPU kjører:

```text
20 00 01
```

Assembleren er broen mellom disse to representasjonene.

Når vi forstår denne broen forsvinner enda et lag med tilsynelatende magi: CPU-en forstår ikke assembly-programmet direkte.

## Hvordan gjør EduCPU det?

EduCPU ISA v0 bruker en opcode på én byte etterfulgt av null eller flere operandbytes.

Eksempler:

| Assembly | Bytes | Lengde |
| --- | --- | ---: |
| `NOP` | `00` | 1 |
| `HALT` | `01` | 1 |
| `MOVI R0,42` | `11 00 2A` | 3 |
| `ADD R0,R1` | `20 00 01` | 3 |
| `NOT R3` | `2B 03` | 2 |
| `JMP 0x1234` | `30 34 12` | 3 |

Registeroperander bruker en hel byte. R0 til R7 kodes som `00` til `07`.

### 16-bits adresser og little endian

EduCPU-adresser er 16 bits. Adresseoperander lagres med **lav byte først og høy byte etterpå**.

For adressen:

```text
0x1234
```

er de to adressebytene:

```text
34 12
```

Dermed blir:

```asm
JMP 0x1234
```

til:

```text
30 34 12
```

Denne byterekkefølgen kalles **little endian**.

> **Hvordan vet EduCPU det?**
>
> Den gjetter ikke hvor en instruksjon slutter. Opcoden bestemmer instruksjonsformatet. Når dekoderen ser `0x11`, sier ISA-en at det følger en registerbyte og en 8-bits immediate-byte. Når den ser `0x01`, vet den at HALT ikke har operander.

## Gjennomgått eksempel

Se på:

```asm
MOVI R0, 42
MOVI R1, 1
ADD R0, R1
HALT
```

Bytene er:

```text
Adresse   Bytes       Betydning
0000      11 00 2A    MOVI R0,42
0003      11 01 01    MOVI R1,1
0006      20 00 01    ADD R0,R1
0009      01          HALT
```

Legg merke til hvordan instruksjonsadressene følger av instruksjonslengdene.

Etter at alle tre bytene i den første instruksjonen er hentet, har PC gått fra `0x0000` til `0x0003`.

Maskinkode er dermed både **data som ligger i minnet** og **en sekvens som tolkes etter reglene i ISA-en**.

## Kjør og observer

Den CI-testede fixturen er:

`course/examples/lesson05-machine-code.eduasm`

Testen kontrollerer den eksakte assemblerte bytesekvensen, ikke bare CPU-ens sluttresultat.

Før du assemblerer den, skriv ned bytene du forventer. Sammenlign deretter med resultatet fra EduASM.

## Forklar resultatet

Navn som `MOVI`, `R0` og `JMP` finnes for programmereren. Under kjøring ser CPU-en kodede felt.

For et gyldig program er begge sider enige fordi assembleren og CPU-en implementerer den samme ISA-spesifikasjonen.

Derfor er ISA-en en kontrakt: Den definerer hva hvert kodet mønster betyr.

## Oppgaver

### Forståelse

1. Hva er en opcode?
2. Kjører EduCPU teksten `ADD`?
3. Hvordan kodes R5 som registeroperand?
4. Hvorfor kan to instruksjoner ha forskjellig lengde?
5. Hva betyr little endian for en 16-bits EduCPU-adresse?

### Praktisk

Kod disse for hånd ved hjelp av ISA-dokumentasjonen:

```asm
HALT
MOVI R3, 0x7F
NOT R3
ADD R2, R5
JMP 0x1234
```

Assembler dem deretter og sammenlign bytene.

### Utforsk selv

Ta et gyldig assemblert program og finn instruksjonsgrensene bare ved hjelp av maskinbytene og ISA-tabellen.

Endre deretter én opcode-byte. Dekod den nye bytesekvensen før du kjører den.

Vær oppmerksom på at en endret opcode også kan endre hvordan de etterfølgende bytene tolkes.

## Sjekk forståelsen

1. Hva kobler assembly-syntaks til maskinkodebytes?
2. Hvilken byte koder EduCPU `HALT`?
3. Hvor mange bytes bruker `MOVI R0,42`?
4. Hvordan lagres adressen `0x1234` i en adresseoperand?
5. Hvordan vet dekoderen hvor mange operandbytes den skal lese?

Løsningene oppbevares separat fra leksjonen.

## Neste

Maskinkode er presist, men upraktisk for mennesker. I neste leksjon går vi ett lag opp igjen og studerer **EduASM og hva en assembler gjør**.
