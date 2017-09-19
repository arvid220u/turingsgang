#include <bits/stdc++.h>
using namespace std;

int main() {

    int v;
    cin >> v;


    // Testa alla möjliga klockslag, och se vilken som ger rätt vinkel
    for (int h = 0; h <= 11; h++) {
        for (int m = 0; m <= 59; m++) {
            // timvisaren rör sig 1/12 varv (d.v.s. 360/12=30 grader) på en timme, och 360/12/60 = 0.5 grader på en minut.
            // därför kommer positionen av timvisaren vara 30h+0.5m (och eftersom vi räknar i tiondels grader alltså 300h+5m)
            int timvisare = 300*h + 5*m;
            // minutvisare beror bara på m, och rör sig 360/60 = 6 grader per minut
            int minutvisare = 60*m;
            // vinkeln mellan dem är minutvisare - timvisare. Den skulle kunna vara negativ, och om den är det lägger vi till 3600
            int vinkel = minutvisare - timvisare;
            if (vinkel < 0) {
                vinkel += 3600;
            }
            // kolla nu om vinkel är = v
            if (vinkel == v) {
                // vi har hittat rätt tid!
                cout << h << ":";
                if (m < 10) cout << "0";
                cout << m << endl;
                // Avsluta programmet direkt
                return 0;
            }
        }
    }

    return 0;
}
