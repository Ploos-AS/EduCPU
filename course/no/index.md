# EduCPU-kurset

**Lær hvordan en datamaskin fungerer, ett forståelig lag om gangen.**

EduCPU er en bevisst liten undervisningsdatamaskin.

## Før du begynner

Kurset er laget for nybegynnere. Du trenger ikke kunne CPU-design, assembly eller programmering på forhånd. Litt grunnleggende regning er nyttig, men alle nødvendige begreper introduseres underveis. Kurset passer både for selvstudium og undervisning i klasserom/lab.

Forvent omtrent **30–60 minutter per leksjon** for gjennomgang og enkle øvelser. Leksjon 10–15 kan ta **60–120 minutter** dersom du gjør de praktiske oppgavene og følger hele toolchainen.

## Begreper vi bruker konsekvent

- **bit / byte** — én bit er 0 eller 1; én byte er 8 bits.
- **register** — liten, navngitt lagringsplass i CPU-en.
- **maskintilstand** — verdiene i registre, PC, SP, FLAGS og relevant minne/arkitektonisk tilstand.
- **instruksjon** — en arkitektonisk operasjon som CPU-en skal utføre.
- **opcode** — bitmønsteret som identifiserer instruksjonens operasjon.
- **ISA** — kontrakten som beskriver instruksjoner, encoding og observerbar oppførsel.
- **referanse-CPU** — den autoritative programvaremodellen som brukes til å definere og kontrollere arkitektonisk oppførsel.
- **emulator** — en separat implementasjon som etterligner EduCPU og kan sammenlignes med referanse-CPU-en.
- **datapath** — hardware-strukturen som flytter og behandler verdier.
- **kontroll-logikk** — logikken som velger hvilke datapath-handlinger som skal skje.
- **implementasjon** — en konkret realisering av ISA-en, for eksempel programvare eller FPGA-logikk.

**Arkitektur og implementasjon holdes adskilt gjennom hele kurset.** EduCPU er et frittstående prosjekt og undervisningssystem. Eksterne CPU- eller hardwareprosjekter er ikke en del av EduCPU-arkitekturen eller kursets roadmap.

## Kurskart

```text
bits → logikk → CPU-tilstand → ISA → assembly → stack/ABI
                                      ↓
                         compiler → IR → object/linking
                                      ↓
                              maskinkode → CPU
                                      ↓
                         datapath/control → FPGA
```

Du trenger ikke forstå hele kartet på forhånd. Det er nettopp dette kurset bygger opp, lag for lag.

**Verktøy fra leksjon 3 og utover:** EduVis lar deg se CPU-tilstanden steg for steg i nettleseren. EduGuide lar deg jobbe etter mønsteret **FORUTSI → OBSERVER → FORKLAR**. Kurset starter med bits og bygger gradvis opp en komplett forståelse av hvordan et EduC-program blir til maskininstruksjoner og observerbare endringer i CPU-tilstanden.

## Reisen

1. Bits, bytes og heksadesimale tall
2. Logikk og lagring av informasjon
3. Hva er en CPU?
4. Registre, minne og maskintilstand
5. Instruksjoner og maskinkode
6. Assembly og hva en assembler gjør
7. Aritmetikk, flagg og hopp
8. Stacken
9. Funksjoner, CALL/RET og ABI
10. Hva er en compiler?
11. EduC, AST og semantisk analyse
12. EduIR og kodegenerering
13. Objektfiler, relocations og linking
14. Følg et komplett program fra EduC til kjøring
15. Hvordan en CPU kan bygges: ALU, datapath, kontroll og veien mot FPGA

Gjennom hele kurset stiller vi spørsmålet: **Hvordan vet EduCPU det?**

## Videre lesning

Hvis du ønsker en bok ved siden av kurset med samme type bottom-up-utforskning, anbefaler vi J. Clark Scotts *But How Do It Know? — The Basic Principles of Computers for Everyone* som videre lesning. Den bygger opp ideene fra enkel digital logikk mot en fungerende CPU, mens EduCPU er et selvstendig prosjekt og kurs.

**Boklenke:** kommer. Når en kjøpslenke er en affiliate-lenke, vil dette merkes tydelig; Ploos AS kan motta provisjon uten ekstra kostnad for deg.


## Lær videre

Etter EduCPU er **EduAVR** et naturlig neste steg: gå fra den bevisst lille undervisnings-CPU-en til en ekte AVR-mikrokontroller, reelle embedded-verktøy og fysisk hardware. EduCPU forklarer mekanismene først; EduAVR lar deg bruke de samme ideene på en praktisk mikrokontrollerplattform.

Fortsett med [EduAVR](https://ploos-as.github.io/EduAVR/).
