#include <bits/stdc++.h>

using namespace std;

int main(){

    int a_1, a_2, a_3, a_4, req = 0;
    cin >> a_1 >> a_2 >> a_3 >> a_4;
    
    req += a_4;

    req += a_3;

    a_1 -= a_3;

    if(a_1 < 0) a_1 = 0;

    req += (a_2 + 1)/2;

    if(a_2 % 2 == 0){
        req += (a_1 + 3)/4;
    } else {
        a_1 -= 2;
        if(a_1 < 0) a_1 = 0;
        req += (a_1 + 3)/4;
    }

    cout << req << endl;

    return 0;
}
