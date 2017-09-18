#include <bits/stdc++.h>
using namespace std;

int main() {

    int n;
    cin >> n;

    int res = 0;
    int x;
    for (int i = 0; i != n; ++i) {
        cin >> x;
        x = min(7,x);
        if (i % 2 == 0) {
            x -= 2;
        } else {
            x -= 3;
        }
        res += x;
    }

    cout << res << enl;

    return 0;
}
