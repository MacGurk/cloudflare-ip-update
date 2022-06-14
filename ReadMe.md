# Cloudflare IP update
Script to dynamically update DNS-Record on cloudflare if IP of server has changed.

## Config file
File named config.json must be present in same directory as ip_update.py.
The file must contain following data
```json
{
  "zones": [
    {
      "name": "domain.ch",
      "zone_id": "z0n3_1D"
    }
  ],
  "cloudflare_api_token": "Cl0uDfl4r3_aP1_t0k3n"
}
```

Everything gets logged to ip_update.log in the same directory of the script.

## Run scheduled
Script can run automatically via cron.

Example crontab to run all 5 minutes, replace the path:
```
*/5 * * * * python3 /path/to/ip_update.py
```
See [crontab man page](https://man7.org/linux/man-pages/man5/crontab.5.html) for reference.