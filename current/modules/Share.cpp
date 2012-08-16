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


string Share::getTextData(string database, string table, string field, string patternField, string pattern) {
    string data("");
    int r, i;
    sqlite3 *dbh;
    sqlite3_stmt *stmt;
    if ( sqlite3_open(database.c_str(), &dbh) != SQLITE_OK ) {
        fprintf( stderr, "Could not open database (%s)\n", sqlite3_errmsg(dbh) );
        return(NULL);
    }
    string query = "SELECT " + field + " FROM " + table + " WHERE " + patternField + " LIKE '" + pattern + "'";
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
            printf("[DEBUG] Retrieved data: %s\n", sqlite3_column_text( stmt, i ));
            data = (char*)sqlite3_column_text( stmt, i );
        }
    }
    sqlite3_finalize( stmt );
    sqlite3_close( dbh );
    string dataToString(data);
    //cout << "Converted: " << dataToString << endl;
    //return dataToString;
    return data;
}

double Share::getRealData(string database, string table, string field, string patternField, string pattern) {
    double data(0);
    int r, i;
    sqlite3 *dbh;
    sqlite3_stmt *stmt;
    if ( sqlite3_open(database.c_str(), &dbh) != SQLITE_OK ) {
        fprintf( stderr, "Could not open database (%s)\n", sqlite3_errmsg(dbh) );
        return(1);
    }
    string query = "SELECT " + field + " FROM " + table + " WHERE " + patternField + " LIKE '" + pattern + "'";
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
            printf("[DEBUG] Retrieved data: %s\n", sqlite3_column_text( stmt, i ));
            data = sqlite3_column_double( stmt, i );
        }
    }
    sqlite3_finalize( stmt );
    sqlite3_close( dbh );
    return data;
}
