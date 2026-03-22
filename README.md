# Invoice Automation Case

En Python-baserad pipeline för fakturaautomation som extraherar strukturerad data från PDF-fakturor, validerar data, upptäcker dubbletter och utvärderar resultat mot ground truth.

Projektet är en **validerad baslinje** med genomtestat beteende och mätbara resultat.

---

## Projektöversikt

Systemet bearbetar faktura-PDF:er och utför:

1. Textextraktion från PDF-fakturor
2. AI-baserad fältextraktion
3. Datanormalisering och validering
4. Regelbaserad dubblettdetektering
5. End-to-end-utvärdering mot ground truth

---

## Huvudfunktioner

- PDF-textextraktion med `pdfplumber`
- AI-baserad strukturerad fältextraktion
- Beloppsnormalisering över olika format
- Valideringsregler för korrekta fakturor
- Förklarlig, regelbaserad dubblettdetektering
- Batchkörning och utvärderingspipeline
- Jämförelse mot ground truth med mätvärden

---

## Pipeline

### 1. Textextraktion
Extraherar råtext från faktura-PDF:er.

### 2. AI-fältextraktion
Extraherar:

- `invoice_number`
- `vendor`
- `invoice_date`
- `due_date`
- `total_amount`

### 3. Normalisering
Hanterar bland annat format som:

- 16,444.59
- 34 930,64
- strängar med valuta

### 4. Validering
Regler:

- alla fält måste finnas
- beloppet måste gå att tolka
- belopp ≤ 50 000

### 5. Dubblettdetektering

Primär regel:

- samma `invoice_number`

Reservregel:

- samma leverantör (`vendor`)
- samma `invoice_date`
- samma `total_amount` (±0,01)

### 6. Klassificering

vid dubblett → `Needs review`  
vid ogiltig data → `Needs review`  
annars → `Approved`

---

## Så kör du projektet

1. Installera beroenden:

```bash
pip install -r requirements.txt
```

2. Kopiera miljömallen och lägg in din API-nyckel (`.env` versionshanteras inte):

```bash
cp .env.example .env
```

3. Sätt `OPENAI_API_KEY` i `.env` (laddas automatiskt via `python-dotenv`), eller exportera variabeln i terminalen.

4. Från projektroten:

```bash
python docs/src/batch_eval.py
```

Detta bearbetar:

```text
data/generated_invoices/
```

och skapar:

```text
data/expected_outputs/predictions.csv
data/expected_outputs/comparison_results.csv
```

---

## Resultat

### Extraktionsnoggrannhet

- `invoice_number`: 100 %
- `vendor`: 100 %
- `invoice_date`: 100 %
- `due_date`: 100 %
- `total_amount`: 100 %
- sammantaget per dokument: 100 %

### Dubblettdetektering

- precisionsgrad: 100 %
- återfinningsgrad (recall): 100 %
- träffsäkerhet (accuracy): 100 %

- sanna positiva: 4
- falska positiva: 0
- falska negativa: 0
- sanna negativa: 12

### Fördelning per regel

- `invoice_number`: 3
- `vendor_amount_date`: 1

---

## Dataset

- 16 fakturor totalt
- rena fakturor
- dubbletter
- reservfall för dubblett (vendor + belopp + datum)
- negativ kontroll
- misstänkta fall

---

## Begränsningar

- ingen leverantörsnormalisering
- ingen fuzzy matchning
- ingen persistens mellan batcher
- beroende av ordning i batchen
- litet, kontrollerat dataset

---

## Framtida förbättringar

- leverantörsnormalisering
- fuzzy matchning
- persistenslager
- OCR-stöd
- större dataset
- utökad bedrägeri-/avvikelsehantering

---

## Sammanfattning

Projektet visar:

- en komplett pipeline för fakturahantering
- fullt validerat beteende
- förklarlig dubblettdetektering
- mätbara utvärderingsresultat

Det är tänkt att vara **enkelt, testbart och redo att visa i intervju**.
