#include "Share.h"

using namespace std;

Share::Share(string name) : index_f_m("./data/index.db"), data_f_m("./data/" + name + ".data"), name_m(name) {
}

int Share::download(string days, string precision, string action, string conf_f = "./data/quotes.ini") {
    int value_r(-1);
    string downloader_cmd("./downloader/downloader.py -o ");
    ofstream flux_out(conf_f.c_str());
    ifstream flux_in(index_f_m.c_str());
    string line;
    string name;
    string stock_i_m[6];

    if ( flux_in && flux_out ) {
        while ( getline( flux_in, line ) ) {
            name = name_m;
            stringstream ss(line);
            ss >> stock_i_m[0] >> stock_i_m[1] >> stock_i_m[2] >> stock_i_m[3] >> stock_i_m[4] >> stock_i_m[5];
            if ( stock_i_m[3] == name ) {
                cout << "[DEBUG] Found a reference in database\n";
                downloader_cmd += name;
                flux_out << "[" + stock_i_m[3] + "]\n";
                flux_out << "name = " + stock_i_m[3] << "\naction = " << action <<"\ncode = " + stock_i_m[4] + "\nmarket = " + stock_i_m[5]  << "\ndays = " << days << "\nprecision = " << precision << endl;
                break;
            }
        }
        flux_out.close();
        cout << "[DEBUG] Checking if processor is available...\n";
        if (system(NULL)) {
            cout << "[DEBUG] OK - Running downloader configured...\n";
            value_r = system( downloader_cmd.c_str() );
            cout << "[DEBUG] Returned value: " << value_r << endl;
        }
    }
    else
        value_r = -2;
    return value_r;
}

/*
 *Remplis la structure infos_m de l'objet
 */
int Share::getData() {
    ifstream flux_in(data_f_m.c_str());
    string line("");
    if ( flux_in ) {
        getline( flux_in, line );
        getline( flux_in, line );
        flux_in.seekg(-line.size(), ios::end);
        getline( flux_in, line );
        stringstream ss(line);
        ss >> data_m.date >> data_m.hour >> data_m.value >> line >> line >> data_m.open >> data_m.volume;
    }
    else
        return -1;
    return 0;
}

void Share::display() {
    cout << "\t[" << data_m.date << data_m.hour << "]\t" << name_m << "\t" << data_m.value << "€ ( " << ((data_m.open - data_m.value) * 100 / data_m.value) << "% )\tvolume: " << data_m.volume/100 << "K€" << endl;
    //cout << "\tVariation: " << stats_m.variation << endl;
}

/*
 *Calcule la variation entre maintenant et le mm/jj
 */
int Share::computeVariation(string date_from) {
    ifstream flux_in(data_f_m.c_str());
    string line("");
    float value_from(1);
    if ( flux_in ) {
        while ( getline(flux_in, line) ) {
            if ( line.find(date_from) != string::npos ) {
                stringstream ss(line);
                ss >> line >> value_from;
                stats_m.variation = ((data_m.value - value_from) * 100) / value_from;
                return 0;
            }
        }
    }
    else
        return -1;
    return 1;
}

int Share::plot() {
    int value_r(0);
    string r_script("R --slave --args " + name_m + " < ./quantmod.R");
    cout << "[DEBUG] Checking if processor is available...\n";
    if (system(NULL)) {
        cout << "[DEBUG] OK - Running R script...\n";
        value_r = system( r_script.c_str() );
        cout << "[DEBUG] Returned value: " << value_r << endl;
    }
    else
        return -1;
    return value_r;
}
