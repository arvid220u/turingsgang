#include <bits/stdc++.h>
using namespace std;

int main() {
    
    // Skapa variabeln n
    int n;
    
    // Läs in talet n
    cin >> n;
    
    // Skapa en variabel för summan, och sätt den till 0
    int summa;
    summa = 0;
    
    // Loopa n gånger
    for (int i = 0; i < n; i++) {
        // Läs in nästa tal
        int x;
        cin >> x;
        // Öka summan med det här talet
        summa = summa + x;
    }
    
    // Skriv ut summan
    cout << summa << endl;
    
    return 0;
}
