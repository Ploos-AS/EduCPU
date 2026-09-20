# 03 — Hva er en CPU?

## Læringsmål

Etter denne leksjonen skal du kunne:

- forklare CPU-ens grunnleggende oppgave;
- identifisere registre, ALU, programteller, minnegrensesnitt og kontroll-logikk;
- beskrive fetch–decode–execute-syklusen;
- forklare hvordan programtelleren velger neste instruksjon;
- følge én enkel EduCPU-instruksjon gjennom maskinen.

## Hva er det?

En **CPU** — central processing unit, eller sentral prosesseringsenhet — er delen av en datamaskin som gjentatte ganger leser instruksjoner og utfører operasjonene de beskriver.

En nyttig første modell av en CPU består av noen få deler som samarbeider:

- **registre** holder små verdier nær prosesseringslogikken;
- **ALU-en** utfører aritmetiske og logiske operasjoner;
- **programtelleren (PC)** peker ut neste instruksjon;
- **FLAGS** husker utvalgte egenskaper ved resultater;
- **minnegrensesnittet** flytter instruksjons- og databytes mellom CPU og minne;
- **kontroll-logikken** tolker en instruksjon og koordinerer hva de andre delene skal gjøre.

CPU-en er altså ikke én magisk komponent som «forstår programmer». Den er et system av enklere mekanismer som arbeider sammen.

## Hvorfor trenger vi det?

I de forrige leksjonene lærte vi at bits kan lagres og endres. En programmerbar datamaskin trenger noe som kan velge **hvilken operasjon som skal skje videre**, basert på instruksjoner som ligger i minnet.

Det er CPU-ens sentrale oppgave.

I stedet for å koble en krets permanent for én bestemt sekvens av operasjoner, lagrer vi en sekvens med instruksjonsbytes i minnet. CPU-en henter og utfører dem etter tur.

## Hvordan gjør EduCPU det?

EduCPU har:

- åtte generelle 8-bits registre: R0–R7;
- en 16-bits PC;
- en 16-bits SP;
- et 8-bits FLAGS-register;
- 64 KiB byte-adresserbart minne;
- instruksjoner som `MOVI`, `ADD`, `AND`, `JMP` og `HALT`.

En forenklet modell er:

```text
                    +------------------+
                    |  Kontroll-logikk |
                    +---------+--------+
                              |
                              v
+---------+     +----------+  |  +---------+
| Minne   |<--->| PC /     |--+->| Dekoder |
|         |     | fetch     |     +----+----+
+---------+     +----------+          |
                                      v
                               +------+------+
                               | Registre    |
                               | R0 ... R7   |
                               +------+------+
                                      |
                                      v
                               +------+------+
                               |    ALU      |
                               +------+------+
                                      |
                                +-----+-----+
                                |   FLAGS   |
                                +-----------+
```

Dette er en pedagogisk modell av informasjonsflyt, ikke en påstand om klokkesyklusene i den senere FPGA-implementasjonen.

## Fetch, decode, execute

Vi kan beskrive CPU-ens gjentatte arbeid slik:

1. **Fetch** — bruk PC til å hente neste instruksjonsbyte fra minnet.
2. **Decode** — finn ut hvilken instruksjon byten representerer og hvilke operander den trenger.
3. **Execute** — utfør operasjonen.
4. **Fortsett** — PC peker ut neste instruksjon, med mindre en instruksjon med vilje endrer kontrollflyten.

Virkelige implementasjoner kan dele opp eller overlappe disse handlingene på andre måter. For EduCPU gir denne rekkefølgen oss en tydelig mental modell.

> **Hvordan vet EduCPU det?**
>
> CPU-en leser ikke ordet `MOVI`. Assembleren har allerede oversatt det til en opcode-byte. Instruksjonsdekoderen gjenkjenner dette bitmønsteret, og kontroll-logikken sørger for at operandbytene hentes og målregisteret skrives.

## Gjennomgått eksempel

Se på:

```asm
MOVI R0, 42
HALT
```

EduASM koder den første instruksjonen som tre bytes:

```text
11 00 2A
```

De betyr:

```text
11  -> MOVI-opcode
00  -> R0
2A  -> immediate-verdien 42
```

Etter reset er PC `0x0000`.

Konseptuelt gjør EduCPU dette:

1. henter `0x11` fra adresse `0x0000`;
2. dekoder den som `MOVI`;
3. henter `0x00` og identifiserer R0;
4. henter `0x2A`;
5. skriver `0x2A` til R0;
6. har nå PC = `0x0003`;
7. henter `0x01`, som er `HALT`-opcoden;
8. går til halted-tilstand.

Ingen av disse stegene krever at CPU-en forstår teksten i kildekoden.

## Kjør og observer

Repoet inneholder:

`course/examples/lesson03-cpu-cycle.eduasm`

Før du kjører det, forutsi:

- sluttverdiene til R0 og R1;
- verdien til PC etter `HALT`;
- om FLAGS endres.

Assembler og kjør deretter programmet med EduCPU-verktøyene.

Den automatiserte kurstesten kjører den samme fixturen mot den kjørbare referanse-CPU-en.

Du kan også åpne akkurat denne kildefilen direkte i nettleservisualiseringen:

```sh
PYTHONPATH=tools:reference python tools/eduvis.py course/examples/lesson03-cpu-cycle.eduasm
```

Åpne deretter `http://127.0.0.1:8080/`. Bruk **Micro-step** for å følge de pedagogiske fasene gjennom PC, minne, dekoder, registre, ALU og FLAGS, eller **Instruction step** for å kjøre én komplett arkitektonisk instruksjon.


## Forklar resultatet

Det viktige er ikke bare at en instruksjon produserte en verdi. CPU-en klarte å **velge en instruksjon fra minnet, identifisere operasjonen, hente operandene, endre maskintilstanden og gå videre til neste instruksjon**.

Et program er derfor ikke noe som eksisterer separat fra maskinen. Under kjøring er det bytes i minnet der bitmønstrene fører til bestemte tilstandsendringer.

## Oppgaver

### Forståelse

1. Hva er oppgaven til PC?
2. Hva gjør ALU-en?
3. Hvorfor trenger en CPU kontroll-logikk?
4. Hvor ligger instruksjonene før CPU-en utfører dem?
5. Hva er forskjellen på et assembly-mnemonic og en opcode?

### Praktisk

For dette programmet:

```asm
MOVI R0, 10
MOVI R1, 20
ADD R0, R1
HALT
```

forutsi sluttverdiene til R0, R1 og PC.

Kjør deretter programmet og sammenlign med det du forutsa.

### Utforsk selv

Endre én byte i et assemblert program i stedet for å endre assembly-kildekoden.

Før du kjører den endrede binærfilen, bruk ISA-dokumentasjonen til å forutsi hva den endrede byten vil gjøre.

Dette er en viktig overgang: Du begynner nå å se programmet fra CPU-ens synsvinkel.

## Sjekk forståelsen

1. Hvilke tre ord oppsummerer den grunnleggende instruksjonssyklusen i denne leksjonen?
2. Henter EduCPU assembly-tekst fra minnet?
3. Hvilket register peker ut neste instruksjon?
4. Hvilken del utfører aritmetiske og logiske transformasjoner?
5. Hvorfor er det bedre å forstå CPU-en som samarbeidende mekanismer enn som en komponent som «vet» programmet?

Løsningene oppbevares separat fra leksjonen.

## Neste

Vi har nå en komplett første mental modell av en CPU. Neste leksjon ser nærmere på **maskintilstand**: PC, SP, FLAGS, R0–R7 og minne, og lærer hvordan vi kan beskrive et nøyaktig øyeblikk i et EduCPU-program.
