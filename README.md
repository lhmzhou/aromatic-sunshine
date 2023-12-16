# aromatic-sunshine

The [Centers for Medicare and Medicaid Services](https://www.cms.gov/) have mandated that hospitals, in accordance with [45 CFR §180.50](https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-E/part-180/subpart-B/section-180.50), disclose a price list on their websites. The guidelines explicitly direct hospitals to present these lists in two specific formats:

- As a comprehensive machine-readable file containing details of all items and services.
- In a user-friendly display of services that are easily understandable and navigable for consumers seeking shoppable services.

### Supplied Data

Each hospital is identified by the NPI.

```
{"cpt":"0031A","cash":12.8,"gross":56.53}
```
- __cpt__: the code from the AMA that corresponds to this billed service
- __gross__: this is often the top line item that the hospital never actually charges  
- __cash__: this is the self-pay discounted price you would pay without insurance