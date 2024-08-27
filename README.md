**Praćenje plivačkih treninga**

# Opis projekta:
Projekt omogučuje jednostavno praćenje vlastitih plivačkih treniga. Na Web servisu je moguće dodati, urediti, brisati treninge po zelji te ih vizualizirati u formi grafa. 

# Use case
![Use case IS](https://github.com/user-attachments/assets/e131a16a-0285-45ce-a3bf-172c463d47ff)

Za projekt je koristen Python uz pomoc Flask framework-a za izraditi backend Web servisa, koristeni su HTML i CSS za frontend, za bazu podataka koristen je Pony ORM.


# Funkcionalnosti
**Unos treninga:** omogućuje unošenje otplivanje daljine, vrijeme u kojem je otplivana daljina, datum te opis treninga

**Brisanje treninga:** korisnik može obrisati treninge po želji 

**Uređivanje treninga:** omogućuje korisniku uređivanje treninga ukoliko je pogriješio unjeti neki podatak

**Pregled treninga:** korisnik moze vidjeti sve treninge koje je do sada unjeo

# Docker pokretanje 
Nakon preuzimanja koda potrebno je koristiti slijedeće instrukcije

***Kreacija Image-a u Docker-u***

``` docker build --tag ime:verzija```

primjer:

ime- treninzi

verzija- 1.0

***Prvo pokretanje i kreacija Container-a u Docker-u***

``` docker run 5001:8080 treninzi:1.0 ```

