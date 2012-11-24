#include "Action.h"

using namespace std;

Action::Action(string name, string conf_f, string rscript, string pyscript, string rulesdb, string assetsdb) : Share(name, conf_f, rscript, pyscript, rulesdb, assetsdb) {
}

/*
* Retrieve every module's informations
*/
void Action::evaluateResults( map<string, string> configuration ) {
    vector<string> textTmp;
    vector<double> doubleTmp;
    int fieldsTmp(0);
    //TODO Apprendre la syntaxe sql et récupérer plusieurs résultats à la fois
    //TODO des paramètres par défaut, donc changement d'ordre
    //TODO Pas de vecteur, une map de vecteur ! (avec le nom des colonnes et demandes multiples)
    if ( (fieldsTmp = getRealData(doubleTmp, configuration["assetsdb"], "stocks", "value", "ticker", name_m)) > 0 ) {
        cout << "[DEBUG] Got " << fieldsTmp << " result(s) for value\n";
        results.value = doubleTmp[0];
    }
    if ( (fieldsTmp = getRealData(doubleTmp, configuration["assetsdb"], "stocks", "variation", "ticker", name_m)) > 0 ) {
        cout << "[DEBUG] Got " << fieldsTmp << " result(s) for variation\n";
        results.variation = doubleTmp[0];
    }
    if ( (fieldsTmp = getTextData(textTmp, configuration["assetsdb"], "stocks", "begin", "ticker", name_m)) > 0 ) {
        cout << "[DEBUG] Got " << fieldsTmp << " result(s) for begin date\n";
        results.beginDate = textTmp[0];
    }
    if ( (fieldsTmp = getTextData(textTmp, configuration["assetsdb"], "stocks", "end", "ticker", name_m)) > 0 ) {
        cout << "[DEBUG] Got " << fieldsTmp << " result(s) for end date\n";
        results.endDate = textTmp[0];
    }
    cout << name_m << " data:\n\tValue: " << results.value << "\n\tVariation: " << results.variation << "\n\tFrom: " << results.beginDate << " to " << results.endDate << endl;
}

/*
 * Write it to a file, for main process use
 */
int Action::writeResults(string out) {
    cout << "[DEBUG] Writting report file: " << out << endl;
    ofstream reportFile(out.c_str(), ios::app);
    if ( reportFile ) {
        reportFile << name_m << ":\tValue: " << results.value << " - " << results.variation << "%\t[ From: " << results.beginDate << " to " << results.endDate << " ]\n";
    }
    else {
        cout <<"** Error opening basic report file\n";
        return 1;
    }
    cout << "Done.\n\n";
    return 0;
}
