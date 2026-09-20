# Løsninger til oppgavene

Disse løsningene er et tillegg til leksjonene, ikke en erstatning for å forutsi og eksperimentere selv. Prøv oppgaven først og sammenlign deretter resonnementet.

### Om praktiske og utforskende oppgaver

Praktiske oppgaver har ikke alltid én fasit. De er laget for at du skal kjøre ekte EduCPU-verktøy, gjøre en prediksjon og kontrollere den mot maskinens faktiske tilstand. Når det finnes en forventet observasjon, beskriver løsningen både **hva** som skal skje og **hvorfor**. For `Praktisk` og `Utforsk selv` bør du derfor bruke løsningen som et resonnementsspor, ikke bare som et svarark.

## 01 — Bits, bytes og heksadesimalt

42 er `00101010₂`, `0x2A` og desimalt 42. Én byte har 256 mulige bitmønstre, fra 0 til 255 når den tolkes som en unsigned EduCPU-byte.

## 02 — Logikk og lagring

For `0xCC` og `0xAA`: AND = `0x88`, OR = `0xEE`, XOR = `0x66`; NOT `0xCC` = `0x33`. Logikk beregner verdier; registre eller minne bevarer tilstand.

## 03 — Hva er en CPU?

En CPU trenger lagret tilstand, en måte å hente instruksjoner på, dekoding/kontroll og mekanismer som ALU og datapath for å utføre de nødvendige tilstandsendringene. Fetch/decode/execute beskriver prosessen uten å kreve ett bestemt internt hardware-design.

## 04 — Maskintilstand

Når to like unsigned bytes subtraheres blir resultatet null, så Z=1. EduCPU setter C=1 ved subtraksjon når det ikke trengs borrow. PC peker på neste instruksjon; SP peker på stackposisjonen.

## 05 — Instruksjoner og maskinkode

Opcode identifiserer operasjonen; operandbytes identifiserer registre, immediate-verdier eller adresser. EduCPU lagrer 16-bits adresser little-endian: `0x1234` blir `34 12`.

## 06 — EduASM

Labels er hjelpemidler for assembleren, ikke CPU-tilstand. En forward label krever at adressen finnes før referansen kan kodes ferdig, derfor bruker den enkle EduASM-modellen to pass.

En countdown kan være:

```asm
MOVI R0, 5
loop:
    SUBI R0, 1
    JNZ loop
HALT
```

## 07 — Aritmetikk, FLAGS og hopp

`255 + 1` wrap-er til 0 i et 8-bits register. Z settes fordi resultatet er null og C registrerer carry. CMP oppdaterer flags uten å lagre subtraksjonsresultatet. JZ tester Z; JC tester C.

## 08 — Stacken

Stacken vokser nedover. PUSH dekrementerer først SP og skriver deretter. POP leser først og inkrementerer så SP. POP sletter ikke den gamle minnebyten; den endrer hvilken del av minnet som regnes som aktiv stack.

## 09 — Funksjoner, CALL/RET og ABI

R0–R3 bærer de første fire byte-argumentene og R0 bærer primær byte-returverdi. CALL lagrer retur-PC på stacken; RET gjenoppretter den. En balansert funksjon gjenoppretter SP til verdien ved inngang.

## 10 — Hva er en compiler?

Compileren oversetter EduC gjennom kontrollerte representasjoner mot EduASM og objektkode. Assembleren gjør EduASM til kodede bytes/objektdata; linkeren kombinerer objekter og løser adresser. CPU-en kjører aldri EduC-kildekode.

## 11 — EduC, AST og semantisk analyse

Parsing avgjør om kilden har gyldig grammatisk struktur. Semantisk analyse kontrollerer blant annet om en variabel finnes, typer passer, et kall har riktige argumenter og en non-void-funksjon returnerer korrekt.

## 12 — EduIR og kodegenerering

EduIR gjør compiler-operasjoner eksplisitte uten å introdusere maskinregistre og stack offsets for tidlig. Kodegenereringen mapper deretter verdier til stack-backed slots og ABI-registre og emitterer konkret EduASM.

## 13 — Objektfiler, relocations og linking

En export tilbyr et symbol; en import etterspør ett. En relocation markerer bytes som ikke kan få endelig verdi før linking. `abs16le` betyr at en endelig absolutt 16-bits adresse skrives low byte først. CPU-en ser bare den patchede numeriske adressen.

## 14 — Fra EduC til kjøring

Kjeden nedover er:

```text
source → AST → semantics → IR → assembly → object
→ relocation/link → bytes → CPU-tilstandsendringer
```

Et kildekodekall blir IR-call under lowering, CALL-instruksjon under kodegenerering og et endelig numerisk CALL-target under linking. Bare de ferdige maskinbytene brukes av CPU-en.

## 15 — Hvordan en CPU bygges

Registre lagrer tilstand. ALU beregner. Datapath gir ruter for verdier. Kontroll-logikken velger rutene og operasjonene som instruksjonen krever. To implementasjoner kan bruke ulik intern hardware eller timing og likevel implementere samme ISA-synlige oppførsel.

For CALL må en konseptuell implementasjon lagre retur-PC etter den definerte high-byte/low-byte-stackkonvensjonen og deretter laste PC med target. Den eksakte interne klokkesekvensen er et implementasjonsvalg.
