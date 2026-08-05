# ChemLab Data Requirements

## Purpose

Store the institutional information needed to determine what a laboratory exercise requires, whether the laboratory is ready, and which safety guidance applies.

## Required Data

### Compounds and Inventory

For each chemical, store:

- Compound name, formula, CAS number, and common aliases when available.
- Available quantity and unit of measurement.
- Purity, lot or batch number, expiry date, and stock status when available.
- Physical storage location and any special storage requirements.
- A concise hazard summary.
- The date on which the stock information was last verified.

### Laboratory Procedures

For each supported exercise, store:

- Exercise and target-compound names.
- Required reagents, including quantities and units when available.
- Required equipment.
- The institution's procedure exactly as provided, without rewriting its steps.
- Safety precautions supplied with the procedure.
- Approval status, version, effective date, review date, and responsible department when available.
- A reference to the original institutional document.

Only procedures identified as approved and current may be presented as an institution-supported procedure. Older versions must remain distinguishable from the current version.

### Laboratory Equipment

For each piece or type of equipment, store:

- Equipment name and identifier when available.
- Available quantity.
- Operational status.
- Storage or laboratory location.
- The date on which its availability and condition were last verified.

### Safety Documents

For each safety document, store:

- Document title and type, such as institutional policy, SDS, or external safety guidance.
- Applicable compound and CAS number when relevant.
- Issuing organization and source link.
- Version, revision date, and effective date when available.
- Whether the document is approved by the institution.
- A reference to the complete source document.

Institutional policies must remain clearly distinguishable from supplier SDS documents and external safety guidance.

## Initial Inventory Records

| Compound | Formula | CAS number | Quantity | Purity | Location | Hazard summary |
|---|---|---|---:|---|---|---|
| Salicylic acid | C7H6O3 | 69-72-7 | 500 g | 99% | Shelf A-12 | Harmful if swallowed; causes serious eye damage |
| Acetic anhydride | C4H6O3 | 108-24-7 | 1000 g | 99% | Flammable Cabinet C-2 | Flammable, corrosive, and harmful if inhaled |
| p-Aminophenol | C6H7NO | 123-30-8 | 250 g | 98% | Shelf B-4 | Harmful if swallowed; suspected of causing genetic defects |
| Aspirin | C9H8O4 | 50-78-2 | 0 g | Out of stock | Shelf A-1 | Harmful if swallowed |
| Acetaminophen | C8H9NO2 | 103-90-2 | 10 g | 99% | Shelf A-2 | Harmful if swallowed |

## Initial Procedure Records

### Aspirin

- **Required reagents:** Salicylic acid and acetic anhydride.
- **Procedure:** React salicylic acid with acetic anhydride in the presence of phosphoric acid as a catalyst. Heat in a water bath at 50°C for 15 minutes. Allow to cool, add ice water to crystallize, filter under vacuum, and recrystallize from ethanol.
- **Safety precautions:** Perform inside a fume hood. Acetic anhydride is corrosive and flammable. Salicylic acid is an irritant.

### Acetaminophen

- **Required reagents:** p-Aminophenol and acetic anhydride.
- **Procedure:** Suspend p-aminophenol in water, add acetic anhydride, and heat gently to dissolve. Stir for 10 minutes, cool in an ice bath to crystallize, filter, and wash the crystals with cold water.
- **Safety precautions:** Perform inside a fume hood. Acetic anhydride is corrosive and flammable. p-Aminophenol is harmful.

## Data Quality Rules

- Missing information must be stored and reported as unknown rather than inferred.
- Quantities must always include a unit of measurement.
- Chemical records must use the CAS number when available to avoid ambiguity.
- Procedure wording, approval status, and version information must be preserved.
- Expired, unavailable, insufficient, outdated, or unverified resources must be identifiable.
- Every policy, SDS, and external safety document must retain its source and revision information.
- The assistant may read this information but must not create, update, or delete institutional records.
