# 09 — Funksjoner, CALL/RET og ABI

## Læringsmål

Etter denne leksjonen skal du kunne forklare hvordan CALL og RET bruker stacken, identifisere en returadresse, sende enkle argumenter etter EduCPU ABI, identifisere caller- og callee-saved registre og forklare hvorfor en calling convention er nødvendig.

## Hvorfor funksjoner trenger regler

Et funksjonskall skaper flere spørsmål:

- Hvor fortsetter kjøringen etterpå?
- Hvor plasseres argumentene?
- Hvor plasseres returverdien?
- Hvilke registre kan funksjonen endre?
- Hvem gjenoppretter midlertidig stackplass?

En **ABI** (Application Binary Interface) svarer presist på disse spørsmålene.

EduCPU ABI v0 er bevisst liten slik at vi kan følge hver eneste byte.

## CALL lagrer hvor vi skal returnere

Se på:

```asm
CALL add_one
HALT

add_one:
    ADDI R0, 1
    RET
```

Når CALL utføres, peker PC allerede på instruksjonen etter CALL. Denne adressen er **returadressen**.

EduCPU pusher den 16-bits returadressen på stacken og legger deretter funksjonsadressen i PC.

CALL pusher returadressen med **high byte først og deretter low byte**. Fordi stacken vokser nedover, ender low byte på `MEM[SP]`.

RET gjør det motsatte: den popper low byte, så high byte, bygger den 16-bits adressen igjen og legger den i PC.

> **Hvordan vet EduCPU hvor den skal returnere?**
>
> Den forstår ikke funksjoner. CALL lagrer et tall — retur-PC — med et presist definert stackformat. RET leser bytene tilbake og legger den rekonstruerte adressen i PC.

## Argumenter og returverdier

EduCPU ABI v0 sender opptil fire byte-store argumenter i registre:

| Formål | Register |
| --- | --- |
| argument 1 | R0 |
| argument 2 | R1 |
| argument 3 | R2 |
| argument 4 | R3 |
| primær 8-bits returverdi | R0 |
| high byte av 16-bits returverdi | R1 |

Eksempel:

```asm
MOVI R0, 20
MOVI R1, 22
CALL add
HALT

add:
    ADD R0, R1
    RET
```

Caller legger 20 og 22 i R0 og R1. Funksjonen returnerer 42 i R0.

Ingen spesiell hardware sier at «R0 er argument 1». Betydningen kommer fra ABI-kontrakten som caller, callee og compiler deler.

## Caller-saved og callee-saved registre

ABI v0 definerer:

- R0–R3: argument-/returregistre og caller-saved;
- R4–R6: callee-saved;
- R7: caller-saved scratch;
- FLAGS: caller-saved.

**Caller-saved** betyr at caller må bevare en verdi dersom den trenger verdien etter funksjonskallet.

**Callee-saved** betyr at en funksjon som endrer registeret må gjenopprette den opprinnelige verdien før den returnerer.

Reglene gjør at funksjoner skrevet uavhengig av hverandre kan samarbeide.

## Stackbalanse

En funksjon må returnere med SP balansert i forhold til tilstanden ved inngang, bortsett fra CALL/RET sin egen returadressemekanisme.

EduCPU har også `ENTER n` og `LEAVE n` for lokal stackplass:

```asm
worker:
    ENTER 2
    ; to bytes lokal frame-plass
    LEAVE 2
    RET
```

`ENTER 2` flytter SP to bytes ned. `LEAVE 2` gjenoppretter den.

Compileren kan lese og skrive bytes i stack-framen med `LOADS` og `STORES`. Vi ser hvorfor dette er nyttig når vi følger EduC gjennom kodegenereringen.

## Gjennomgått eksempel

Leksjonsfixturen kaller en funksjon med to argumenter:

```asm
MOVI R0, 20
MOVI R1, 22
CALL add
HALT

add:
    ADD R0, R1
    RET
```

Før kjøring, forutsi:

1. adressen umiddelbart etter CALL;
2. SP umiddelbart før CALL;
3. de to minnebytene CALL skriver;
4. SP ved inngangen til `add`;
5. R0 etter ADD;
6. PC og SP umiddelbart etter RET.

Kjør deretter steg for steg og sammenlign.

## ABI kontra ISA

Dette skillet er viktig.

**ISA-en** definerer hva CALL, RET, PUSH, registre og minneoperasjoner gjør.

**ABI-en** definerer konvensjoner for hvordan disse mekanismene brukes sammen: argumentregistre, returregistre, saved-registre og stackdisiplin.

CPU-en håndhever ISA-en. Programmer og verktøy blir enige om å følge ABI-en.

## Oppgaver

### Forståelse

1. Hva er en returadresse helt konkret?
2. Hvilken byte av en EduCPU-returadresse ligger på `MEM[SP]`?
3. Hvor sendes det første byte-argumentet?
4. Hvilke registre er callee-saved?
5. Hvorfor kan to funksjoner være uenige selv om begge bruker gyldige ISA-instruksjoner?

### Praktisk

Skriv en funksjon `double` som tar imot én byte i R0 og returnerer det dobbelte i R0.

Skriv deretter en funksjon som endrer R4 midlertidig. Bevar R4 etter ABI-reglene.

### Utforsk selv

Kjør CALL og RET steg for steg mens du følger PC, SP og minnet rundt stacken.

Legg deretter et nytt funksjonskall inne i den første funksjonen. Tegn begge returadressene på stacken før du kjører programmet.

## Sjekk forståelsen

Følg kjeden:

```text
caller → argumentregistre → CALL → returadresse på stack
       → callee → returverdi → RET → caller
```

Hvilke deler er hardware/ISA-oppførsel, og hvilke eksisterer bare fordi programvare er enig om ABI-en?

## Verktøy

Bruk den ekte kursfixturen: `course/examples/lesson09-call-ret-abi.eduasm`.

**EduVis:** bruk nettleservisualiseringen for å stege gjennom CPU-tilstanden. **eduguide:** bruk den guidede PREDICT → OBSERVE → EXPLAIN-flyten.

Forvent viktige tilstands- eller compiler-endringer før du kjører fixturen, og sammenlign deretter med resultatet.

## Neste

Nå kjenner vi nok av lavnivåmekanismene til å stille et mye større spørsmål: Hvordan kan programmereren skrive noe mer uttrykksfullt og la verktøy produsere alt dette automatisk? Neste: **Hva er en compiler?**
