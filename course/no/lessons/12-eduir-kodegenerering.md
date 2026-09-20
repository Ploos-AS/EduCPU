# 12 — EduIR og kodegenerering

## Læringsmål

Etter denne leksjonen skal du kunne forklare hvorfor en compiler bruker en mellomrepresentasjon, lese enkel EduIR, skille lowering fra kodegenerering og følge EduIR-verdier til stack slots, registre og EduASM.

## Hvorfor enda en representasjon?

Etter parsing og semantisk analyse har compileren et kontrollert høynivåprogram. Den kunne forsøkt å generere maskininstruksjoner direkte, men da ville flere forskjellige jobber blitt blandet sammen.

EduCPU senker derfor programmet til **EduIR**.

EduIR er en liten, pedagogisk, non-SSA mellomrepresentasjon. Den gjør operasjoner eksplisitte, men er fortsatt uavhengig av fysiske EduCPU-registre og instruksjonskoding.

Kjeden er:

```text
kontrollert EduC-AST
      ↓ lowering
EduIR
      ↓ kodegenerering
EduASM
```

Skillet lar oss undersøke *hva programmet gjør* før vi bestemmer *hvordan EduCPU skal gjøre det*.

## Kildevariabler og midlertidige verdier

Se på:

```c
byte main() {
    byte x = 40;
    return x + 2;
}
```

En forenklet EduIR-lignende visning er:

```text
const %t0, 40
copy x, %t0
const %t1, 2
add %t2, x, %t1
ret %t2
```

Midlertidige navn som `%t0` er verdier compileren lager. `x` er en variabel fra kildekoden.

Den nøyaktige IR-en som verktøyet produserer er autoritativ; denne forenklede visningen brukes for å lære rollene til operasjonene.

> **Hvordan vet EduCPU hva `%t2` betyr?**
>
> Det gjør den aldri. EduIR eksisterer bare inne i compileren. Kodegenereringen må velge konkret lagring og konkrete instruksjoner før CPU-en ser noe.

## Kontrollflyt blir eksplisitt

Høynivåkonstruksjoner blir også eksplisitte.

En EduC-`if` kan senkes til labels, et betinget hopp og jumps. En `while` blir labels og en kontrollflytkant bakover.

Dette er nyttig fordi backenden ikke lenger trenger å forstå hele syntaksen til en EduC-`while`. Den trenger bare å oversette et lite sett IR-operasjoner.

## Kodegenerering velger maskinressurser

EduCPU v0-backenden bruker en bevisst enkel strategi: parametere, kildevariabler og compiler-temporaries får hver sin én-byte stack slot.

Den genererte funksjonen får derfor en frame:

```asm
ENTER n
...
LEAVE n
RET
```

Verdier flyttes mellom stack slots og scratch-registre mens operasjonene utføres.

Dette er ikke ment som en optimaliserende register allocator. Det er ment å være forutsigbart og pedagogisk.

## Fra IR-addisjon til EduASM

Anta at EduIR skal addere to verdier.

Backenden kan måtte:

1. laste én verdi fra dens stack slot;
2. laste den andre i et annet register;
3. utføre `ADD`;
4. lagre resultatet i destination-slotten.

Én konseptuell IR-operasjon kan altså kreve flere maskininstruksjoner.

Det gir et viktig compilerpoeng:

```text
én kildeoperasjon ≠ én IR-operasjon ≠ én maskininstruksjon
```

## Funksjonskall møter ABI-en

Ved et kall må kodegenereringen gjøre abstrakte argumenter om til ABI-reglene fra leksjon 09.

Argumentene lastes i R0–R3, `CALL` overfører kontrollen og returverdien kommer i R0. Hvis IR-en trenger resultatet senere, lagrer backenden det i stack slotten som tilhører destination-verdien.

ABI-en er dermed kontrakten mellom compiler-generert caller- og callee-kode.

## Gjennomgått eksempel

Den CI-testede kilden er `course/examples/lesson12-ir-codegen.educ`:

```c
byte add_two(byte x) {
    byte y = x + 2;
    return y;
}

byte main() {
    return add_two(40);
}
```

Kurstesten kjører den ekte pipelinen gjennom:

```text
parse → semantisk analyse → EduIR → EduASM → objekt → link → kjøring
```

Den kontrollerer at EduIR inneholder funksjonene og aritmetikk-/call-operasjonene, at generert assembly inneholder frame- og call-mekanikk, og at sluttprogrammet returnerer 42.

## Undersøk stegene

For fixturen, sammenlign:

### EduC

Navn og strukturerte uttrykk er praktiske for mennesker.

### EduIR

Operasjoner, verdier og kontrollflyt er eksplisitte, men det finnes ingen fysiske stackadresser eller kodede opcodes.

### EduASM

ABI, registre, stack-frame-instruksjoner og konkrete kontrolloverføringer er synlige.

### Maskinkode

Navn som `x`, `%t0` og `add_two` trenger ikke lenger eksistere som kildespråkbegreper.

Hvert steg svarer på et forskjellig teknisk spørsmål.

## Oppgaver

### Forståelse

1. Hvorfor ikke generere maskinkode direkte fra AST-en?
2. Hva er forskjellen mellom en kildevariabel og en EduIR-temporary?
3. Kjører EduCPU noen gang EduIR?
4. Hvorfor kan én IR-operasjon kreve flere instruksjoner?
5. Hvor blir ABI-en først konkret i denne pipelinen?

### Praktisk

Endre `x + 2` til `x + 3`. Forutsi hvilke høynivåsteg som forblir strukturelt like og hvilken generert konstantbyte som må endres.

Legg til enda en lokal variabel. Undersøk hvordan den genererte stack-framen endrer seg.

### Utforsk selv

Skriv en EduC-`if` eller `while`. Sammenlign den strukturerte AST-en med eksplisitte EduIR-labels og branches, og deretter med EduASM-hoppinstruksjonene.

Finn én compiler-generert temporary og følg den fra EduIR til stack slotten som generert kode bruker.

## Sjekk forståelsen

Forklar grensen:

```text
EduIR: hvilke operasjoner og verdier som trengs
EduASM: hvordan EduCPU-ressurser utfører dem
```

Hvorfor er dette skillet nyttig både for compilerdesign og undervisning?

## Neste

Neste leksjon følger generert assembly inn i **objektfiler, relocations og linking**, der separat oversatte deler til slutt får konkrete adresser.
