# xlcrf

Un tool (libreria Python + script) per creare file utili per la
raccolta dati (con validazione dell'input) a partire da una descrizione
della struttura del dataset desiderato (mediante un file `.xlsx`).

## Utilizzo
Lo strumento si può utilizzare via web [qui](https://share.streamlit.io/lbraglia/webxlcrf/main) oppure da linea di comando, come segue:
```
xlcrf file_struttura.xlsx
```
Questo produrrà `file_struttura_CRF.xlsx`.

## File di struttura

Si tratta di un file `.xlsx` che specifica la struttura del dataset
desiderato. [Qui](https://github.com/lbraglia/xlcrf/tree/main/examples)
vi sono alcuni esempi, mentre [questo](https://github.com/lbraglia/xlcrf/raw/main/examples/blank_template.xlsx) è un template bianco
utilizzabile.

In generale un file struttura si compone di:
- tanti fogli quanti sono quelli desiderati nel file finale
- un foglio `modalita_output` per gli elenchi/risposte a tendina che si 
  desidereranno implementare;
- un foglio `modalita_struttura`, di servizio ed ignorabile
  (utilizzando il template).

### Compilazione delle schede


### Compilazione `modalita_output`


