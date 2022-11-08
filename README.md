# Dopravní přestupky v Praze

Úplne základní nahrání dat o dopravních přestupcích, asi by to chtělo:

- vyčistit ulice a korelovat je s databází ulic (ČÚZK, Geoportál, ...)
- zbooleanovat osobu/firmu
- dočistit zákonnou úpravu a prolinkovat s textem zákona
- zareportovat nějaký základnosti

V tuto chvíli to vyplivne příkaz pro nahrání dat do Postgresy. Tj. stačí

```
python3 main.py
sh load.sh
```
