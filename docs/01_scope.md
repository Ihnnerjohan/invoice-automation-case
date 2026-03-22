# 01 Scope

## Projektmål
Bygga ett realistiskt **invoice automation**-case med AI-stöd och regelmotor för att visa förmåga inom:
- processautomation
- AI-användning i verksamhetsflöden
- validering och riskhantering
- testning och dokumentation
- konsultmässig kommunikation

**Ursprunglig riktning** var Microsoft **Power Automate** med intag i **SharePoint/OneDrive** och extraktion via **AI Builder** eller **Azure Document Intelligence**. På grund av miljö- och licensbegränsningar (tenant utan full provisioning, ingen aktiv SharePoint-site, saknad AI Builder-licens, ingen Azure-prenumeration) har den **levererade referensimplementationen** byggts i **Python** med samma logiska pipeline och mätbar utvärdering. Se `README.md` och `prd.md` (avsnitt om dokumentstatus) för formulering mot intervju.

## Affärsproblem
Ekonomi- och operationsfunktioner får in fakturor i många format och kvalitetsnivåer. Den manuella hanteringen är tidskrävande och riskerar:
- felregistrering
- dubbletter
- missade avvikelser
- lång ledtid
- dålig spårbarhet

## Scope in
- Syntetiska fakturor
- Flera typer av inputfiler
- **Levererat:** Python-pipeline för intag från katalog (batch), extraktion, validering, dubbletter och klassificering
- **Målbild Power Platform (ej slutfört som integration):** flöde för intake, loggning i SharePoint/Excel, daglig sammanfattning
- AI-baserad extraktion (i repot: OpenAI; i målbilden: AI Builder / Document Intelligence)
- Affärsregler för validering
- Klassificering och routing (status + orsak i kod/CSV)
- Enkel human review (som designkoncept via `Needs review`)
- Testmatris och testresultat
- Intervjumaterial

## Scope out
- ERP-integration
- Skarp betalningshantering
- Produktionssäkerhetsmodell
- Fullständig Power Apps-front
- Avancerad bedrägerimodell

## Primära leverabler
- `prd.md`
- syntetiskt fakturadataset
- ground truth CSV
- **Levererat:** Python-moduler under `docs/src/`, batch + eval, CSV-resultat
- **Ej levererat som produktionsflöde:** separata Power Automate-flöden (intentionen dokumenteras i PRD)
- regelmotor för routing (i Python)
- testmatris
- testresultat
- intervju-pitch

## Framgångskriterier
Lösningen ska minst kunna:
- processa 30+ fakturor *(Python-batch kan köras upprepat; nuvarande demo-dataset är mindre men utbyggbart)*
- logga utfall strukturerat *(CSV + terminal)*
- särskilja clean, noisy, duplicate och suspicious fall *(dataset-design)*
- visa mänsklig review för osäkra fall *(via status/orsak)*
- förklaras tydligt på 1–3 minuter

## Risker
- AI-tjänster kan kräva nycklar, kostnad eller begränsad åtkomst
- **Power Platform-miljön gav i praktiken spärrar** (licens/provisioning) — dokumenterat i PRD
- Tidsramen är kort
- Vissa dokumenttyper kan vara svåra att extrahera korrekt
- PDF-verktyg (t.ex. pdf2image/Poppler) kan kräva lokal installation vid variantgenerering

## Fallback-strategi
När Power Platform-integration inte var möjlig end-to-end:
- **Primär fallback:** Python-pipeline med OpenAI + regler + ground truth-eval *(nuvarande repo)*
- Var tydlig i intervjun om **avsikt** (Power Automate/Azure) vs **leverans** (Python-referens)
- Om AI-extraktion inte fungerar: simulera från metadata/ground truth *(enligt PRD)*
