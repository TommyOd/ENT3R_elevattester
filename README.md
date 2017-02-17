# Elevattester til ENT3R - automatisk
Programvaren bruker Python og LaTeX til å generere eleverattester. For å se hvordan dette ser ut, se filen `eksempel.pdf`.
## Hvordan installere
### Python og LaTeX
Først og fremst må du ha Python og LaTeX på systemet ditt.

 * **Python**: Last ned [Anaconda](https://www.continuum.io/downloads) distributsjonen av Python, versjon 3.x
 * **LaTeX**
 	* Windows: [MikTeX](https://miktex.org/) + [TeXstudio](http://texstudio.sourceforge.net/)
 	* Mac: [MacTeX](https://tug.org/mactex/) + [TeXstudio](http://texstudio.sourceforge.net/)
 
 ### Dette programmet
 Last så ned disse filene fra GitHub. Du må gjøre følgende endringer:
 * I filen `template/attest_template.tex` må du endre årstall, institutisjon, etc.
 * Du må legge til logoer for din institusjon i `template/figs`. Dersom du buker andre filnavn enn de som er, må du inn i filen `template/attest_template.tex` og endre filnavnene.
 * I filen `main.py` må du endre de første linjene (se nederst på siden).
 	* Sett `USERNAME` og `PASSWORD` til dine verdier for reg-siden.
 	* Sett kravene for at attest skal genereres
 		*  `MIN_OPPMOTER` er minste antall oppmøter som kreves
 		*  `MIN_PROSENT` er prosent oppmøter (i tidsrommet *etter* første gang eleven møtte)
 		*  Du kan eksempelvis sette `MIN_OPPMOTER = 1` og `MIN_PROSENT = 10`  for å generere attest til "alle"
    *  Sett så årene og ukene det har vært grupper via `WEEKS` variabelen

Åpne programmet Spyder (som er inkludert i [Anaconda](https://www.continuum.io/downloads)), åpne `main.py` i Spyder og trykk F5 eller den grønne pilen øverst for å kjøre programmet.
Programmet lager en mappe som heter `generated`, og der havner attestene.

## Kjøretid
På et prosjekt med ~470 elever og 67 genererte attester var kjøretiden 6min 7s.
* 6 sekunder per attest.
* 0.78 sekunder per elev.

## Linjer som må endres i `main.py`
```python
USERNAME = r'email' # Endre til din epost på reg-siden
PASSWORD = r'password' # Endre til ditt passord på reg-siden
MIN_OPPMOTER = 8 # Minste antall oppmøter som krever for å få attest
MIN_PROSENT = 50 # Minste antall prosent som kreves. Prosent regnes av mulige oppmøter etter første oppmøte, ikke av hele året. Dersom Lise begynner i uke 4 og ENT3R slutter i uke 20, og hun møter alle ukene, har hun 100% oppmøte.
WEEKS = collections.defaultdict(lambda : None) # Ikke endre dette.
WEEKS[2016] = [36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46] # Endre til gjeldende uker i år 2016 
WEEKS[2017] = [4, 5, 6, 7] # Endre til gjeldende uker i år 2017 
```

Mvh,
Tommy O.