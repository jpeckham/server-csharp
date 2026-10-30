# Local integration checks

## Seasonal configuration regression

`seasonal_config.py` is read-only and requires Python 3. It checks seasonal gear, loot and appearance bot references against the supplied database, including both PMC factions. Run from the repository root:

```powershell
python Testing/LocalIntegration/seasonal_config.py --data Libraries/SPTushonka.Server.Assets/SPT_Data
# Also verify the installed data:
python Testing/LocalIntegration/seasonal_config.py --data '<game>/SPT_Runtime/SPT_Data'
```

On 2026-10-30 the initial check failed on six obsolete `bear`/`usec` keys. Replacing them with `pmcbear`/`pmcusec` made both tests pass. This fixes the Halloween startup exception in SeasonalEventService.AddEventGearToBots and the same outdated references in Christmas gear/appearances. No service-code workaround or assembly replacement is required.

The local 48484 installation then started with automatic seasonal detection enabled, logged `Event: Halloween is active`, and reached `Server has started, happy playing`. The 31 TarcoinStoreServiceTests also passed with detection enabled, without the previous test-output-only workaround. Those tests cover initialization and shop regressions, not Halloween raid gameplay or Christmas activation. Full gameplay needs player validation. Local backups/logs and owned-process orchestration are documented in the parent SPT-BE README.

## Shop integration checks

`stash_cap.py` preserves the real HTTP regression test used for the local SPT 5 / EFT 1.3.0.0.48484 shop fixes. The server is the owner of stash bundle grants/caps, so the test belongs here rather than in FreeTarcoins. FreeTarcoins supplies test currency only.

Prerequisites: Python 3 (without `-O`), this server branch running on local HTTPS port 6969, FreeTarcoins installed, client closed, and a **fresh disposable** LocalBuildTest account with zero purchased stash rows. The name check is only a guard: do not reuse a played character. Back up all profiles before server startup. Do not run against a remote server. The test allows the local self-signed certificate.

```powershell
python Testing/LocalIntegration/stash_cap.py --runtime '<game>/SPT_Runtime' --profile '<disposable-id>' --output '<new-local-results-directory>'
# Use a separate fresh zero-row account for this second scenario:
python Testing/LocalIntegration/stash_cap.py --runtime '<game>/SPT_Runtime' --profile '<other-disposable-id>' --output '<another-new-directory>' --bundle-ownership
```

The first scenario grants test currency and buys rows; checks oversized/overflow rejection, 2+20=22, 78+2=80, concurrent purchases at the cap, no currency/inventory changes on rejection, rendered shop explanation and unchanged other profiles. The second verifies 20+60 works while repeating an owned bundle fails. Both deliberately persist purchases on the disposable account. The script saves its initial profile and HTML evidence under output; it never restores a running server's profile file. Stop the server before deliberately restoring the disposable profile, or discard the test account normally.

Original scenarios passed during the 48484 stash-cap implementation. The parameterized relocation was checked for Python syntax and command-line help only; it was not rerun on the now-played account. Server unit tests for the cap are in Testing/UnitTests. Parent SPT-BE scripts/README.md documents process ownership, startup/log capture and cleanup. Keep output directories and profile backups outside this repository.
