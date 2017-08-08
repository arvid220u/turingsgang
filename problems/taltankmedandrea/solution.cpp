#include <bits/stdc++.h>
using namespace std;

int main() {

    // Deklarera talet hogt, som Linn säger högt
    int hogt;
    
    // Läs in y
    cin >> hogt;

    // Låt x vara talet som Linn tänker på. Vi vill testa alla möjligheter.
    for (int x = 1; x <= 10000; x++) {

        // Skapa ett nytt tal y, som är talet Linn skulle ha sa högt om hon tänkte på x
        // Vi kommer att behöva x senare
        int y = x;

        // Lägg till 19
        y = y + 19;

        // Multiplicera med 3
        y = y * 3;

        // Multiplicera med talet som Linn tänkte på från början, det vill säga x
        y = y * x;

        // Ta bort 37 från svaret
        y = y - 37;

        // Vi vill nu kolla om y faktiskt är det talet som Linn sa högt
        if (y == hogt) {
            
            // Då måste Linn ha tänkt på talet x
            cout << x << endl;

            // Avsluta programmet
            return 0;
        }
    }

    // Vi har testat alla möjligheter på tal som Linn kan ha tänkt på, och inget fungerar
    // Alltså måste Linn ha räknat fel
    cout << "FEL" << endl;

    return 0;
}
