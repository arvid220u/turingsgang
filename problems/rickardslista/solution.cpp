#include <bits/stdc++.h>
using namespace std;

int main() {
    
    // Läs in antalet tal i listan
    int n;
    cin >> n;
    
    // Vi skapar en vector av vår lista
    vector<int> lista;
    
    // Vi läser in talen som vi får in till vår lista
    for (int i = 0; i < n; i++) {
        int x;
        cin >> x;
        lista.push_back(x);
    }
    
    for (int i = 0; i < n; i++) {
        // lista[n-1] är det sista talet i listan eftersom man börjar på 0
        cout << lista[i] + lista[n-1] << endl;
    }
    
    return 0;
}
