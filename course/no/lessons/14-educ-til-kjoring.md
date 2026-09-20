# 14 — Fra EduC til kjøring

## Læringsmål

Følg ett program gjennom hele EduCPU-toolchainen og koble kildekode, IR, assembly, bytes og CPU-tilstand sammen.

## Ett program, hele veien ned

```c
byte add(byte a, byte b) { return a + b; }
byte main() { byte answer = add(20, 22); return answer; }
```

Hele kjeden er:

```text
EduC → AST → semantisk analyse → EduIR → EduASM
→ objekt + relocations → linker → maskinkodebytes
→ fetch/decode/execute → CPU-tilstand
```

På kildenivå ser vi funksjoner, parametere, en lokal variabel og returns. AST-en gjør grammatisk struktur eksplisitt. Semantisk analyse verifiserer navn, typer, kall og returns. EduIR gjør operasjoner og temporaries eksplisitte. Kodegenereringen velger stack slots, registre og ABI-mekanismer. Assembleren koder instruksjonene og bevarer uløste adresser som relocations. Linkeren gir symbolene endelige numeriske adresser.

> **Hvordan vet EduCPU hvilken kildekodefunksjon den skal kalle?**
>
> Den kjenner ikke kildekodefunksjoner. Ved runtime har compiler, assembler og linker redusert ideen til en CALL-opcode etterfulgt av en numerisk adresse.

## Kjøring: bytes blir til tilstandsendringer

CPU-en henter gjentatte ganger opcode på PC, dekoder operandene og utfører ISA-definerte tilstandsendringer. I programmet kan vi observere PC gjennom instruksjoner og CALL/RET, SP for returadresser og frames, argumenter i ABI-registre, verdier i stack slots, ADD som produserer 42 og R0 som bærer sluttresultatet.

## Compile trace

EduC kan produsere et `educpu-compile-trace-v0`-artifact som korrelerer source, AST, EduIR, generert assembly, maskinbytes, symboler og instruksjonsadresser. Dette er en **compile-time trace**, ikke en runtime execution trace. I denne leksjonen kombinerer vi den med faktisk steg-for-steg-kjøring på referanse-CPU-en.

Den CI-testede fixturen er `course/examples/lesson14-end-to-end.educ`. Testen verifiserer ekte compile trace og kompilert image, kjører deretter imaget og registrerer faktiske tilstandsendringer til programmet returnerer 42 med balansert stack.

## Kjør med EduGuide

Fra roten av repositoryet kan du kjøre den virkelige leksjonsfixturen gjennom den guidede runneren:

```bash
PYTHONPATH=tools:reference python tools/eduguide.py course/examples/lesson14-end-to-end.educ
```

For hver arkitektoniske instruksjon viser EduGuide instruksjonen, ber deg **FORUTSI**, viser de faktiske tilstandsendringene under **OBSERVER**, skriver resulterende PC/SP/FLAGS/registertilstand og ber deg **FORKLARE** hvilken ISA-regel som forårsaket endringen.

For bare å kontrollere sluttresultatet:

```bash
PYTHONPATH=tools:reference python tools/eduguide.py course/examples/lesson14-end-to-end.educ --summary
```

EduGuide bruker samme compiler og referanse-CPU som kvalifikasjonstestene; det er ikke en separat undervisnings-CPU.

## Følg én instruksjon

Velg en instruksjon fra trace. Noter adresse, generert assembly og kodede bytes. Forutsi opcode, operander, tilstandsendring og neste PC. Kjør ett CPU-steg og sammenlign.

```text
forutsi → steg → observer → forklar
```

## Følg funksjonskallet

Finn generert CALL til `add`. Før du stepper den, noter PC og SP. Etterpå undersøker du ny PC, ny SP og returadressebytene i minnet. Fortsett gjennom `add` og RET og verifiser at kjøringen fortsetter etter CALL.

Dette kobler et EduC-funksjonskall til konkrete bytes og stacktilstand.

## Oppgaver

1. På hvilket steg blir et EduC-kall til IR-call, CALL-instruksjon og til slutt numerisk target-adresse?
2. Hvilke representasjoner finnes bare under bygging?
3. Endre 20 og 22 til 19 og 23. Forutsi hva som endres og hva som forblir strukturelt likt.
4. Legg til `byte inc(byte x) { return x + 1; }`, kall den og tegn CALL/RET-stacktilstandene.

## Sjekk forståelsen

Forklar hver pil uten å hoppe over et lag:

```text
source → AST → semantics → IR → assembly → object
→ relocation/link → bytes → fetch/decode/execute → state
```

For hver pil spør du: **Hvilken informasjon ble lagt til, fjernet eller gjort mer konkret?**

## Neste

Neste går vi under arkitekturnivået: **Hvordan kan en CPU bygges av ALU, registre, datapath og kontroll-logikk, og hvordan leder det mot en FPGA-implementasjon?**
