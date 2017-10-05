#include <bits/stdc++.h>

using namespace std;

int main() {

    int n;
    cin >> n;
    vector <string> vec;
    string temp;
    for (int i = 0; i != n; ++i) {
        cin >> temp;
        vec.push_back(temp);
    }
    reverse(vec.begin(), vec.end());
    for (int i = 0; i != n; ++i) {
        cout << vec[i] << endl;
    }

    int asd;
    cin >> asd;
    return 0;
}
