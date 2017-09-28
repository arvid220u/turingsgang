#include <bits/stdc++.h>
using namespace std;
char enl = '\n';

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(0);

    // breadth = b; height = h;
    // b = smallest integer greater than or equal to sqrt(n);
    // h = n / b;
    // area = (b + 2) * (h + 1)
    // shouldn't work in all cases, but should be a pretty good estimate from where to start brute forcing
    // instead, do some kind of brute force, within some limits
    //
    // see the points as being a square that has its lower left corner in the point
    // thus, the area will be the number of points, plus h + b + 1 + (n % b).
    // Since the number of points is given, and static, you only need to minimize h + b + ((b - n % b) % b)
    // Establish the relationship: b >= h, always.
    // a possible brute force: from ceil(sqrt(n)) up until a divisor is found
    int n;
    cin >> n;
    
    // get integer sqrt
    int b = ceil(sqrt(n));
    int h = 1 + ((n - 1) / b);
    int min_val = b + h + 1 + ((b - n % b) % b);
    while (n % b != 0) {
        ++b;
        if (b + 2 >= min_val)
            break;
        h = 1 + ((n - 1) / b);
        int new_val = b + h + 1 + ((b - n % b) % b);
        min_val = min(min_val, new_val);
    }
    cout << (min_val + n) << enl;
        


    return 0;
}
