# 11 — EduC, AST og semantisk analyse

## Læringsmål

Etter denne leksjonen skal du kunne skille tokens, syntaks og semantikk, lese en liten EduC-AST, forklare hva parseren gjør og identifisere feil som semantisk analyse finner etter parsing.

## Fra tegn til struktur

Se på:

```c
byte main() {
    byte x = 40;
    return x + 2;
}
```

For oss ser dette allerede strukturert ut. For compileren starter det som tegn.

Frontenden gir gradvis tegnene mening:

```text
tegn i kildekoden
      ↓ lexer
tokens
      ↓ parser
AST
      ↓ semantisk analyse
kontrollert AST/program
```

Hvert steg svarer på et forskjellig spørsmål.

## Tokens

Lexeren gjenkjenner nyttige deler av teksten.

For deler av eksemplet får vi begreper som:

```text
byte   main   (   )   {   byte   x   =   40   ;
return x      +   2   ;   }
```

Et token forteller hvilken type leksikalsk element som ble funnet. Det beskriver ennå ikke hele programstrukturen.

## AST-en

Parseren leser tokens etter EduC-grammatikken og bygger et **Abstract Syntax Tree**.

En forenklet visning av eksemplet er:

```text
Program
└── Function main : byte
    ├── VarDecl x : byte
    │   └── Literal 40
    └── Return
        └── Add
            ├── Name x
            └── Literal 2
```

Treet er *abstract* fordi tegnsetting som trengs for å skrive kildekoden ikke nødvendigvis trenger egne noder. Det viktige er programstrukturen.

> **Hvordan vet EduCPU at `x + 2` er en addisjon?**
>
> Det gjør den ikke. Parseren gjenkjenner strukturen i kildespråket. Mye senere oversetter lowering og kodegenerering strukturen til operasjoner som til slutt blir en ADD-instruksjon eller en tilsvarende maskinkodesekvens.

## Syntaks kontra semantikk

En parser svarer omtrent på:

> Har denne teksten formen til et EduC-program?

Semantisk analyse spør:

> Gir navnene, typene, kallene og returverdiene mening etter EduC-reglene?

For eksempel:

```c
byte main() {
    return missing + 2;
}
```

kan ha gyldig grammatisk struktur samtidig som den refererer til et ukjent navn. Det er en semantisk feil.

## Hva EduC sin semantiske analyse kontrollerer

EduC v0 kontrollerer blant annet:

- funksjonsnavn kan ikke dupliseres;
- lokale navn kan ikke dupliseres innen tillatt scope;
- refererte navn må eksistere;
- funksjonskall må gå til deklarerte funksjoner;
- antall argumenter og typene deres må stemme;
- assignments må følge typene;
- return-uttrykk må passe funksjonens returtype;
- non-void-funksjoner må konservativt returnere på alle paths.

Det viktige poenget er at **gyldig syntaks ikke er det samme som et gyldig program**.

## Typer i EduC v0

EduC har bevisst et lite typesystem:

- `byte`: unsigned 8-bits verdi;
- `bool`: logisk verdi representert som 0 eller 1;
- `void`: kun returtype for funksjoner.

Det lille språket holder compileren oversiktlig. Vi kan lære hele regelsettet i stedet for å skjule kompleksitet bak et stort produksjonsspråk.

## Gjennomgått eksempel

Den CI-testede kildefilen er `course/examples/lesson11-ast-semantics.educ`:

```c
byte add(byte a, byte b) {
    return a + b;
}

byte main() {
    byte answer = add(20, 22);
    return answer;
}
```

Kurstesten parser akkurat denne filen, kontrollerer semantisk gyldighet og undersøker AST-strukturen.

Den lager også en bevisst ugyldig variant med et ukjent navn og verifiserer at semantisk analyse avviser den.

Det er viktig: leksjonen testes mot den ekte frontenden i stedet for et håndskrevet bilde som kan drive bort fra implementasjonen.

## Observer den ekte compileren

Bruk EduC-CLI-en til å undersøke stegene separat:

```text
tokens → AST → semantisk kontroll
```

Sammenlign kildekoden med AST-en. Finn:

1. tegnsetting som forsvinner fra AST-en;
2. navn som beholdes;
3. nesting av uttrykk;
4. funksjons- og returtyper.

Introduser deretter én feil om gangen og finn hvilket steg som avviser den.

## Oppgaver

### Forståelse

1. Hva produserer lexeren?
2. Hva produserer parseren?
3. Hvorfor kalles treet abstract?
4. Gi et eksempel på EduC som er syntaktisk gyldig, men semantisk ugyldig.
5. Hvorfor skjer typekontroll før maskinkoden finnes?

### Praktisk

Endre fixturen slik at `main` deklarerer en `bool` og returnerer den fra en `byte`-funksjon. Forutsi om parsing lykkes og om semantisk analyse lykkes.

Kall deretter `add` med ett argument i stedet for to.

### Utforsk selv

Ta et nestet uttrykk som:

```c
return a + b - 1;
```

Forutsi AST-formen før du ber compileren vise den.

Endre parentesene og observer hvordan treet endrer seg.

## Sjekk forståelsen

Fullfør spørsmålene:

```text
lexer:    hvilke ______ finnes?
parser:   hvordan er de ______?
semantic: gir strukturen ______ etter språkreglene?
```

Hvorfor er det nyttig å holde disse jobbene adskilt?

## Neste

Neste leksjon senker det kontrollerte programmet til **EduIR** og viser hvordan høynivåuttrykk blir eksplisitte, maskinuavhengige operasjoner klare for kodegenerering.
