#include <bits/stdc++.h>
using namespace std;

int main() {

    int n, total = 0, temp;
    cin >> n;
    for (int i = 0; i != n; ++i) {
        cin >> temp;
        total += temp;
    }
    cout << total << endl;
    return 0;
}
