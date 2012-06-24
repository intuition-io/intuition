
#include <stdio.h>
#include <stdlib.h>
#include <sqlite3.h>

sqlite3 *sqliteConnection(char *db) {
    sqlite3 *dbh;
    if ( sqlite3_open(db, &dbh) != SQLITE_OK ) {
        fprintf( stderr, "Can't open database (%s)\n", sqlite3_errmsg(dbh) );
        return(NULL);
    }
    return(dbh);
}

void sqliteRead( sqlite3 *dbh ) {
    int r, i;
    sqlite3_stmt *stmt;
    if ( sqlite3_prepare_v2( dbh, "SELECT ticker, comment FROM stock", 1024, &stmt, NULL ) != SQLITE_OK ) {
        fprintf( stderr, "Didn't get any data\n" );
        exit( EXIT_FAILURE );
    }
    int fields = sqlite3_column_count( stmt );
    /*
     *affichage du header
     */
    for (i = 0; i < fields; i++) 
        printf("%s | ", sqlite3_column_name(stmt, i));
    printf("\n");
    /*
     *affichage des valeurs
     */
    while ( sqlite3_step( stmt ) == SQLITE_ROW ) {
        for (i = 0; i < fields; i++) 
            printf("%s | ", sqlite3_column_text( stmt, i ));
        printf("\n");
    }
    sqlite3_finalize( stmt );
}

void sqliteSelection( sqlite3 *dbh ) {
    char *errmsg;
    char **table;
    int nl, nc;
    int i, j;
    if ( sqlite3_get_table( dbh, "SELECT ticker, rss, comment FROM stocks", &table, &nl, &nc, &errmsg ) != SQLITE_OK ) {
        fprintf( stderr, "Request failled (%s)\n", errmsg ? errmsg : "NULL" );
        sqlite3_free( errmsg );
        return;
    }
    for (i = 0; i < nl; i++) {
        for (j = 0; j < nc; j++) {
            printf("%25s | \n", table[( i+1 ) * nc + j]);
        }
        printf("\n");
    }
    sqlite3_free_table( table );
}

int main(int argc, char *argv[]) {
    char *db = "assets.db";
    sqlite3 *dbh; 
    if ( ( dbh  = sqliteConnection(db) ) == NULL ) 
        fprintf( stderr, "Could not open database\n" );
    sqliteRead( dbh );
    /*sqliteSelection( dbh );*/
    sqlite3_close( dbh );
	return(EXIT_SUCCESS);
}

/*
 *Compilation: gcc csqlite.c -o csqlite -lsqlite3
 */
