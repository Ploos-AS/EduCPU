# 15 — Hvordan en CPU bygges

## Læringsmål

Etter denne leksjonen skal du kunne forklare rollene til registre, ALU, datapath og kontroll-logikk, beskrive hvordan en instruksjon får data til å bevege seg gjennom en CPU, skille arkitektonisk oppførsel fra én bestemt hardware-implementasjon og koble EduCPU-modellen til en framtidig FPGA-realisering.

## Før du leser videre: forutsi datapathen

Se på:

```asm
MOVI R0, 20
MOVI R1, 22
ADD R0, R1
```

Før du leser hardware-delen, tegn en minimal datapath på papir.

Marker:

- hvor instruksjonen hentes;
- hvor immediate-verdien går;
- hvor R0 og R1 leses;
- hvor ALU-resultatet går;
- hvor FLAGS får informasjon;
- hvordan PC går videre.

Du trenger ikke tegne alle muxer. Målet er å lage en første hypotese om **hvilken informasjon som må kunne flyttes hvor**.

Etter gjennomgangen: sammenlign tegningen med den konseptuelle datapathen under. Rett bare det som faktisk var feil.

## Vi har nådd hardware-grensen

Så langt har vi behandlet EduCPU som en arkitektur:

- registrene R0–R7;
- PC og SP;
- FLAGS;
- minne;
- instruksjoner som MOVI, ADD, LOAD, CALL og RET;
- presise regler for hvordan hver instruksjon endrer maskintilstanden.

Referanse-CPU-en implementerer disse reglene i programvare.

Men en CPU kan også bygges som digital hardware.

Hovedideen er:

> ISA-en definerer **hva** maskinen må gjøre. Hardware-designet bestemmer **hvordan** signaler, lagring og logikk får det til å skje.

## Hva er ekte og hva er foreløpig?

Denne leksjonen beskriver **arkitekturen**, ikke en ferdig FPGA-nettlist eller et påstått fysisk skjema.

Det som allerede er konkret og testbart er:

- ISA v0 og dens instruksjonskoding;
- referanse-CPU-en;
- den uavhengige emulatoren;
- differential/conformance-testene;
- compiler- og toolchain-resultatene.

FPGA-datapathen er neste implementasjonslag. Derfor bruker vi bevisst en konseptuell datapath her i stedet for å late som om den er det endelige kretsdesignet.

Når HDL-implementasjonen finnes, skal denne leksjonen kunne oppgraderes med et faktisk EduCPU-blokkdiagram og vise hvilke deler av diagrammet som er arkitekturkrav versus konkrete FPGA-designvalg.

## Registre: små biter med tilstand

Et register lagrer bits.

EduCPU har åtte 8-bits general-purpose-registre, i tillegg til arkitektonisk tilstand som PC, SP og FLAGS.

På hardware-nivå trenger et register mekanismer for å:

1. holde nåværende verdi;
2. gjøre verdien tilgjengelig for annen logikk;
3. ta imot en ny verdi når kontroll-logikken ber det laste.

Uten lagring kan en krets beregne et resultat, men den kan ikke huske maskintilstand fra ett steg til det neste.

## ALU: beregn

**Arithmetic Logic Unit** utfører operasjoner som:

```text
ADD
SUB
AND
OR
XOR
NOT
SHL
SHR
sammenligningsrelatert aritmetikk
```

Konseptuelt mottar den inputverdier og en valgt operasjon, og produserer et resultat pluss informasjon som brukes til å oppdatere FLAGS.

For:

```asm
ADD R0, R1
```

må en hardware-implementasjon på en eller annen måte gjøre:

```text
les R0 ─┐
        ├→ ALU(add) → resultat → R0
les R1 ─┘              └──────→ FLAGS
```

ISA-en sier hva sluttverdien i R0 og flags skal være. Den krever ikke én bestemt intern kretsstruktur.

## Datapath: hvor verdiene kan reise

Registre og en ALU er ikke nok. Verdiene trenger ruter mellom komponentene.

**Datapath** er samlingen av lagring, busser, multiplexere og forbindelser som lar verdier bevege seg gjennom prosessoren.

En konseptuell EduCPU-datapath kan ha ruter mellom:

```text
             ┌──────────┐
Memory ─────►│ Decode / │
             │ Control  │
             └────┬─────┘
                  │
PC ───────────────┤
                  ▼
Registers ◄──────► ALU ─────► FLAGS
    ▲              │
    └──────────────┴────────► Memory
```

Dette er en undervisningsfigur, ikke det endelige FPGA-skjemaet.

## Kontroll: få riktig ting til å skje

Datapath gir muligheter. **Kontroll-logikken** velger hvilke muligheter som skal brukes for den aktuelle instruksjonen.

For ADD kan kontrollen måtte sørge for at:

- valgte kilde-registre leses;
- ALU-operasjonen settes til ADD;
- resultatet skrives til destination-registeret;
- FLAGS oppdateres;
- PC avanserer korrekt.

For STORE blir valgene annerledes. For JMP får PC en target-adresse i stedet for bare å gå videre.

Instruksjonsdekoderen og kontroll-logikken gjør opcode-bits om til disse kontrollvalgene.

> **Hvordan vet hardwaren at opcode 0x20 betyr ADD?**
>
> Fordi kontroll-logikken er designet slik at bitmønsteret som er tildelt ADD velger datapath-handlingene ISA-en krever. Betydningen skapes av arkitekturspesifikasjonen og realiseres av logikk.

## Klokke og tilstandsoverganger

Synkron digital hardware bruker vanligvis en klokke for å koordinere når lagret tilstand endres.

En nyttig forenklet modell er:

```text
nåværende tilstand
    ↓
kombinatorisk logikk beregner neste verdier
    ↓
klokkeflanke
    ↓
registre fanger neste tilstand
    ↓
ny nåværende tilstand
```

Dette kobler direkte til simulatorens idé om deterministiske tilstandsoverganger, men simulatorens konseptuelle microsteps er **ikke et løfte om eksakt FPGA-timing**.

Det skillet er viktig.

## Fetch, decode og execute i hardware

Den kjente syklusen kan nå sees som datapath- og kontrollaktivitet.

### Fetch

Bruk PC til å adressere minnet og hente opcode. Flytt eller forbered PC i henhold til instruksjonskodingen.

### Decode

Tolk opcode-bits og bestem instruksjonsform og nødvendige operander.

### Execute

Velg ALU-, minne-, register-, stack- eller kontrollflythandlinger og commit det arkitektoniske resultatet.

En enkel implementasjon kan bruke flere klokkesykluser per arkitektonisk instruksjon. En annen implementasjon kan organisere arbeidet annerledes og likevel implementere nøyaktig samme ISA.

## Arkitektur kontra implementasjon

Dette er et av de viktigste skillene i kurset.

**Arkitektur** inkluderer observerbare regler som:

- instruksjonskoding;
- registeroppførsel;
- flaggsemantikk;
- minnesynlige effekter;
- CALL/RET-stackkonvensjon;
- reset-tilstand.

**Implementasjon** inkluderer interne valg som:

- antall interne cycles;
- busstruktur;
- multiplexere;
- koding av kontrolltilstand;
- bruk av FPGA block RAM;
- om enkelte operasjoner deler hardware.

Programvare skal avhenge av arkitekturen, ikke tilfeldige interne detaljer.

## Hvorfor FPGA?

En **FPGA** er programmerbar digital hardware. I stedet for å skrive programvare som simulerer EduCPU-instruksjoner kan vi beskrive logikk som fysisk realiserer registre, ALU-operasjoner, kontroll og datapath inne i FPGA-fabric.

Utviklingen blir:

```text
ISA-spesifikasjon
      ↓
referanse-CPU i programvare
      ↓
tester / kvalifisering
      ↓
HDL-implementasjon
      ↓
simulering
      ↓
FPGA-syntese
      ↓
hardware-kjøring
```

Referansemodellen blir svært verdifull her: FPGA-implementasjonen kan testes mot allerede definert arkitektonisk oppførsel.

## Samme program, forskjellig realisering

Tenk deg samme maskinkodeprogram kjørt på:

1. Python-referanse-CPU-en;
2. EduCPU-emulatoren;
3. en framtidig EduCPU på FPGA.

Hvis alle tre implementerer ISA-en korrekt, skal programmet observere de samme arkitektoniske resultatene.

Internt kan de være helt forskjellige.

Dette er grunnen til at ISA v0 ble fryst før de senere lagene bygges: compiler, emulator og hardware trenger en stabil kontrakt.

## Fra ADD til hardware-tenkning

Ta:

```asm
MOVI R0, 20
MOVI R1, 22
ADD R0, R1
HALT
```

For ADD, svar på:

1. Hvor er de to inputverdiene lagret?
2. Hvilke datapath-ruter fører dem til ALU?
3. Hvilken ALU-operasjon velges?
4. Hvor skrives resultatet?
5. Hvilke flags oppdateres?
6. Hva skjer med PC?
7. Hvilke av disse oppførslene kreves av ISA-en, og hvilke avhenger av implementasjonen?

Det siste spørsmålet er nøkkelen når vi går fra programmerer til CPU-designer.

## Oppgaver

### Forståelse

1. Hva er forskjellen mellom et register og en ALU?
2. Hva er en datapath?
3. Hva gjør kontroll-logikken?
4. Hvorfor gir opcode 0x20 ADD-oppførsel?
5. Kan to forskjellige hardware-design implementere samme ISA?

### Praktisk

Velg MOVI, LOAD, STORE og JMP. Tegn for hver instruksjon bare komponentene som må delta og piler for den viktige dataflyten.

### Utforsk selv

Lag en konseptuell kontrollsekvens for CALL.

Husk de arkitektoniske kravene EduCPU allerede har definert:

- lagre retur-PC;
- push high byte og deretter low byte;
- la low byte ligge på MEM[SP];
- last PC med target.

Ikke bekymre deg for nøyaktig antall FPGA-klokkesykluser ennå.

## Sjekk forståelsen

Forklar setningen:

> En CPU er ikke en instruksjonsliste. Den er tilstand pluss logikk og kontrollert flytting av informasjon som realiserer instruksjonslisten.

Forklar deretter hvorfor både Python-referanse-CPU-en og en framtidig FPGA kan være «EduCPU».

## Hvor går vi videre?

Du har nå hele den konseptuelle reisen:

```text
bits
→ logikk og lagring
→ CPU-tilstand
→ instruksjoner
→ maskinkode
→ assembly
→ stack og ABI
→ compiler
→ IR og kodegenerering
→ objekter og linking
→ kjøring
→ datapath og kontroll
→ hardware-realisering
```

Neste prosjektmilepæl tar dette fundamentet videre mot **EduCPU-emulatoren**, og senere **FPGA-CPU-implementasjonen**. ISA-en og kvalifikasjonstestene forblir kontrakten alle realiseringene må følge.
