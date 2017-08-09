#include <bits/stdc++.h>

using namespace std;

int main() {

    int onebok, twobok, threebok, hyllorstorlek, temp, result = 0;
    bool haveMadeMove = false;
    cin >> onebok >> twobok >> threebok >> hyllorstorlek;

    while (onebok != 0 || twobok != 0 || threebok != 0) {

        temp = 0; 

        while (temp != hyllorstorlek) {

            haveMadeMove = false;

            if (threebok > 0 && (hyllorstorlek - temp >= 3)) {

                threebok--;
                temp += 3;
                haveMadeMove = true;
            }
            else if (twobok > 0 && (hyllorstorlek - temp >= 2)) {
                twobok--;
                temp += 2;
                haveMadeMove = true;
            }
            else if (onebok > 0 && (hyllorstorlek - temp >= 1)) {
                onebok--;
                temp++;
                haveMadeMove = true;
            }
            if (haveMadeMove == false) {
                temp = hyllorstorlek;
            }
        }
        result++;
    }
    cout << result << endl;
    return 0;
}
