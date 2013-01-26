#include <iostream>
#include <Poco/Thread.h>
#include <Poco/ThreadTarget.h>

#include "UtilsSubsystem/utils.h"
#include "TradeCenter.h"

using namespace std;
//using Poco::Thread;
//using Poco::ThreadTarget;

void TradeCenter::run_backtest()
{

    quantrade::Backtester& backtester = getSubsystem<quantrade::Backtester>();
    logger().information("Loading online backtester module: " + toStr(backtester.name()));
    backtester.online();
}


//TODO Daemon or server app
int TradeCenter::main(const vector<string>& args) {
#ifdef DEBUG
    logger().information("Debug mode activated");
#endif
#ifdef OS_LINUX
    logger().information("Opearting system: Linux");
#endif

    if ( !_helpRequested ) {
        quantrade::DataSubsystem& database = getSubsystem<quantrade::DataSubsystem>();
        logger().information("Connected to database: " + toStr(database.name()));
        //database.test()

        Poco::ThreadTarget ra(&TradeCenter::run_backtest);
        Poco::Thread bt;
        bt.start(ra);
        bt.join();
    }

    return Application::EXIT_OK;
}
