#include <bits/stdc++.h>
using namespace std;

int main() {

    int n, m;
    cin >> n >> m;

    int curr = 1;
    int ans = 0;
    for (int i = 0; i < m; i++) {
        int x;
        cin >> x;
        ans += min(abs(curr - x), abs(min(x, curr) + min(n - x, n- curr)));
        curr = x;
    }

    cout << ans << endl;


    return 0;
}
