#include "Share.h"

using namespace std;

Share::Share(string name, string conf_f, string rscript, string pyscript, string rulesdb, string assetsdb) : database_m(assetsdb), conf_f_m(conf_f), name_m(name), datarules_m(rulesdb), rscript_m(rscript), pyscript_m(pyscript) {}

int Share::download(string days, string precision, string action) {
    int value_r(-1);

    cout << "[DEBUG] Checking if processor is available...\n";
    string downloader_cmd = pyscript_m + " -f " + conf_f_m + "\n";
    if (system(NULL)) {
        cout << "[DEBUG] OK - Running downloader configured: " + downloader_cmd;
        value_r = system( downloader_cmd.c_str() );
        cout << "[DEBUG] Returned value: " << value_r << endl;
    }
    else
        value_r = -2;
    return value_r;
}

int Share::compute(string function) {
    int value_r(0);
    string r_cmd("R --slave --args " + conf_f_m + " < " + rscript_m);

    cout << "[DEBUG] Computing " + function + " R script\n";
    cout << "[DEBUG] Checking if processor is available...\n";
    if (system(NULL)) {
        cout << "[DEBUG] OK - Running R script: " + r_cmd +  "\n";
        value_r = system( r_cmd.c_str() );
        cout << "[DEBUG] Returned value: " << value_r << endl;
    }
    else
        return -1;
    return value_r;
}
