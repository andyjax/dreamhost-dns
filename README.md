# dreamhost-dns

Based off of https://github.com/shang-lin/dyndream

More info here: http://shang-lin.com/blog/2017/03/16/Dynamic-DNS-with-Dreamhost

Requires `credential.json` with the following information:

```json
{
    "accessKey": "key-from-dreamhost",
    "dreamhostUrl": "https://api.dreamhost.com",
    "ipUrl": "https://ipinfo.io",
    "dynamicUrl": "url-to-update"
}
```