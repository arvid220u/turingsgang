#include <bits/stdc++.h>
using namespace std;

int main() {

    for (int i = 0; i < 10; i++) {
        int x;
        cin >> x;
        while (x >= 1000) {
            x = x - 1000;
        }
        while (x >= 10) {
            x = x - 10;
        }
        cout << x << endl;
    }



    return 0;
}
