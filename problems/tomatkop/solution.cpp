#include <bits/stdc++.h>
using namespace std;

int main() {

    int X, K, T;
    cin >> X >> K >> T;

    int totalkostnad = X * T;

    if (totalkostnad <= K) {
        cout << "JA" << endl;
    } else {
        cout << "NEJ" << endl;
    }

    return 0;
}
