This was taken from "8086 RELOCATABLE OBJECT MODULE FORMATS", Intel, 1981. Pages
100-104
---
***

# 1.2 Self-Relative Intersegment References

**Example:** Self-relative jump or call to another segment.

```text
A LLLLLLLLLLLLLL   <- PP            B LLLLLLLLLLLLLL   ^
  L            L                      L            L   |
  L +--------+ L                      L            L   d1
  L |  LOC   | |--------------------> L            L   |
  L +--------+ L                      L +--------+ L   V  <- PT
  L            L                      L | TARGET | L
  L            L                      L +--------+ L
  L            L                      L            L
  LLLLLLLLLLLLLL                      LLLLLLLLLLLLLL
```

Both LSEG's are created in the same translation.

## FIXUP REPRESENTATION:

*   **LOCATION:** OFFSET or LOBYTE
*   **PSEG:** SI(A) (this is the most common choice)
*   **TARGET:** SI(B),d1
    *   or SI(B) (see diagram and discussion following LOCATE OPERATION)

## LINK OPERATION:

If LSEG B combines then the LINKER will modify all fixups of the above form by changing `SI(B),d1` to `SI(B),d1+d2`.

```text
  B'
  ..............   ^
  .            .   | d2
  .            .   V
  B LLLLLLLLLLLLLL ^
  L              L | d1
  L +----------+ L V              =>  B
  L |  TARGET  | L                    ..............
  L +----------+ L                    L            L
  L              L                    L +--------+ L  <- PT
  L              L                    L | TARGET | L
  LLLLLLLLLLLLLL                      L +--------+ L
                                      L            L
                                      LLLLLLLLLLLLLL
```

100

## LOCATE OPERATION:

At LOCATE time these various sample possibilities can be detected:

```text
1. PPPPPPPPPPPPPPPPPP           2. PPPPPPPPPPPPPPPPPP
   P                P              P                P
   P LLLLLLLLLLLLLL P <- PP        P LLLLLLLLLLLLLL P <- PP
   P L A          L P              P L A          L P
   P L +--------+ L P              P L +--------+ L P
   P L |  LOC   | L P              P L |  LOC   | L P
   P L +--------+ L P              P L +--------+ L P
   P L            L P              P L            L P
   P LLLLL|LLLLLL L P              P LLLLL|LLLLLL L P
   P      |         P              P      |         P
   P LLLLL|LLLLLL L P              P LLLLL|LLLLLL L P
   P L B  V       L P              P L B  V       L P
   P L +--------+ L P <- PT        P L +--------+ L P <- PT
   P L | TARGET | L P              P L | TARGET | L P
   P L +--------+ L P              P L +--------+ L P
   P L            L P              P L            L P
   P LLLLLLLLLLLLLL P              P LLLLLLLLLLLLLL P
   PPPPPPPPPPPPPPPPPP              P P            P P
                                   L LLLLLLLLLLLLLL L
```

```text
3. PPPPPPPPPPPPPPPPPP           4. LLLLLLLLLLLLLL
   P                P              L B          L
   P LLLLLLLLLLLLLL P <- PP        L +--------+ L <- PT
   P L A          L P              L | TARGET | L
   P L +--------+ L P              L +--------+ L
   P L |  LOC   | L P              L            L
   P L +--------+ L P              LLLLLL|LLLLLLL
   P L            L P              PPPPPP|PPPPPPP
   P LLLLLLLLLLLLLL P              P LLLLL|LLLLLL P <- PP
   P                P              P L A  |     L P
   P LLLLLLLLLLLLLL P              P L +--------+ L P
   P L B  V       L P              P L |  LOC   | L P
   P L +--------+ L P <- PT        P L +--------+ L P
   P L | TARGET | L P              P L          L P
   P L +--------+ L P              P LLLLLLLLLLLLLL P
   P L            L P              P                P
   P LLLLLLLLLLLLLL P              P                P
   P P   V        P P              P                P
     L +--------+ L <- PT          P                P
     L | TARGET | L                P                P
     L +--------+ L                P                P
     LLLLLLLLLLLLLL                PPPPPPPPPPPPPPPPPP
```

```text
5. PPPPPPPPPPP!PPPPPP
   P          !     P
   P LLLLLLLLL!LLLL P <- PP
   P L B      V   L P
   P L +--------+ L P <- PT
   P L | TARGET | L P
   P L +--------+ L P
   P L            L P
   P LLLLL|LLLLLL L P
   P      |         P
   P LLLLL|LLLLLL L P
   P L A  |       L P
   P L +--------+ L P
   P L |  LOC   | L P
   P L +--------+ L P
   P L        !   L P
   P LLLLLLLLL!LLLL P
   P          !     P
   PPPPPPPPPPPPVPPPPPP
```

Diagrams 1 and 2 show valid fixups. In diagram 3, the TARGET is not in the defined PSEG. A warning will be given by LOCATE. In diagram 4, if the choice for PSEG is changed from SI(A) to SI(B) then the fixup can be made, as in diagram 5; if the displacement is greater than 32K a "clever" fixup, shown in diagram 5 as an exclamatory arrow, will be generated.

R & L attempts to inform the user of any erroneous self-relative references. The symbol being referenced must be within the defined PSEG independent of the bias value to be applied:

**EXAMPLES:** `JMP SYM + 10` or `JMP SYM - 2`

The symbol SYM will have an offset within its containing LSEG. The values 10 and -2 are biases. If the offset of SYM is added to the bias in LOCATION and the result overflows, it is not known whether this is due to the offset of SYM being greater than 64K or whether the bias (perhaps a negative or positive number) caused the overflow. If the bias caused the overflow then the reference is good according to R & L, if not, then SYM is not in the defined PSEG and the reference is invalid.

The solution to this problem is to maintain the offset of SYM independent of the bias. If the TARGET is specified in a primary way (e.g., `TARGET: SI(B),d`), then the offset will be maintained in the fixup record itself and will be added to LOCATION only at LOCATE time. If the TARGET is specified in a secondary way (e.g., `TARGET: SI(B)`), then the offset must be maintained in LOCATION itself, and R & L can do less checking on the correctness of the fixup.

If the LOCATION is an OFFSET (i.e., a full word, not just a byte) and the bias is known to be zero, then a fixup target of `TARGET: SI(B)` could be used instead of `TARGET: SI(B),d1`, without sacrificing any correctness checking.

# 3 Self-Relative Reference To An EXTERNAL Symbol

```text
A LLLLLLLLLLLLLL   <- PP       ? ............
  L            L                 .          .
  L +--------+ L                 . ........ . <- PT
  L |  LOC   |------------------->.  SYM   .
  L +--------+ L                 . ........ .
  L            L                 .          .
  LLLLLLLLLLLLLL                 ............
```

## FIXUP REPRESENTATION:

*   **LOCATION:** OFFSET or LOBYTE
*   **PSEG:** SI(A) (this is the most common choice)
*   **TARGET:** EI(SYM),0
    *   or EI(SYM) if the offset is to be maintained in LOCATION

Or if the reference is to the i'th element of an external array:

*   **LOCATION:** OFFSET or LOBYTE
*   **PSEG:** SI(A) this is the most common choice
*   **TARGET:** EI(SYM),i-1

## LINK OPERATION:

There are three ways in which an external self-relative reference may be resolved.

**CASE 1:** The EXTERNAL symbol (SYM) is found (by LINK) to be in the same LSEG as the LOCATION.

**CASE 2:** The EXTERNAL symbol (SYM) is found (by LINK) to be in a different LSEG, B.

**CASE 3:** The EXTERNAL symbol (SYM) is found (by LINK) to be absolute.

**CASE 1:** EXTERNAL symbol (SYM) is found (by LINK) to be in the same LSEG as the reference. The following four cases exist.

Assume that PSEG is specified as `PSEG: LOCATION`.

```text
PPPPPPPPPPPPPPPPPPPPP               PPPPPPPP!PPPPPPPPPPPP
P                   P               P       !           P
P                   P               P                   P
P                   P               P                   P
P LLLLLLLLLLLLLLLLL P               P LLLLLLLLLLLLLLLLL P
P L +-----------+ L P  <- PP        P L +-----------+ L P  <- PT
P L |    LOC    | L P               P L |  TARGET   | L P
P L +-----------+ L P               P L +-----------+ L P
P L               L P               P L       ^       L P
P L               L P               P L       |       L P
P L               L P               P L       |       L P
P L       V       L P               P L       |       L P
P L +-----------+ L P  <- PT        P L +-----------+ L P  <- PP
P L |  TARGET   | L P               P L |    LOC    | L P
P L +-----------+ L P               P L +-----------+ L P
P L               L P               P L               L P
P LLLLLLLLLLLLLLLLL P               P LLLLLLLLLLLLLLLLL P
PPPPPPPPPPPPPPPPPPPPP               PPPPPPPPPPPPPPPPPPPPP


PPPPPPPP^PPPPPPPPPPPP               PPPPPPPP!PPPPPPPPPPPP
P       !           P               P       !           P
P LLLLLL!LLLLLLLLLL P               P LLLLLL!LLLLLLLLLL P
P L     !         L P               P L     V         L P
P L +-----------+ L P  <- PP        P L +-----------+ L P  <- PT
P L |    LOC    | L P               P L |  TARGET   | L P
P L +-----------+ L P               P L +-----------+ L P
P L               L P               P L               L P
P L               L P               P L               L P
P L               L P               P L               L P
P L               L P               P L               L P
P L               L P               P L               L P
P L +-----------+ L P  <- PT        P L +-----------+ L P  <- PP
P L |  TARGET   | L P               P L |    LOC    | L P
P L +-----------+ L P               P L +-----------+ L P
P L     ^         L P               P L     !         L P
P LLLLLL!LLLLLLLLLL P               P LLLLLL!LLLLLLLLLL P
PPPPPPPP!PPPPPPPPPPPP               PPPPPPPPVPPPPPPPPPPPP
```

Depending on the absolute length of the arrow, LINK can perform a "normal" fixup or a "clever" fixup (exclamatory arrow). Note that even if the LSEG continues to grow in future LINKing, the fixup is OK as long as the LSEG remains less than 64K in length, which is enforced by LINK. Thus the fixup is completely resolved by LINK.
