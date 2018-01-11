#include <bits/stdc++.h>
using namespace std;

int main() {

    string x;
    cin >> x;

    int points = 0;
    if (x[0] == 'B') {
        points += 1;
    }
    if (x[x.size()-1] == 't') {
        points += 1000;
    }
    
    cout << points << endl;

    return 0;
}
