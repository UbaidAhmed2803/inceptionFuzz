# inceptionFuzz

This tool is created by Ubaid Ahmed based on some project requirement.

**Features**
1. This tool helps in fuzzing a url upto 2 levels i.e. https://domain.com/Fuzz/Fuzz.
2. You can provide the status for which you want the result to be printed.
3. All your results are saved in a txt file which is saved with the name of the domain for which you are fuzzing.
4. You can even specify upto 3 headers.
5. You can even provide your own wordlist for fuzzing or let the tool use a default wordlist of 36K payloads

**Options**

```
Usage: python3 inceptionFuzz.py https://domain.com [--status] 200,301 [--headers] "X-Forwarded-For:127.0.0.1" 
"Origin:127.0.0.1" "User-Agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:101.0) Gecko/20100101 Firefox/101.0" 
[--wordlist] /wordlists/wordlist_test.txt
```

**Simple Usage**

```
python3 inceptionFuzz.py https://domain.com
```

```
python3 inceptionFuzz.py https://domain.com --status 200,301
```

```
python3 inceptionFuzz.py https://domain.com --status 200,301 --headers "Origin:127.0.0.1"
```

```
python3 inceptionFuzz.py https://domain.com --status 200,301 --headers "Origin:127.0.0.1" "X-Forwarded-Host:127.0.0.1" --wordlist /wordlist/test.txt
```
