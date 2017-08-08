#include <bits/stdc++.h>
using namespace std;

int main() {

    // Deklarera talet x, som Linn tänker på
    int x;
    
    // Läs in x
    cin >> x;

    // Skapa ett nytt tal y, som är talet Linn kommer att säga högt
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

    // y är nu talet som Linn ska säga! Skriv ut det
    cout << y << endl;

    return 0;
}
