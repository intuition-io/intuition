#include <iostream>
#include "Action.cpp"
#include <vector>
#include <string>

using namespace std;

void init(string conf_f, vector< vector <string> > &configuration) {
    /* */
}

int main() {
    cout << "-----------------------------------------------------------------\n";
    cout << "[DEBUG] Module basic running...\n";
    vector<vector <string> > configuration;
    init("./modules/basic/config.json", configuration);

    Action test("archos", "./modules/basic/config.json");
    test.init();
    if ( test.download("1", "10", "plot") != 0 )
        cout << "[ERROR] downloading\n";
    if ( test.compute("plot") != 0 )
        cout << "[ERROR] computing\n";
    cout << "-----------------------------------------------------------------\n";
    return 0;
}
