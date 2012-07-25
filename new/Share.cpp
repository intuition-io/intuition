#include "Share.h"

using namespace std;
using namespace boost::property_tree;

Share::Share(string name, string conf_f) : database_m("./assets.db"), conf_f_m(conf_f), name_m(name) {
}

int Share::download(string days, string precision, string action) {
    int value_r(-1);
    string downloader_cmd("./modules/basic/downloader.py -f ");
    
    //ptree pt;
    //pt.put("command", action);
    //pt.put("share.name", name_m);
    //pt.put("share.precision", precision);
    //pt.put("share.days", days);
    //write_json(, pt);

    cout << "[DEBUG] Checking if processor is available...\n";
    downloader_cmd = downloader_cmd + conf_f_m + " -d " + database_m + "\n";
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
    string r_script("R --slave --args " + name_m + " " + conf_f_m + " < ./modules/basic/compute.R");

    //ptree pt;
    //int dpo(0);
    //pt.put("command", function);
    //pt.put("share.name", name_m);
    //pt.put("graphic.macd", "on");
    //pt.put("graphic.dpo", "off");
    //pt.put("graphic.bbands", "on");
    //write_json(conf_f_m, pt);

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
 
string Share::getTextData(string database, string table, string field, string pattern) {
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

float Share::getRealData(string database, string table, string field, string pattern) {
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
