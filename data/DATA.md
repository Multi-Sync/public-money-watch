# The data

`dol_contracts_fy2024.csv`: every U.S. Department of Labor contract award with at least one
action between October 1, 2023 and September 30, 2024 (fiscal year 2024). One row per award.

- Rows: 2,358 awards, $16.18 billion obligated in total
- Source: USAspending.gov, Custom Award Download, pulled 2026-09-29
- SHA-256: `289d94941c10e9e085d8c71bca2fd1e4089873f690637818104dc27313718c39`
- Request (rebuild it with `python3 fetch_data.py`; a fresh pull will differ a little):

```
POST https://api.usaspending.gov/api/v2/download/awards/
{"filters": {"award_type_codes": ["A","B","C","D"],
             "agencies": [{"type": "awarding", "tier": "toptier", "name": "Department of Labor"}],
             "time_period": [{"start_date": "2023-10-01", "end_date": "2024-09-30"}]},
 "file_format": "csv"}
```

The download has 286 columns; 34 are kept here, sorted by `contract_award_unique_key`.
U.S. federal spending data is a work of the U.S. government and is not under copyright.

## Things that will trip you

- **Blank is not zero.** `number_of_offers_received` is blank on 648 awards (27%). The office did
  not report it. Do not read blank as one bidder or as none.
- **One row is the whole award, not one payment.** Amounts are totals across the award's life as
  USAspending reports them, not only what was spent in FY2024.
- **Most awards sit under a bigger vehicle.** 864 are delivery orders and 720 are BPA calls; their
  `parent_award_id_piid` points to the contract or agreement they were ordered under.
- **Competition codes in this file:** A full and open 1,298; D full and open after exclusion of
  sources 429; C not competed 221; B not available for competition 167; F competed under
  simplified acquisition 135; G not competed under simplified acquisition 106; blank 2.
- **71 awards carry COVID-19 supplemental money** (`obligated_amount_from_COVID-19_supplementals`).
- **Recipients are public.** Names and UEIs are in the public record. That does not make a
  flagged recipient a wrongdoer. See the rules in README.md.
- **Some recipients are people, not companies.** 18 of the 811 recipients here are individuals
  holding 24 awards, mostly sole proprietors: arbitrators, expert witnesses and the like.
  `check.py` warns when you flag one. The award is public; the person is still a person.

## Columns

Definitions are quoted from USAspending's data dictionary
(https://api.usaspending.gov/api/v2/references/data_dictionary/).

| Column | Definition |
|---|---|
| `contract_award_unique_key` | Derived unique record key used by the Broker to identify the prime award. Note that this element is different from the AssistanceTransactionUniqueKey and the ContractTransactionUniqueKey in that it identifies the award, not a specific transaction within the award. For contract records, this element is a concatenation of PIID, agencyID, ParentAwardId, and Referenced IDV Agency Identifier. For financial assistance records, this element is a concatenation of FAIN, URI, and AwardingSubTierAgencyCode. In both cases a single underscore ('_') character is inserted in between each element value. And in both cases if an element value is blank then the values used is "NONE". |
| `award_id_piid` | The unique identifier of the specific award being reported. |
| `parent_award_id_piid` | The identifier of the procurement award under which the specific award is issued, such as a Federal Supply Schedule. This data element currently applies to procurement actions only. |
| `usaspending_permalink` | This is Usaspending Permalink |
| `award_type` | Description tag (by way of the FPDS Atom Feed) that explains the meaning of the code provided in the ContractAwardType Field. |
| `prime_award_base_transaction_description` | For procurement awards: Per the FPDS data dictionary, a brief, summary level, plain English, description of the contract, award, or modification. Additional information: the description field may also include abbreviations, acronyms, or other information that is not plain English such as that required by OMB policies (CARES Act, etc).  For financial assistance awards: A plain language description of the Federal award purpose; activities to be performed; deliverables and expected outcomes; intended beneficiary(ies); and subrecipient activities if known/specified at the time of award. |
| `recipient_name` | The name of the awardee or recipient that relates to the unique identifier. For U.S. based companies, this name is what the business ordinarily files in formation documents with individual states (when required). |
| `recipient_uei` | The Unique Entity Identifier (UEI) for an awardee or recipient. A UEI is a unique alphanumeric code used to identify a specific commercial, nonprofit, or business entity. |
| `recipient_parent_name` | The name of the ultimate parent of the awardee or recipient. |
| `recipient_state_code` | United States Postal Service (USPS) two-letter abbreviation for the state or territory in which the awardee or recipient’s legal business address is located. Identify States, the District of Columbia, territories (i.e., American Samoa, Guam, Northern Mariana Islands, Puerto Rico, U.S. Virgin Islands) and associated states (i.e., Republic of the Marshall Islands, the Federated States of Micronesia, and Palau) by their USPS two-letter abbreviation for the purposes of reporting. |
| `awarding_sub_agency_name` | Name of the level 2 organization that awarded, executed or is otherwise responsible for the transaction. |
| `awarding_office_name` | Name of the level n organization that awarded, executed or is otherwise responsible for the transaction. |
| `total_obligated_amount` | This is a system generated element providing the sum of all the amounts entered in the "Action Obligation" field for a particular PIID and Agency. Example: Contract has 9 Modifications under "Transaction Number" as '1' and 9 modifications with the same PIID under "Transaction Number" as '2'. The base contracts and all the modifications have "Action Obligation" as $10 each. The value for the field "Total Obligated Amount" when the either of the bases or the modification is retrieved through atom feeds will be $200 ($100 under Transaction Number 1 + $100 under Transaction Number 2). "Total Obligated Amount" is generated irrespective of the "Transaction Number" on the Awards. |
| `obligated_amount_from_COVID-19_supplementals` | Represents the obligated amount funded from COVID-19 supplementals. |
| `current_total_value_of_award` | For procurement, the total amount obligated to date on a contract, including the base and exercised options. |
| `potential_total_value_of_award` | For procurement, the total amount that could be obligated on a contract, if the base and all options are exercised. |
| `period_of_performance_start_date` | For procurement awards: Per the FPDS data dictionary, the date that the parties agree will be the starting date for the contract's requirements. This is the period of performance start date for the entire contract period, this date does not reflect period of performance per modification, but rather the start of the entire contract period of performance. This data element does NOT correspond to FAR 43.101 or 52.243 and should not be mapped to those fields in your contract writing systems.   For grants and cooperative agreements: The Period of Performance is defined in the 2 CFR 200 as the total estimated time interval between the start of an initial Federal award and the planned end date, which may include one or more funded portions, or budget periods.  For all other financial assistance awards: The date on which, for the award referred to by the action being reported, awardee effort begins or the award is otherwise effective. |
| `period_of_performance_current_end_date` | For procurement awards: The contract completion date based on the schedule in the contract. For an initial award, this is the scheduled completion date for the base contract and for any options exercised at time of award. For modifications that exercise options or that shorten (such as termination) or extend the contract period of performance, this is the revised scheduled completion date for the base contract including exercised options. If the award is solely for the purchase of supplies to be delivered, the completion date should correspond to the latest delivery date on the base contract and any exercised options. The completion date does not change to reflect a closeout date.   For grants and cooperative agreements: The Period of Performance is defined in the CFR 200 as the total estimated time interval between the start of an initial Federal award and the planned end date, which may include one or more funded portions, or budget periods. If the end date is revised due to an extension, termination, lack of available funds, or other reason, the current end date will be amended.  For all other financial assistance awards: The current date on which, for the award referred to by the action being reported, awardee effort completes or the award is otherwise ended. Administrative actions related to this award may continue to occur after this date. |
| `period_of_performance_potential_end_date` | For procurement, the date on which, for the award referred to by the action being reported if all potential pre-determined or pre-negotiated options were exercised, awardee effort is completed or the award is otherwise ended. Administrative actions related to this award may continue to occur after this date. This date does not apply to procurement indefinite delivery vehicles under which definitive orders may be awarded. |
| `extent_competed_code` | A code that represents the competitive nature of the contract. |
| `extent_competed` | Description tag (by way of the FPDS Atom Feed) that explains the meaning of the code provided in the Extent Competed Field. |
| `solicitation_procedures_code` | The designator for competitive solicitation procedures available. |
| `solicitation_procedures` | Description tag (by way of the FPDS Atom Feed) that explains the meaning of the code provided in the Solicitation Procedures Field. |
| `number_of_offers_received` | The number of actual offers/bids received in response to the solicitation. |
| `other_than_full_and_open_competition_code` | The designator for solicitation procedures other than full and open competition pursuant to FAR 6.3. |
| `other_than_full_and_open_competition` | Description tag (by way of the FPDS Atom Feed) that explains the meaning of the code provided in the Other than Full and Open Competition Field. |
| `type_of_set_aside_code` | The designator for type of set aside determined for the contract action. |
| `type_of_set_aside` | Description tag (by way of the FPDS Atom Feed) that explains the meaning of the code provided in the Type Set Aside Field. |
| `naics_code` | The identifier that represents the North American Industrial Classification System (NAICS) Code assigned to the solicitation and resulting award identifying the industry in which the contract requirements are normally performed. |
| `naics_description` | The title associated with the NAICS Code. |
| `product_or_service_code` | The code that best identifies the product or service procured. Codes are defined in the Product and Service Codes Manual. |
| `product_or_service_code_description` | Description tag (by way of the FPDS Atom Feed) that explains the meaning of the code provided in the Product or Service Code Field. |
| `primary_place_of_performance_state_code` | United States Postal Service (USPS) two-letter abbreviation for the state or territory indicating where the predominant performance of the award will be accomplished. Identify States, the District of Columbia, territories (i.e., American Samoa, Guam, Northern Mariana Islands, Puerto Rico, U.S. Virgin Islands) and associated states (i.e., Republic of the Marshall Islands, the Federated States of Micronesia, and Palau) by their USPS two-letter abbreviation for the purposes of reporting. |
| `last_modified_date` | The last modified date captures the change date. |
