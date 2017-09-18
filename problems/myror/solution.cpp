#include <bits/stdc++.h>
using namespace std;

int main() {
    
    int n;
    cin >> n;
    
    int myror = -1;
    for (int i = 0; i <= 42; i++) {
        int ben = 6 * i + 8 * (42 - i);
        if (ben == n) myror = i;
    }
    
    if (myror == -1) cout << "FEL" << endl;
    else cout << myror << endl;
    
    return 0;
}
