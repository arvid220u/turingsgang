#include <bits/stdc++.h>
using namespace std;

int main() {

    int N;
    cin >> N;

    // Baserat på observationen att varje tal i högra kolumnen är det första talet i listan minus det sista talet
    // Därmed blir den slutgiltiga summan bara summan av de N - 1 första talen, minus N - 1 gånger det sista talet

    int sum = 0;

    for (int i = 0; i < N; i++) {
        int x;
        cin >> x;
        if (i != N-1) {
            // sum += x är samma sak som sum = sum + x
            sum += x;
        } else {
            // samma sak som sum = sum - (N-1) * x;
            sum -= (N-1) * x;
        }
    }

    cout << sum << endl;

    return 0;
}
