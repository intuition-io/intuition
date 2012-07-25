#include "Share.h"

using namespace std;
using namespace boost::property_tree;

Share::Share(string name) : database_m("assets.db"), name_m(name) {
}

int Share::download(string days, string precision, string action, string conf_dl = "./conf_dl.json") {
    int value_r(-1);
    string downloader_cmd("./downloader.py -f ");
    
    ptree pt;
    pt.put("command", action);
    pt.put("share.name", name_m);
    pt.put("share.precision", precision);
    pt.put("share.days", days);
    write_json(conf_dl, pt);

    cout << "[DEBUG] Checking if processor is available...\n";
    downloader_cmd = downloader_cmd + conf_dl + " -d " + database_m + "\n";
    if (system(NULL)) {
        cout << "[DEBUG] OK - Running downloader configured: " + downloader_cmd;
        value_r = system( downloader_cmd.c_str() );
        cout << "[DEBUG] Returned value: " << value_r << endl;
    }
    else
        value_r = -2;
    return value_r;
}

int Share::compute(string function, string conf_r = "./conf_r.json") {
    int value_r(0);
    string r_script("R --slave --args " + name_m + " " + conf_r + " < ./compute.R");

    ptree pt;
    int dpo(0);
    pt.put("command", function);
    pt.put("share.name", name_m);
    pt.put("graphic.macd", "on");
    pt.put("graphic.dpo", "off");
    pt.put("graphic.bbands", "on");
    write_json(conf_r, pt);

    cout << "[DEBUG] Computing " + function + " R script\n";
    cout << "[DEBUG] Checking if processor is available...\n";
    if (system(NULL)) {
        cout << "[DEBUG] OK - Running R script: " + r_script +  "\n";
        value_r = system( r_script.c_str() );
        cout << "[DEBUG] Returned value: " << value_r << endl;
    }
    else
        return -1;
    return value_r;
}

void Share::display() {
    cout << "\t[" << data_m.date << data_m.hour << "]\t" << name_m << "\t" << data_m.value << "€ ( " << ((data_m.open - data_m.value) * 100 / data_m.value) << "% )\tvolume: " << data_m.volume/100 << "K€" << endl;
    //cout << "\tVariation: " << stats_m.variation << endl;
}
