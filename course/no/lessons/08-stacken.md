# 08 — Stacken

## Læringsmål

Etter denne leksjonen skal du kunne forklare hva en stack er, beskrive LIFO-rekkefølge, følge SP mens PUSH og POP kjører, finne de eksakte minneadressene som brukes og forklare hvorfor balansert stackbruk er viktig.

## Hva er en stack?

En stack er en disiplinert måte å bruke minnet til midlertidig lagring.

Regelen er **last in, first out (LIFO)**. Hvis du pusher A og deretter B, popper du B før A.

EduCPU bruker det 16-bits **SP**-registeret til å angi toppen av stacken.

Etter reset:

```text
SP = 0xFF00
```

Stacken vokser mot lavere adresser.

## PUSH

I EduCPU:

```asm
PUSH R0
```

utfører konseptuelt:

```text
SP = SP - 1
MEM[SP] = R0
```

Hvis SP starter på `0xFF00` og R0 inneholder `0x2A`:

```text
før:   SP = FF00
etter: SP = FEFF
       MEM[FEFF] = 2A
```

Dekrementeringen skjer før skrivingen.

## POP

```asm
POP R1
```

utfører konseptuelt:

```text
R1 = MEM[SP]
SP = SP + 1
```

Hvis SP er `0xFEFF` og byten der inneholder `0x2A`, blir R1 `0x2A` og SP går tilbake til `0xFF00`.

> **Hvordan vet EduCPU det?**
>
> Den vet ikke at en byte er «midlertidige data». PUSH og POP har presise arkitektoniske regler for SP og minnet. LIFO-oppførselen oppstår fordi PUSH dekrementerer SP før skriving, mens POP leser før SP inkrementeres.

## Gjennomgått eksempel

```asm
MOVI R0, 0x11
MOVI R1, 0x22
PUSH R0
PUSH R1
POP R2
POP R3
HALT
```

Følg stacken:

```text
reset          SP=FF00
PUSH R0        SP=FEFF  MEM[FEFF]=11
PUSH R1        SP=FEFE  MEM[FEFE]=22
POP R2         R2=22    SP=FEFF
POP R3         R3=11    SP=FF00
```

R2 får verdien som ble pushet sist. Det er LIFO.

Legg merke til at POP ikke sletter den gamle minnebyten. Den endrer SP slik at byten ikke lenger er en del av den aktive stacken.

## Stackbalanse

En nyttig invariant er:

```text
midlertidige pushes = tilsvarende pops
```

Hvis en kodebit starter med SP=`0xFF00` og bare bruker stacken til midlertidig lagring, bør den normalt gjenopprette SP til `0xFF00` før den avslutter.

Ubalanserte stackoperasjoner kan føre til at senere kode leser feil bytes eller overskriver data uventet.

Dette blir spesielt viktig når funksjoner begynner å bruke stacken.

## Minne, ikke magi

Stacken er ikke et separat fysisk lagringssystem i EduCPU-arkitekturen. Den er vanlig minne som brukes etter regler knyttet til SP.

Dermed kan vi undersøke både:

- SP, som forteller hvor den aktive stacken begynner;
- minnet rundt SP, som viser de lagrede bytene.

Denne synligheten er svært nyttig ved debugging.

## Kjør og observer

Den CI-testede fixturen er `course/examples/lesson08-stack.eduasm`.

Før du kjører den, tegn adressene `0xFEFE`, `0xFEFF` og `0xFF00`. Forutsi SP og minnebytene etter hver PUSH og POP.

Testen kontrollerer de eksakte mellomtilstandene på stacken, ikke bare sluttverdiene i registrene.

## Oppgaver

### Forståelse

1. Hva betyr LIFO?
2. Hvilken retning vokser EduCPU-stacken?
3. Skriver PUSH før eller etter at SP dekrementeres?
4. Inkrementerer POP SP før eller etter at minnet leses?
5. Sletter POP minnebyten den leser?

### Praktisk

Start med R0=`0xAA`, R1=`0xBB` og SP=`0xFF00`.

Forutsi SP og minnet etter:

```asm
PUSH R0
PUSH R1
POP R4
```

Hva ligger fortsatt på den aktive stacken?

### Utforsk selv

Push tre forskjellige verdier. Pop bare to og halt.

Sammenlign sluttverdien til SP med resetverdien. Legg deretter til den manglende POP-en og se hvordan stackbalansen gjenopprettes.

## Sjekk forståelsen

Fullfør transformasjonene:

```text
PUSH Rx: SP → ______ ; MEM[SP] → ______
POP  Rx: Rx → ______ ; SP → ______
```

Hvorfor gir dette paret naturlig LIFO-rekkefølge?

## Neste

En stack blir langt kraftigere når CPU-en kan lagre hvor programmet skal returnere. Neste leksjon: **funksjoner, CALL/RET og EduCPU ABI**.
