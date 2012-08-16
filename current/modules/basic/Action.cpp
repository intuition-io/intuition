#include "Action.h"

using namespace std;

Action::Action(string name, string conf_f, string rscript, string pyscript, string rulesdb, string assetsdb) : Share(name, conf_f, rscript, pyscript, rulesdb, assetsdb) {
}

void Action::evaluateResults( map<string, string> configuration ) {
    results.value = getRealData(configuration["assetsdb"], "stocks", "value", "ticker", configuration["name"]);
    results.variation = getRealData(configuration["assetsdb"], "stocks", "variation", "ticker", configuration["name"]);
    results.beginDate = getTextData(configuration["assetsdb"], "stocks", "begin", "ticker", configuration["name"]);
    results.endDate = getTextData(configuration["assetsdb"], "stocks", "end", "ticker", configuration["name"]);
    cout << configuration["name"] << " data:\n\tValue: " << results.value << "\n\tVariation: " << results.variation << "\n\tFrom: " << results.beginDate << " to " << results.endDate << endl;
}

void writeResults(string out) {

}
