#include <bits/stdc++.h>
using namespace std;

int main() {

    int p;
    cin >> p;

    int gg = 1;

    for (int d = 2; d < p; d++) {
        if (p % d == 0) {
            gg = 0;
        }
    }

    if (gg == 1) {
        cout << "primtal" << endl;
    } else {
        cout << "inte primtal" << endl;
    }
    
    return 0;
}
