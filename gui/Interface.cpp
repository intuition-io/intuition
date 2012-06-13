#include "Interface.h"

using namespace std;

Interface::Interface() : index_f_m("./data/index.db"), conf_f_m("./data/quotes.ini") {
}

Interface::~Interface() {
    /*Currently nothing*/
}

void Interface::cmd_parser(string cmd_line_edit) {
    stringstream ss(cmd_line_edit);
    string input("");
    ss >> input;
    while (input.find(';') == string::npos) {
        cmd_m.push_back(input);
        ss >> input;
    }
    //cmd_m.push_back("dl");
    //cmd_m.push_back("alstom");
}

void Interface::config_file_generator() {
    ofstream flux_out(conf_f_m.c_str());        //opening in write mode
    ifstream flux_in(index_f_m.c_str());       //opening in read mode
    if (flux_in) {
        string line;
        while ( getline(flux_in, line) ) {
            stringstream ss(line);
            ss >> stock_m[0] >> stock_m[1] >> stock_m[2] >> stock_m[3] >> stock_m[4] >> stock_m[5];
            if ( stock_m[3] == cmd_m[1] || stock_m[2] == cmd_m[1]) {
                if ( flux_out ) {
                    stocks_list_m.push_back(stock_m[3]);
                    flux_out << "[" + stock_m[3] + "]\n";
                    flux_out << "name = " + stock_m[3] << endl;
                    flux_out << "code = " + stock_m[4] << endl;
                    flux_out << "market = " + stock_m[5] << endl << endl;
                }
            }
        }
        if (stocks_list_m.size() != 0) {
            cout << "Found " << stocks_list_m.size() << " references in database.\n";
            flux_out << "[general]\nstocks_list = ";
            for (unsigned int i = 0; i < stocks_list_m.size(); i++) {
                flux_out << stocks_list_m[i] + " ";
            }
            flux_out << endl;
        }
        else
            cout << "No matching reference in database.\n";
    }
    else
       cout << "Error while opening file." << endl;
}

QString Interface::infos_printer() {
    QString infos("");
    unsigned int i(0);
    while ( i < stocks_list_m.size() ) {
        ifstream quote_data(("./data/" + stocks_list_m[i] + ".data").c_str());
        if ( quote_data ) {
            infos.append("Un truc pourrave");
        }
        else
            infos = "[!] Error while opening file.";
        i++;
    }
    return infos;
}
