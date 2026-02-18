# MMF fetcher setup — sync your MyMiniFactory library

The MMF fetcher pulls your **MyMiniFactory library** (saved/liked objects) or your uploaded objects via the [MMF API v2](https://www.myminifactory.com/api-doc/index.html) and writes JSON that the hydrator uses to update `stl_library` in the database. By default it fetches **library** items (`GET /users/{username}/objects_liked`); set `MMF_LIBRARY_SOURCE=objects` to fetch objects you uploaded instead.

---

## 1. One-time setup

### 1.1 Your MMF username

The API endpoint used is:

`GET https://www.myminifactory.com/api/v2/users/{username}/objects`

So you need the **username** whose library you want to sync (usually your own). You can also set **MMF_LIBRARY_SOURCE**: `objects_liked` (default) = your library (saved/liked objects), or `objects` = objects you uploaded. You can set the username via:

- **Environment variable (recommended):**  
  `MMF_USERNAME=YourMmfUsername`
- Or edit the top of `scripts/mmf/fetch_mmf_library.py` and set `MMF_USERNAME = "YourMmfUsername"`.

### 1.2 API key / auth (required for `/users/{username}/objects`)

The library endpoint returns **401 Unauthorized** without a valid **OAuth2 access token**. MyMiniFactory does not give a simple “API key” from the developer page; the developer-page "API key" is often not accepted for this endpoint; use the OAuth2 flow below to get an access token and set it as `MMF_API_KEY`.

**Step A — Create an app**

1. Log in to MyMiniFactory and go to:  
   **https://www.myminifactory.com/settings/developer/application**
2. Create an application and note the **Client ID** and **Client secret**.
3. Add this **Redirect URI** to your app:  
   `http://localhost:8765/callback`  
   (required for the token helper script).

**Step B — Get an access token (one-time)**

Use the helper script so you don’t have to do the OAuth exchange by hand:

1. Set your client ID and secret (edit the script or use env):
   ```powershell
   $env:MMF_CLIENT_ID = "your_client_id"
   $env:MMF_CLIENT_SECRET = "your_client_secret"
   ```
   Or edit the top of `scripts/mmf/get_mmf_token.py` and set `MMF_CLIENT_ID` and `MMF_CLIENT_SECRET`.
2. Run:
   ```powershell
   python scripts\mmf\get_mmf_token.py
   ```
3. A browser window will open; log in to MyMiniFactory and approve the app. When the page says “You can close this tab”, return to the terminal. The script will print an **access token**.
4. Use that token as `MMF_API_KEY` (see Step C). Tokens expire (e.g. after 1 hour); if you get 401 again later, run `get_mmf_token.py` again to get a new token. You can also use the printed **refresh token** with MMF’s token endpoint to get new access tokens without opening the browser again (see [MMF oauth2-instructions](https://github.com/MyMiniFactory/api-documentation/blob/master/oauth2-instructions.md)).

**Step C — Set the token in the fetcher**

- **Environment (recommended):**  
  `$env:MMF_API_KEY = "paste_access_token_here"`
- Or in the script: in `scripts/mmf/fetch_mmf_library.py`, set  
  `MMF_API_KEY = os.environ.get("MMF_API_KEY", "paste_access_token_here")`  
  (avoid committing real tokens; prefer env.)

The fetcher sends this as `Authorization: Bearer <token>` and as query param `key=...`.

**Alternative — Session cookie (when OAuth/API key fails)**

You can use your **browser session cookie** instead of an API key. This is the same approach as the [MyMiniFactory Model Downloader](https://gist.github.com/deliriyum/d353b9528e970e242b1915bb51da2a61) scripts:

1. Log in to [MyMiniFactory](https://www.myminifactory.com) in your browser.
2. Open Developer Tools (F12) → **Network** tab.
3. Trigger any request (e.g. open your profile or an object page).
4. Click a request to `myminifactory.com` → **Headers** → find **Cookie:** and copy the **entire** value (all `name=value` pairs). The script needs the full header; in particular **cf_clearance** (Cloudflare) and **PHPSESSID** (session) are required to avoid 403 / "Just a moment..." when calling the data-library API.
5. Set it for the fetcher. **In PowerShell you must wrap the cookie in double quotes** (the value contains `;`, which PowerShell otherwise treats as a command separator):
   ```powershell
   $env:MMF_SESSION_COOKIE = "paste_the_entire_cookie_string_here"
   python scripts\mmf\fetch_mmf_library.py
   ```
   Easiest: type `$env:MMF_SESSION_COOKIE = "` then paste the cookie from the clipboard, then type the closing `"`.
6. Cookies expire (often 30–60 minutes); if you get **401** or **403** (or a "Just a moment..." HTML page), copy a **fresh** cookie from the browser while still logged in.

7. **403 "Just a moment" with a valid cookie:** Cloudflare can block scripts by TLS fingerprint. Install **curl_cffi** so the fetcher can impersonate Chrome when using a session cookie: `pip install curl_cffi`. The script will then use it automatically and print "Using curl_cffi (Chrome TLS)…".

The fetcher tries cookie auth if `MMF_SESSION_COOKIE` is set; you can set it with or without `MMF_API_KEY`.

**Preview images:** The data-library list endpoint may return minimal objects (no `previewUrl`). To fill previews, set **`MMF_ENRICH_PREVIEW=1`** before running the fetcher. It will then call `GET /api/v2/objects/{id}` for each object missing a preview URL (slower; use `MMF_ENRICH_DELAY=0.3` or higher to avoid rate limits). After that, re-run the hydrator so the DB gets the new preview URLs.

**Object detail vs “content-json” on the page:** The JSON you see as `content-json` when loading an object page (e.g. `/object/3d-print-phaeton-guard-...`) is **cart/checkout data** (getCart, items, campaigns, pricing), not the 3D object metadata. For **object detail** (name, description, previewUrl, images, creator, price), the fetcher uses **`GET /api/v2/objects/{id}`** during enrichment. That endpoint returns the full object; we already map previewUrl and could extend the normalizer to store description/price if we add those columns later.

### 1.3 Library IDs file (for exact Library sync: `MMF_LIBRARY_SOURCE=data_library`)

To sync **exactly** what appears at [My Library](https://www.myminifactory.com/library), the fetcher reads object IDs from **`data/mmf/library_ids.txt`** (one numeric ID per line) and calls `GET /api/data-library/objects?ids[]=...`. To build that file without copying hundreds of Network requests:

1. Open **https://www.myminifactory.com/library** and log in.
2. **Scroll down until your full library has loaded** (or as far as you need).
3. Open DevTools (F12) → **Console**.
4. Paste and run the **“Get library IDs from Performance”** snippet from the script comment in `scripts/mmf/fetch_mmf_library.py` (or from the section below). It reads already-made requests from the Performance API (no DOM, no manual copying).
5. The snippet will **copy** the IDs to your clipboard. Paste into **`data/mmf/library_ids.txt`** (one ID per line), save, then run the fetcher with `MMF_LIBRARY_SOURCE=data_library`.

**Recommended for large libraries (big Performance buffer):**

The buffer size must be set **on the same page that will make the requests**, and **before** you scroll. If you set the buffer and then refresh, the new page gets the default buffer again, so you’d still see only ~100 IDs. Do this order:

1. Open **https://www.myminifactory.com/library** and log in.
2. Open DevTools (F12) → **Console**.
3. **Refresh the page (F5)** so you have a clean load.
4. **As soon as the page has loaded**, run this on the **new** page (so this page’s buffer is large before you scroll):
   ```js
   performance.setResourceTimingBufferSize(15000);
   console.log('Buffer set to 15000. Now scroll to the very bottom to load the full library, then run the extract snippet.');
   ```
5. **Scroll slowly to the very bottom** so every batch of library items loads (all requests will now be kept in the buffer).
6. **Then** run this to collect IDs from the buffer and copy to clipboard:
   ```js
   (function(){
     var urls = [];
     try {
       var entries = performance.getEntriesByType('resource');
       for (var i = 0; i < entries.length; i++) {
         if (entries[i].name && entries[i].name.indexOf('data-library/objects') !== -1)
           urls.push(entries[i].name);
       }
     } catch(e) { console.log('Error:', e); return; }
     var ids = [];
     urls.forEach(function(u) {
       var q = u.indexOf('?');
       if (q === -1) return;
       var s = u.slice(q + 1).split('&');
       s.forEach(function(p) {
         var eq = p.indexOf('=');
         if (eq === -1) return;
         var k = p.slice(0, eq), v = decodeURIComponent(p.slice(eq + 1)).trim();
         if ((k.indexOf('ids') !== -1) && /^\d+$/.test(v)) ids.push(v);
       });
     });
     ids = ids.filter(function(id, i, a) { return a.indexOf(id) === i; });
     console.log('Found ' + ids.length + ' library IDs');
     if (typeof copy === 'function') { copy(ids.join('\n')); console.log('Copied to clipboard. Paste into data/mmf/library_ids.txt'); }
     else console.log(ids.join('\n'));
   })();
   ```
7. Paste the clipboard into **`data/mmf/library_ids.txt`** and save.

**Large libraries (10k+ items):** The fetcher is tuned for big ID lists:

- **Chunk size** defaults to 50 IDs per request (fewer requests). Override with `MMF_LIBRARY_CHUNK_SIZE=20` if the API errors on large chunks.
- **Delay** between requests defaults to 0.5s to reduce rate limiting. Override with `MMF_LIBRARY_DELAY=0` to run faster (risk of 429), or `MMF_LIBRARY_DELAY=1` to be gentler.
- Progress is printed every 20 chunks and at the end. For ~10k IDs expect roughly 200 requests and several minutes. The resulting `mmf_download.json` and hydrator run may take a minute or two.

---

## 2. Normal workflow

1. **Fetch latest library from MMF**  
   From the repo root (e.g. `WahapediaExport`):
   ```powershell
   $env:MMF_USERNAME = "YourUsername"
   python scripts\mmf\fetch_mmf_library.py
   ```
   Or from the `scripts\mmf` folder:
   ```powershell
   python .\fetch_mmf_library.py
   ```
   (PowerShell does not run scripts from the current folder by name only—use `python` and the path.)
   This writes:
   - `data/mmf/mmf_download.json` — list of objects in the shape the hydrator expects.
   - `data/mmf/last_sync.json` — hash + timestamp for sync check.

2. **Update the database**  
   ```powershell
   python scripts\mmf\mmf_hydrator.py
   ```
   The hydrator reads `data/mmf/mmf_download.json` and upserts into `stl_library`. If the content hash matches `last_sync.json`, it skips the DB write (no change). Use `--force` to run anyway:
   ```powershell
   python scripts\mmf\mmf_hydrator.py --force
   ```

3. **Optional: run both in one go**  
   Fetch then hydrate:
   ```powershell
   python scripts\mmf\fetch_mmf_library.py; python scripts\mmf\mmf_hydrator.py
   ```

---

## 3. Sync check (no redundant DB writes)

- **fetch_mmf_library.py** always overwrites `data/mmf/mmf_download.json` and `data/mmf/last_sync.json` with the latest API response and its hash.
- **mmf_hydrator.py** computes the hash of the current JSON; if it equals `last_sync.json`’s hash, it exits without writing to the DB. So you can run the hydrator after every fetch, or on a schedule; the DB is only updated when the fetched data actually changed.

---

## 4. Troubleshooting

| Issue | What to try |
|-------|---------------------|
| **401 Unauthorized** | You need an OAuth2 **access token**, not the app client ID/secret. Run `python scripts\mmf\get_mmf_token.py` (see §1.2), then set `MMF_API_KEY` to the printed token. If it used to work, the token may have expired—run the script again. |
| **Invalid client ID or secret** (token exchange) | Re-copy **Client ID** and **Client Secret** from your app at https://www.myminifactory.com/settings/developer/application (no leading/trailing spaces). Use the OAuth client secret for that app; if you regenerated the secret, use the current one. |
| **Prefer not to use OAuth** | Use **session cookie** instead: log in at myminifactory.com, F12 → Network → copy Cookie header, then `$env:MMF_SESSION_COOKIE = "..."` and run the fetcher. See [MyMiniFactory Model Downloader](https://gist.github.com/deliriyum/d353b9528e970e242b1915bb51da2a61) for the same approach. |
| **0 objects returned** (cookie works, logged-in user correct) | The API may only return **published** objects. Draft or private objects might not appear. On myminifactory.com, confirm you have at least one **published** object on your profile. If you do and still get 0, the API may require OAuth for “your objects” in some cases. |
| **No objects returned** | Confirm `MMF_USERNAME` is correct and that the account has objects. |
| **Wrong or missing fields** | The API response shape may differ from the mapper. Check `data/mmf/mmf_download.json` and adjust `_normalize_object()` in `fetch_mmf_library.py` (e.g. different field names for creator, preview image, or url). |
| **Hydrator says “JSON not found”** | Run `fetch_mmf_library.py` first so that `data/mmf/mmf_download.json` exists. |

---

## 5. References

- **Scrapers and sync design:** `docs/Scrapers-and-Sync-Design.md`
- **Data sources table:** `MySQLDumps/README.md` — “Data sources and import/export scripts”
- **MMF API:** https://www.myminifactory.com/api-doc/index.html (base URL: `https://www.myminifactory.com/api/v2`)
