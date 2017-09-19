#include <bits/stdc++.h>
using namespace std;

int main() {

    int x;
    cin >> x;

    while (x >= 2) {
        x = x - 2;
    }

    if (x == 0) {
        cout << "jämnt" << endl;
    } else {
        cout << "udda" << endl;
    }

    // Det finns faktiskt en funktion i C++ som gör att man kan bestämma om ett tal är udda eller jämnt
    // x % 2 ger svaret 1 om x är udda och 0 om x är jämnt, alltså precis det vi gjorde med while-loopen
    // % kallas modulo och kan användas med andra tal än 2

    return 0;
}
