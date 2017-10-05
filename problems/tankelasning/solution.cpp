#include <iostream>
#include <vector>
#include <unordered_set>
#include <unordered_map>
#include <algorithm>
#include <iomanip>

using namespace std;

int main() {

    int n, tempInt;
    long coefficients[12][2];
    for (int i = 0; i != 12; i++) {

        coefficients[i][0] = 0;
        coefficients[i][1] = 1;

    }
    char tempChar, temp;
    cin >> n;
    coefficients[1][0] = 1;
    coefficients[1][1] = 1;

    for (int i = 0; i != n; i++) {

        cin >> tempChar >> temp;

        if (temp == 'x') {

            if (tempChar == '+') {

                coefficients[1][0] += coefficients[1][1];

            }
            else if (tempChar == '-') {

                coefficients[1][0] -= coefficients[1][1];

            }
            else if (tempChar == '*') {

                for (int j = 11; j != 0; j--) {

                    coefficients[j][1] = coefficients[j - 1][1];
                    coefficients[j][0] = coefficients[j - 1][0];

                }
                coefficients[0][0] = 0;
                coefficients[0][1] = 1;
            }

        }
        else {
            tempInt = temp - '0';
            if (tempChar == '+') {

                coefficients[0][0] += tempInt * coefficients[0][1];

            }
            else if (tempChar == '-') {

                coefficients[0][0] -= tempInt * coefficients[0][1];

            }
            else if (tempChar == '*') {

                for (int j = 0; j != 12; j++) {

                    coefficients[j][0] *= tempInt;

                }

            }
            else if (tempChar == '/') {

                for (int j = 0; j != 12; j++) {

                    coefficients[j][1] *= tempInt;

                }

            }

        }

    }
    bool works = true;
    for (int i = 1; i != 12; i++) {

        if (coefficients[i][0] != 0) {

            works = false;

        }

    }

    if (works && (coefficients[0][0] % coefficients[0][1] == 0)) {

        cout << coefficients[0][0] / coefficients[0][1];
        
    }
    else {

        cout << "Nej";

    }

    int asd;
    cin >> asd;
    return 0;
}
