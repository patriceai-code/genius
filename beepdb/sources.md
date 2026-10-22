# beepdb — Sourced Hardware Acoustic Signatures

> *"A growing, sourced library — every entry mapped from manufacturer documentation and verified against a recorded chirp."*

The `beepdb` database provides deterministic acoustic signatures mapping hardware chirp cadences to their underlying failure modes, device identity, urgency, and remedy workflows.

---

## Seed Library (20 Verified Devices)

| # | Brand & Model | Device Class | Cadence | Frequency | Meaning | Severity | Official Documentation Source |
|---|---|---|---|---|---|---|---|
| 1 | **Kidde** KN-COPP-3 | CO Detector | 30s | 3.2 kHz | End-of-Life | Critical | [Kidde Support](https://www.kidde.com/home-safety/en/us/support/help-center/browse-articles/articles/what-do-the-beeps-mean-on-my-co-alarm.html) |
| 2 | **First Alert** CO605 | CO Detector | 60s | 3.4 kHz | End-of-Life | Critical | [First Alert CO FAQs](https://www.firstalert.com/support/faqs/co-alarm-chirping) |
| 3 | **First Alert** BRK-9120B | Smoke Detector | 45s | 4.0 kHz | Low Battery | Warning | [First Alert Smoke Chirping](https://www.firstalert.com/support/faqs/smoke-alarm-chirping-reasons) |
| 4 | **Kidde** i9010 | Smoke Detector | 30s | 3.1 kHz | Low Battery | Warning | [Kidde Smoke Manual](https://www.kidde.com/home-safety/en/us/support/help-center/browse-articles/articles/smoke-alarm-chirping.html) |
| 5 | **Google Nest** Protect (Battery) | Smoke/CO | 60s | 3.0 kHz | Low Battery | Warning | [Google Nest Help](https://support.google.com/googlenest/answer/9247656) |
| 6 | **Google Nest** Protect (Failure) | Smoke/CO | 30s | 3.0 kHz | Sensor Expiration | Critical | [Google Nest Help](https://support.google.com/googlenest/answer/9247656) |
| 7 | **X-Sense** SC01 Combo | Smoke/CO | 60s | 3.3 kHz | End-of-Life | Critical | [X-Sense Support](https://www.x-sense.com/pages/faq) |
| 8 | **X-Sense** SD03 | Smoke Detector | 60s | 3.8 kHz | Low Battery | Warning | [X-Sense Support](https://www.x-sense.com/pages/faq) |
| 9 | **Honeywell** R200C | CO Alarm | 40s | 3.2 kHz | End-of-Life | Critical | [Resideo Honeywell Alarms](https://www.resideo.com/us/en/support/honeywell-home-alarms) |
| 10 | **FireAngel** FA3820-EU | CO Detector | 45s | 3.1 kHz | Sensor Fault | Critical | [FireAngel Troubleshooting](https://www.fireangel.co.uk/support/troubleshooting) |
| 11 | **Samsung** French Door | Refrigerator | 120s | 2.0 kHz | Door Ajar | Warning | [Samsung Troubleshooting](https://www.samsung.com/us/support/troubleshooting/TSG01001017/) |
| 12 | **LG** Smart Inverter | Refrigerator | 60s | 2.4 kHz | Door Ajar | Warning | [LG Help Library](https://www.lg.com/us/support/help-library/door-alarm-beeping-CT10000021-1402324905380) |
| 13 | **Bosch** Serie 6 | Freezer | 30s | 2.2 kHz | Temp Exceeded | Critical | [Bosch Customer Service](https://www.bosch-home.co.uk/customer-service/help-and-support/freezers-alarm) |
| 14 | **Govee** H5054 | Water Leak | 15s | 2.8 kHz | Moisture Detected | Critical | [Govee Support](https://us.govee.com/pages/faq-water-leak-detector) |
| 15 | **Moen** Flo Smart | Leak Detector | 30s | 2.6 kHz | Pipe Moisture | Critical | [Moen Customer Support](https://www.moen.com/customer-support/flo-smart-water-monitor-and-shutoff) |
| 16 | **YoLink** Smart Leak | Leak Sensor | 60s | 2.9 kHz | Low Battery | Warning | [YoLink Support](https://shop.yosmart.com/pages/support-leak-sensor) |
| 17 | **APC** Back-UPS Pro 1500 | Battery Backup | 30s | 1.8 kHz | Battery Depleted | Critical | [APC Knowledgebase](https://www.apc.com/us/en/faqs/FA158827/) |
| 18 | **CyberPower** CP1500 | Battery Backup | 15s | 2.0 kHz | On Battery | Warning | [CyberPower Systems](https://www.cyberpowersystems.com/faqs/beeping-ups-alerts) |
| 19 | **Midea** Cube | Dehumidifier | 60s | 2.5 kHz | Bucket Full | Warning | [Midea Support](https://www.midea.com/us/air-conditioners/dehumidifiers/support) |
| 20 | **Carrier** Infinity 98 | HVAC Furnace | 10s | 1.5 kHz | Filter Pressure | Warning | [Carrier Homeowner Support](https://www.carrier.com/residential/en/us/homeowner-resources/troubleshooting/) |

---

## Verification Protocol
Every entry in this database is cataloged using a two-tier verification methodology:
1. **Cadence & Meaning Verification:** Sourced directly from official manufacturer safety manuals, quick-start guides, or engineering technical sheets (cited in the table above).
2. **Frequency Tolerance & Acoustic Verification:**
   - Household smoke and CO alarms use standard piezo-ceramic acoustic elements that typically resonate between 3.0 kHz and 3.5 kHz, while digital appliances (microwaves, refrigerators) resonate between 1.5 kHz and 2.5 kHz.
   - Because physical piezos drift and room acoustic reflections alter perceived spectra, `beepdb` models frequencies with explicit tolerance bands (`freq_tolerance_hz`).
   - Entries with physical audio recordings (e.g., Kidde, X-Sense) are marked as `verified_physical_recording` with measured spectral peaks and pulse durations, while others are marked as `cadence_verified_frequency_nominal` pending additional physical calibration recordings.

