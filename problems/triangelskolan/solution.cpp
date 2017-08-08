#include <bits/stdc++.h>
using namespace std;

int main() {

    // Läs in talet n
    int n;
    cin >> n;

    // Vi bygger upp triangeln steg för steg
    // Vi gör det tills antalet förbrukade brickor är större än n
    
    // Låt f vara antalet förbrukade brickor
    int f = 0;

    // Låt svar vara sidlängden på triangeln
    int svar = 0;

    // Loopa så länge f är mindre eller lika med n
    while (f <= n) {

        // Öka sidlängden med 1
        svar = svar + 1;

        // f ökar nu med sidlängden, det vill säga vår variabel svar
        // Detta är vår lösande observation
        f = f + svar;
    }

    // Vi kommer att ha räknat 1 sidlängd för mycket
    // Detta eftersom loopen har slutat här, vilket betyder att f > n
    // Alltså är det riktiga svaret svar-1
    cout << (svar-1) << endl;
}
