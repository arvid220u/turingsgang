#include <bits/stdc++.h>
using namespace std;

int main() {

    int X, K, T;
    // På det här sättet kan vi läsa in 3 variabler genom att bara använda en rad.
    cin >> X >> K >> T;
    // Vi hade också kunnat skriva följande:
    // cin >> X;
    // cin >> K;
    // cin >> T;
    // Det betyder exakt samma sak, men tar lite längre tid att skriva.

    int totalkostnad = X * T;

    // Vi vill kolla om totalkostnaden är mindre eller lika med hur mycket pengar Linn har (dvs K)
    if (totalkostnad <= K) {
        // Notera: skulle vi skriva ut "Ja!" eller "ja" skulle vi få fel svar (Wrong Answer).
        cout << "JA" << endl;
    } else {
        // På samma sätt om vi skulle skriva ut "nä" eller "nEJ". Datorn är petig.
        cout << "NEJ" << endl;
    }

    return 0;
}
