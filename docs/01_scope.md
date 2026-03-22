# 01 Scope

## Projektmål
Bygga ett realistiskt invoice automation-case i Power Automate med AI-stöd och regelmotor för att visa förmåga inom:
- processautomation
- AI-användning i verksamhetsflöden
- validering och riskhantering
- testning och dokumentation
- konsultmässig kommunikation

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
- Power Automate-flöde för intake
- AI extraction eller simulerad extraction
- Affärsregler för validering
- Klassificering och routing
- Loggning i SharePoint eller Excel
- Enkel human review
- Daily summary
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
- Flow 1: intake + extraction + loggning
- regelmotor för routing
- daily summary flow
- enkel review-process
- testmatris
- testresultat
- intervju-pitch

## Framgångskriterier
Lösningen ska minst kunna:
- processa 30+ fakturor
- logga utfall strukturerat
- särskilja clean, noisy, duplicate och suspicious fall
- visa mänsklig review för osäkra fall
- förklaras tydligt på 1–3 minuter

## Risker
- AI Builder kan vara begränsad av credits/licens
- Power Platform-miljön kan ge setupproblem
- Tidsramen är kort
- Vissa dokumenttyper kan vara svåra att extrahera korrekt

## Fallback-strategi
Om AI-extraction inte fungerar fullt ut:
- simulera extraction från metadata/ground truth
- fortsätt bygga routing, regler, loggning och review
- var tydlig i intervjun om vad som var simulerat
