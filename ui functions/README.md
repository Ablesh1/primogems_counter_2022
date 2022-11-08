https://drive.google.com/file/d/1z44VRClLGRNCwu4gxd2eUUvgXXGgD6j4/view?usp=sharing
Link powyżej prowadzi do awaryjnej wersji narzędzi Qt, jeśli już nic by nie działało

Zadanie 1:
Programista zapomniał podłączyć sygnał wyszukiwarki 

do funkcji "onChanged2" znajdującej się pliku main.py

Podłącz tę funkcję w pliku GUI.py. Funkcja musi wykonywać się za każdym razem gdy tekst zostanie zmieniony

Podpowiedź: Wyszukiwarka nosi nazwę "lineEdit"


Zadanie 2:
To nie koniec problemów z wyszukiwarką
Zły Troll wkradł się do programu i ją zepsuł 
Napraw ją tak, aby funkcja usuwała z listView wydarzenia których opis nie zaczyna się w taki sposób, jaki tekst został wpisany w wyszukiwarkę

Podpowiedź: Skorzystaj z atrybutu removeRow(index) dla modelu listView


Zadanie 3:
Korzystając z QtDesignera otwórz plik GUI.ui. Następnie dodaj przycisk w dowolnym miejscu po lewej stronie okienka programu. Dodaj mu funkcję onClicked(), zapisz plik i skompiluj do GUI.py

Korzystając z klasy ExampleLabel, napisz funkcję która stworzy nowe puste okienko


Zadanie 4:

Korzystając z dokumentacji Pickle:
https://docs.python.org/3/library/pickle.html

Napisz ciało funkcji loadEvents w taki sposób, aby zczytywała ona \
zapisane kategorie (z wydarzeniami w środku) i nadpisywała nimi globalną zmienną CatDatabase

Eventy powinny wyświelić się natychmiast po wczystniu kategorii
