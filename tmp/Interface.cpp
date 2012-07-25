#include "Interface.h"

using namespace std;
using namespace boost::property_tree;

Interface::Interface() : index_f_m("./data/index.db"), database_m("assets.db") {
}

Interface::Interface(string index_f, string database) : index_f_m(index_f), database_m(database) {}

Interface::~Interface() {
    /*Currently nothing*/
}

int Interface::init(const string &config_f) {
    // Retireving data from json config file
    ptree pt;
    try {
        read_json(config_f, pt);
        cmd_m.push_back(pt.get<string>("commande"));
        cmd_m.push_back(pt.get<string>("share.name"));
        parameters_m["days"] = pt.get("share.days", "1");
        parameters_m["action"] = pt.get("share.action", "current");
        parameters_m["precision"] = pt.get("share.precision", "10");
        parameters_m["rss"] = pt.get("share.rss", "off");
        parameters_m["dependancies"] = pt.get("share.dependancies", "off");
    }
    catch(exception &e) {
        cout << "[!] Error: " << e.what() << "\n";
    }
    if ( parameters_m["dependancies"] == "on" ) {
        cout << "[DEBUG] Storing list of dependancies to handle... ";
        string parent("");
        string child("");
        ifstream flux_in( index_f_m.c_str() );
        string line("");
        while ( getline( flux_in, line ) ) {
            stringstream ss(line);
            ss >> line >> line >> parent >> child;
            if ( parent == cmd_m[1] ) {
                cout << child + ", ";
                cmd_m.push_back(child);
            }
        }
        cout << "Done.\n";
    }
    return 0;
}
 
string Interface::getTextData(string database, string table, string field, string pattern) {
    string data("");
    int r, i;
    sqlite3 *dbh;
    sqlite3_stmt *stmt;
    if ( sqlite3_open(database.c_str(), &dbh) != SQLITE_OK ) {
        fprintf( stderr, "Could not open database (%s)\n", sqlite3_errmsg(dbh) );
        return(NULL);
    }
    string query = "SELECT " + field + " FROM " + table + " WHERE " + pattern;
    cout << "[DEBUG] accessing database: " << query << endl;
    if ( sqlite3_prepare_v2( dbh, query.c_str(), 1024, &stmt, NULL ) != SQLITE_OK ) {
        fprintf( stderr, "Didn't get any data\n" );
        exit( EXIT_FAILURE );
    }
    int fields = sqlite3_column_count( stmt );
    /*
     *affichage du header
     */
    for (i = 0; i < fields; i++) 
        printf("[DEBUG] Retrienving data as %s\n", sqlite3_column_name(stmt, i));
    /*
     *affichage des valeurs
     */
    while ( sqlite3_step( stmt ) == SQLITE_ROW ) {
        for (i = 0; i < fields; i++) {
            printf("data: %s\n", sqlite3_column_text( stmt, i ));
            data = (char*)sqlite3_column_text( stmt, i );
        }
    }
    sqlite3_finalize( stmt );
    sqlite3_close( dbh );
    return data;
}

float Interface::getRealData(string database, string table, string field, string pattern) {
    float data(0);
    int r, i;
    sqlite3 *dbh;
    sqlite3_stmt *stmt;
    if ( sqlite3_open(database.c_str(), &dbh) != SQLITE_OK ) {
        fprintf( stderr, "Could not open database (%s)\n", sqlite3_errmsg(dbh) );
        return(NULL);
    }
    string query = "SELECT " + field + " FROM " + table + " WHERE " + pattern;
    cout << "[DEBUG] accessing database: " << query << endl;
    if ( sqlite3_prepare_v2( dbh, query.c_str(), 1024, &stmt, NULL ) != SQLITE_OK ) {
        fprintf( stderr, "Didn't get any data\n" );
        exit( EXIT_FAILURE );
    }
    int fields = sqlite3_column_count( stmt );
    /*
     *affichage du header
     */
    for (i = 0; i < fields; i++) 
        printf("[DEBUG] Retrienving data as %s\n", sqlite3_column_name(stmt, i));
    /*
     *affichage des valeurs
     */
    while ( sqlite3_step( stmt ) == SQLITE_ROW ) {
        for (i = 0; i < fields; i++) {
            printf("data: %s\n", sqlite3_column_text( stmt, i ));
            data = sqlite3_column_double( stmt, i );
        }
    }
    sqlite3_finalize( stmt );
    sqlite3_close( dbh );
    return data;
}

void Interface::process() {
    for ( vector<string>::iterator it = cmd_m.begin()+1; it != cmd_m.end(); it++ ) {
        cout << "[DEBUG] Processing " << *it << "...\n";
        Share action(*it);
        if ( action.download(parameters_m["days"], parameters_m["precision"], parameters_m["action"]) != 0)
            cout << "[ERROR] Downloading quotes\n";
        string database("assets.db");
        string table("stocks");
        string field("market");
        string pattern = "ticker=\"" + *it + "\"";
        string data = getTextData(database, table, field, pattern);
        cout << data << endl;
        if ( action.compute("plot") != 0 )
            cout << "[ERROR] Computing\n";
    }
}
