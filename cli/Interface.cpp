#include "Interface.h"

using namespace std;

Interface::Interface() : index_f_m("./data/index.db"), conf_f_m("./data/quotes.ini") {
    parameters_m[0] = "1";
    parameters_m[1] = "10";
    parameters_m[2] = "0";
}

Interface::Interface(string index_f, string conf_f, string days, string precision, string rss) : index_f_m(index_f), conf_f_m(conf_f) {    
    parameters_m[0] = days;
    parameters_m[1] = precision;
    parameters_m[2] = rss;
}

Interface::~Interface() {
    /*Currently nothing*/
}

void Interface::cmd_parser(string cmd_line) {
    // Try cmd_m.clear();
    while ( cmd_m.size() > 0  ) 
        cmd_m.pop_back();
    while ( stocks_list_m.size() > 0 ) 
        stocks_list_m.pop_back();

    stringstream ss(cmd_line);
    string input("");
    unsigned int i(0);
    //ss >> input;
    while (input.find(';') == string::npos) {
        ss >> input;
        cmd_m.push_back(input);
    }
    if ( cmd_m[2].compare("parametric") == 0 ) {
        cout << "parameters: [days precision rss]\n\t> ";
        cin >> input;
        while ( input.find(';') == string::npos ) {
            parameters_m[i] = input;
            cin >> input;
            i++;
        }
    }
    cin.ignore();
}

int Interface::config_file_generator() {
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
            cout << "[DEBUG] Found " << stocks_list_m.size() << " references in database.\n";
            flux_out << "[general]\nstocks_list = ";
            for (unsigned int i = 0; i < stocks_list_m.size(); i++) {
                flux_out << stocks_list_m[i] + " ";
            }
            flux_out << "\ndays = " << parameters_m[0] << "\nprecision = " << parameters_m[1] << "\nrss = " << parameters_m[2] << endl;
        }
        else
            return -1;
    }
    else
        return -2;
    return 0;
}

string Interface::accessDb() {
    unsigned int i(0);
    string infos("");
    string data_f("");
    string pattern("10:00");
    while ( i < stocks_list_m.size() ) {
        data_f = "./data/" + stocks_list_m[i] + ".data";
        ifstream flux_data(data_f.c_str());
        if ( flux_data ) {
            string line("");
            while ( getline(flux_data, line) ) {
                if (line.find(pattern) != string::npos) {
                    stringstream ss(line);
                    ss >> stock_m[0] >> stock_m[1] >> stock_m[2] >> stock_m[3] >> stock_m[4] >> stock_m[5];
                    line = stocks_list_m[i] + " the " + stock_m[0] + ":\n\tClose: " + stock_m[1] + "\n\tVolume: " + stock_m[5] + "\n";
                    infos += line;
                    break;

                }
            }
        }
        else
            infos += "Openinf file failled\n";
        flux_data.close();
        i++;
    }
    return infos;
}
