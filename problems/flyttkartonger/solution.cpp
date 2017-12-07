#include <bits/stdc++.h>
using namespace std;
#define rep(i, from, to) for (int i = from; i < (to); ++i)
typedef long long ll;
typedef long double ld;
typedef unsigned long long ull;
typedef vector<int> vi;
typedef pair<int,int> ii;
typedef vector<pair<int, int>> vii;

int main()
{

    ll n;
    cin >> n;

    vector<ll> d(n);
    rep(i,0,n) {
        cin >> d[i];
    }

    ll oy = 0;
    for (int i = n-1; i > 0; i--) {
        ll y = max(oy, d[i]);
        ll x = 2ll * y - d[i];
        oy = x;
    }

    cout << max(0ll, oy - d[0]) << endl;
        

    return 0;
}
