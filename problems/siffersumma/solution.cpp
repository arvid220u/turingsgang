#include <bits/stdc++.h>
using namespace std;

int main() {
    
    int n;
    cin >> n;
    
    int y = n;
    int nsumma = 0;
    while (y > 0) {
        nsumma += y % 10;
        y /= 10;
    }
    
    int g = 1;
    while (g == 1) {
        n += 1;
        int y = n;
        int siffersumma = 0;
        while (y > 0) {
            siffersumma += y % 10;
            y /= 10;
        }
        if (siffersumma == nsumma) {
            g = 0;
        }
    }
    cout << n << endl;
    
    return 0;
}
