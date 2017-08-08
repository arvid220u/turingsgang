#include <bits/stdc++.h>
using namespace std;

int main() {

    string input, output = "";

    // Läs in input-strängen
    cin >> input;

    
    // i är index i input-strängen
    int i = 0;

    // Gå igenom input-strängen
    while (i < input.size()) {

        output += input[i];
        i += input[i] - 'A' + 1;

    }

    cout << output << endl;

    return 0;
}
