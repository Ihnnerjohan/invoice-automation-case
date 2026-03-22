# Projektöverblick — Invoice Automation Case

Det här dokumentet beskriver **hur repot hänger ihop**, **vad som är byggt idag**, **hur det relaterar till Microsoft Power Platform i PRD:n**, och **hur du kan prata om det på intervju**. Det ersätter inte `README.md` eller `prd.md`, utan binder ihop dem.

---

## 1. Vad projektet är till för

**Affärsbilden (från `prd.md`):** Många organisationer tar emot fakturor i olika format. Man vill automatisera intag, extrahera strukturerad data med AI, validera mot affärsregler, upptäcka dubbletter och osäkra fall, logga beslut och kunna eskalera till mänsklig granskning.

**Ditt portfolio-mål:** Visa att du kan tänka i termer av *automation + AI + regler + spårbarhet + testning*, inte bara “en cool demo”.

**Vad som faktiskt finns i repot idag:** En **validerad Python-baseline** som:

- läser PDF-fakturor,
- extraherar fält med hjälp av OpenAI,
- normaliserar och validerar data,
- kör **regelbaserad** dubblettdetektering i batch-ordning,
- jämför resultat mot **ground truth** och skriver ut mätvärden.

**Microsoft-integration (SharePoint / OneDrive / Power Automate)** finns som **målbild** i PRD och scope-dokument, men ingår **inte** i den levererade lösningen här (ingen koppling till Power Platform i det här repot). **Eget frontend** är avstått tills vidare. På intervju kan du säga ungefär: *“Jag har skrivit PRD och tänkt igenom hur det skulle sitta i Power Platform, men det jag visar körbart och mätbart är en Python-baseline med AI-extrahering, regler och utvärdering.”*

---

## 2. Två “verkligheter” — håll isär dem i pitch

| Aspekt | PRD / `docs/01_scope.md` (målbild) | Repot idag (levererat) |
|--------|-----------------------------------|-------------------------|
| Intag | Övervakad mapp i OneDrive/SharePoint | Mapp `data/generated_invoices/` med PDF:er |
| Extrahering | AI Builder / liknande i flöde | `pdfplumber` + OpenAI API i `process_invoice.py` |
| Regler & routing | Villkor i Power Automate | Python-funktioner (`validate`, `detect_duplicate`, `classify`) |
| Loggning | SharePoint-lista eller Excel | CSV: `predictions.csv`, `comparison_results.csv` |
| Utvärdering | Testmatris + resultat | `docs/03_test_matrix.md`, `docs/04_test_results.md` + batch-eval |

**Intervjutips:** Beskriv först *affärsflödet* (intag → AI → regler → status → logg → review). Visa sedan *vad du konkret byggt och mätt* i Python. Koppla med: *“Samma logik kan flyttas till lågkod som conditions och parallel branches i Power Automate.”*

---

## 3. Katalogstruktur (vad ligger var)

| Sökväg | Roll |
|--------|------|
| `prd.md` | Produktkrav: problem, scope, komponenter (inkl. Power Platform), risker, leverabler. |
| `README.md` | Engelsk sammanfattning: pipeline, körinstruktion, resultat, begränsningar. |
| `docs/01_scope.md` | Kort svensk scope mot automation/AI/test/intervju. |
| `docs/03_test_matrix.md` | Övergripande testkategorier (clean, noisy, duplicates, osv.). |
| `docs/04_test_results.md` | Detaljerade testresultat och tolkning för baseline-pipelinen. |
| `docs/src/process_invoice.py` | Kärnan: PDF-text → AI-JSON → validering → dubblett → klassificering. |
| `docs/src/batch_eval.py` | Batch över alla PDF:er, merge mot ground truth, metrics, CSV-output. |
| `generate_invoices.py` | Skapar syntetiska PDF-fakturor + grundläggande ground truth (ReportLab). |
| `generate_noisy_variants.py` | Skapar brusiga bildvarianter + manifest (för framtida / Power-flödestest). |
| `data/generated_invoices/` | PDF-fakturor som pipelinen läser. |
| `data/expected_outputs/` | `invoice_ground_truth_clean.csv`, `predictions.csv`, `comparison_results.csv`, m.m. |
| `promts/` | Rollprompter för AI-assistenter (Planner, Builder, Reviewer, Tester) — **stöd för hur du arbetat**, inte runtime för pipelinen. |

**Obs — sökväg i dokumentation:** `README.md` och `docs/04_test_results.md` nämner `src/batch_eval.py`, men skripten ligger under **`docs/src/`**. När du kör lokalt: stå i `docs/src` och kör `python batch_eval.py`, eller uppdatera dokumentationen senare så sökvägarna stämmer.

---

## 4. Dataflöde steg för steg (den körbara pipelinen)

1. **Dataunderlag**  
   PDF:er i `data/generated_invoices/` (t.ex. `INV_CLEAN_*`, `INV_DUP_*`, `INV_SUSP_*`, `INV_NONDUP_*`). Dessa kan komma från `generate_invoices.py` och manuellt/kompletterande scenarier.

2. **Text från PDF**  
   `extract_text()` använder `pdfplumber` och samlar text per sida.

3. **Strukturerad extrahering**  
   `extract_fields_with_ai()` skickar text till OpenAI (modell enligt kod, t.ex. `gpt-4.1-mini`) och förväntar JSON med: `invoice_number`, `vendor`, `invoice_date`, `due_date`, `total_amount`.

4. **Normalisering av belopp**  
   `parse_amount()` hanterar olika format (mellanslag, tusentals-/decimaltecken, valutatecken).

5. **Validering**  
   `validate()` kräver att alla obligatoriska fält finns, att belopp går att tolka, och att total ≤ 50 000 (affärsregel i baseline).

6. **Dubblettdetektering** (endast om validering lyckades)  
   `detect_duplicate()` jämför mot tidigare **redan processade** fakturor i samma körning:
   - **Stark regel:** samma `invoice_number`.
   - **Fallback:** samma `vendor`, samma `invoice_date`, samma `total_amount` (±0,01).

7. **Klassificering**  
   `classify()`: dubblett eller ogiltig → `Needs review`; annars `Approved`.  
   *(PRD:n talar om fler statusar som “Suspected duplicate”; i Python-baseline mappas dubbletter till `Needs review` med tydlig `duplicate_reason`.)*

8. **Batch och utvärdering**  
   `batch_eval.py` sorterar filer, håller `seen_invoices`, skriver `predictions.csv`, joinar mot `invoice_ground_truth_clean.csv`, räknar fältaccuracy och dubblett-metriker, sparar `comparison_results.csv`.

---

## 5. Ground truth och vad som mäts

- **`data/expected_outputs/invoice_ground_truth_clean.csv`** innehåller per fil förväntade fält och kolumnen **`expected_is_duplicate`** (True/False) för utvärdering av dubblettlogiken.
- Jämförelsen är **deterministisk** per fält (och belopp med liten tolerans).
- Resultat och tolkning finns i **`docs/04_test_results.md`** (100 % på den kontrollerade datamängden — viktigt att på intervju nämna att datasetet är **litet och designat**, inte “produktionsrepresentativt”).

---

## 6. Hjälpfiler utanför själva pipelinen

- **`generate_invoices.py`:** Reproducerbara syntetiska fakturor + CSV med förväntade värden (bra för demo och regression).
- **`generate_noisy_variants.py`:** Bildbrus för robusthetstester; avsett att kunna matas in i ett framtida flöde (t.ex. OCR / AI Builder). Kräver extra beroenden (Pillow, ev. pdf2image/poppler).
- **`promts/*.md`:** Roller för planering, byggande, review och test — visar **arbetssätt** (hur du brutit ner case:et), inte en del av runtime.

---

## 7. Kända begränsningar (bra att nämna ärligt)

- Ingen **vendor-normalisering** eller fuzzy matchning.
- Dubbletter bara mot **samma batch** och **i minnet** — ingen databas över körningar.
- **Bearbetningsordning** påverkar vad som räknas som “tidigare” faktura.
- PDF:erna är **textbaserade**; skannade dokument utan textlager kräver OCR (uttryckligen “future improvement” i README).
- **OpenAI API-nyckel** sätts i **`.env`** lokalt (filen committas inte). Mall finns i **`.env.example`**.

---

## 8. Git och GitHub

I repot finns **`.gitignore`**. Den ignorerar bland annat:

- **`.env`** (hemligheter)
- **`data/expected_outputs/predictions.csv`** och **`comparison_results.csv`** (regenereras när du kör batch-evaluering)
- **`data/noisy_variants/`** (om du genererar brusfiler)
- Python-cache, virtuella miljöer, vanliga IDE/OS-filer

**`.env.example`** committas och visar vilka variabler som behövs. Din riktiga **`.env`** ligger i projektmappen lokalt men följer inte med till GitHub.

**Första gången på GitHub:**

1. Skapa ett **nytt tomt repository** på GitHub (utan README om du redan har filer lokalt), t.ex. `invoice-automation-case`.
2. Lokalt i projektmappen:

```bash
git init
git add .
git commit -m "Initial commit: invoice automation baseline"
git branch -M main
git remote add origin https://github.com/<ditt-användarnamn>/<repo-namn>.git
git push -u origin main
```

(Byt ut URL mot ditt konto/repo. Med SSH: `git@github.com:...`.)

3. Efter kloning: kopiera `.env.example` → `.env`, sätt `OPENAI_API_KEY`, kör `python docs/src/batch_eval.py` från projektroten så skapas predictions- och jämförelsefiler igen.

---

## 9. Muntlig berättelse (svenska, utan presentation)

Du kan berätta ungefär så här, i valfri ordning:

- **Varför:** Fakturaintag är ofta manuellt och felkänsligt; jag ville visa hur man kombinerar **AI för tolkning**, **tydliga affärsregler** och **testbarhet**.
- **Vad:** PDF-fakturor → text → modell extraherar fält → normalisering och kontroller → enkel dubblettlogik som går att förklara → status och CSV som går att granska.
- **Bevis:** Ground truth och batch-körning så jag kan visa **accuracy** och **dubblett-metriker** på en kontrollerad datamängd (liten men tydlig).
- **Vad som inte är med:** Ingen Power Platform-koppling och inget eget gränssnitt i den här versionen — det är medvetet, så fokus ligger på kärnflödet och mätbarheten.
- **Framåt:** Om man skulle produktionssätta: datalager över batchar, vendor-normalisering, OCR, och eventuellt samma regler i lågkod eller integration mot ekonomisystem.

---

## 10. Snabb “elevator pitch” (ca 1 minut)

*“Jag har tagit fram ett case kring AP-liknande fakturaintag: dokument in, strukturerad data ut, regler för kvalitet och dubbletter, och spårbara beslut. I PRD:n finns en målbild kring Power Platform och loggning i lista, men här har jag medvetet levererat en mätbär Python-baseline: text från PDF, AI-extrahering, validering, förklarbara dubblettregler och utvärdering mot ground truth. Det ger konkreta siffror och en tydlig berättelse om hur samma logik skulle kunna ligga i ett automationsflöde senare.”*

---

*Dokument för intervju, muntlig förklaring och orientering i repot.*
