# 10 — Hva er en compiler?

## Læringsmål

Etter denne leksjonen skal du kunne forklare hvorfor en compiler finnes, skille kildespråk fra maskinspråk, navngi de viktigste stegene i EduC-kompileringen og følge et lite uttrykk fra EduC mot EduCPU-instruksjoner.

## Et oversettelsesproblem

Mennesker foretrekker gjerne å skrive:

```c
byte add(byte a, byte b) {
    return a + b;
}
```

EduCPU kan ikke kjøre denne teksten. Den kjører bytes definert av ISA-en.

En **compiler** oversetter et program uttrykt i ett språk til en representasjon på lavere nivå, samtidig som programmets tiltenkte oppførsel bevares.

For EduCPU er hele undervisningskjeden:

```text
EduC-kildekode
    ↓ parsing
AST
    ↓ semantisk analyse
kontrollert program
    ↓ lowering
EduIR
    ↓ kodegenerering
EduASM
    ↓ assembler
objektfil
    ↓ linker
maskinkode-bytes
    ↓ kjøring
endringer i EduCPU-tilstand
```

Mellomstegene er bevisste. De lar oss undersøke hva hvert verktøy har lært og hvilken informasjon som legges til eller fjernes.

> **Hvordan vet EduCPU hva EduC-programmet betyr?**
>
> Det gjør den ikke. CPU-en ser aldri EduC, AST eller EduIR. Compiler- og assemblerstegene oversetter programmet gradvis til bare ISA-definerte bytes gjenstår. CPU-en kjører kun disse bytene.

## Parsing: struktur fra tekst

En parser gjør kildetekst om til en strukturert representasjon kalt et **Abstract Syntax Tree (AST)**.

For:

```c
return a + b;
```

er den viktige strukturen omtrent:

```text
Return
└── Add
    ├── Name a
    └── Name b
```

AST-en lagrer relasjoner som bare er implisitte i tegnene i kildeteksten.

## Semantisk analyse: gir det mening?

Tekst kan være syntaktisk gyldig og likevel bryte språkreglene.

Semantisk analyse kontrollerer blant annet:

- navn må finnes;
- funksjonskall må vise til deklarerte funksjoner;
- argumenttyper må passe;
- returverdier må passe funksjonstypen;
- duplikate lokale navn avvises.

Dette steget svarer på spørsmål på språknivå før maskinkode finnes.

## EduIR: gjør operasjonene eksplisitte

EduCPU bruker en liten pedagogisk mellomrepresentasjon kalt **EduIR**.

Et høynivåuttrykk som:

```c
byte answer = add(20, 22);
```

kan senkes til eksplisitte operasjoner med konstanter, funksjonskall og kopiering.

EduIR er bevisst ikke maskin-assembly. Den har midlertidige verdier og kildekodebegreper uten å tvinge compileren til å velge fysiske registre med en gang.

## Kodegenerering

Backenden gjør EduIR om til EduASM som følger EduCPU ISA og ABI.

Argumenter må for eksempel til slutt plasseres der ABI v0 krever — R0, R1, R2 og R3 — før CALL.

Compiler-genererte verdier kan også trenge stackplasser. Her blir stacken og ABI-en fra de forrige leksjonene praktisk compilermaskineri.

## Assembly og linking er separate jobber

Compileren trenger ikke løse alt selv.

EduASM gjør assembly om til objektdata og relocation-informasjon. Linkeren kombinerer objekter og løser adresser mellom dem. Først da har vi det endelige maskinkodebildet.

Ved å holde stegene separate blir toolchainen enklere å undersøke, samtidig som vi lærer hvorfor virkelige systemer bruker assemblere, objektfiler og linkere.

## Gjennomgått eksempel

Den CI-testede fixturen er `course/examples/lesson10-compiler.educ`:

```c
byte add(byte a, byte b) {
    return a + b;
}

byte main() {
    return add(20, 22);
}
```

Testen sender den samme kildekoden gjennom den ekte EduC-pipelinen og kjører de resulterende bytene på referanse-CPU-en.

Forventet resultat er 42.

Det interessante er ikke bare at 42 dukker opp. Følg hvordan betydningen skifter representasjon:

```text
20 + 22
→ kildeuttrykk
→ AST-noder
→ EduIR-operasjoner
→ generert EduASM
→ kodede bytes
→ register-/stackoperasjoner
→ R0 = 42
```

## Compiler kontra CPU

En compiler analyserer språkstruktur og oversetter den før kjøring.

CPU-en gjør den langt mindre, gjentatte jobben vi allerede kjenner:

```text
fetch → decode → execute → continue
```

Dette skillet er grunnleggende. Et avansert kildespråk kan kjøre på en enkel CPU fordi programvare utfører oversettelsen.

## Oppgaver

### Forståelse

1. Hvorfor kan ikke EduCPU kjøre EduC-kildetekst direkte?
2. Hva representerer en AST?
3. Hvilken type feil hører hjemme i semantisk analyse?
4. Hvorfor er EduIR nyttig?
5. Hvilket verktøy gjør til slutt symbolsk assembly om til kodede instruksjonsbytes?

### Praktisk

Endre konstantene i fixturen fra 20 og 22 til to andre verdier med en sum som passer i én byte. Forutsi returverdien før kompilering.

Endre deretter funksjonskallet slik at et argument har feil type. Hvilket kompileringssteg bør avvise det?

### Utforsk selv

Kjør compileren med utskrift av AST, IR, assembly og compile trace. Sammenlign den samme operasjonen på hvert steg.

Finn én opplysning som finnes i EduC, men forsvinner før maskinkoden, og én lavnivådetalj som først dukker opp under kodegenereringen.

## Sjekk forståelsen

Forklar setningen:

> Compileren forstår EduC-struktur; CPU-en forstår bare ISA-en sin.

Hvor, helt konkret, blir forbindelsen mellom disse to verdenene skapt?

## Representasjonssjekk

Stopp før du kjører fixturen. Velg uttrykket `20 + 22` og skriv én setning for hva som er synlig på hvert nivå:

```text
EduC → AST → EduIR → EduASM → bytes → CPU-state
```

For hvert steg: **Hva vet dette laget som laget før ikke visste, og hva har blitt abstrakt bort?**

Kjør deretter fixturen og kontroller én konkret overgang mellom hvert nabonivå.

## Verktøy

Bruk den ekte kursfixturen: `course/examples/lesson10-compiler.educ`.

**EduGuide:** bruk den guidede PREDICT → OBSERVE → EXPLAIN-flyten. For CPU-kjøring kan du bruke EduVis.

Forvent viktige tilstands- eller compiler-endringer før du kjører fixturen, og sammenlign deretter med resultatet.

## Neste

Neste leksjon undersøker de første stegene i detalj: **EduC, AST og semantisk analyse**.
