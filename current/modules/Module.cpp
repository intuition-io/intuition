#include "Module.h"

using namespace std;
using namespace boost::property_tree;

Module::Module(string name) : moduleName(name) {}

void Module::init(string configFile, map<string, string> &configuration)
{
	cout << "[DEBUG] Initiating module: " << moduleName << endl;;
    ptree pt;
    try {
        read_json(configFile, pt);
        //ptree pt_child = pt.get_child("debug.modules");
        for ( ptree::iterator iptree = pt.begin(); iptree != pt.end(); iptree++ ) {
            configuration[iptree->first] = iptree->second.data();
            cout << iptree->first << "\t" << iptree->second.data() << endl;
        }
        
    }
    catch(exception &e) {
        cout << "[ERROR] " << e.what() << "\n";
    }
    cout << " Done.\n";
}

string Module::getTextData(string database, string table, string field, string pattern) {
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

double Module::getRealData(string database, string table, string field, string pattern) {
    double data(0);
    int r, i;
    sqlite3 *dbh;
    sqlite3_stmt *stmt;
    if ( sqlite3_open(database.c_str(), &dbh) != SQLITE_OK ) {
        fprintf( stderr, "Could not open database (%s)\n", sqlite3_errmsg(dbh) );
        return(1);
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
