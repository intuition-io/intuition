#include <iostream>
#include "../UtilsSubsystem/utils.h"
#include "Backtester.h"

using namespace std;

//TODO: Distributed modules
int Backtester::runLocalModule(string moduleName, vector<string> args) {
  int rc(0);
  logger().information("Runnig sub-program " + moduleName);
  try
  {
    Poco::Pipe outPipe;
    Poco::ProcessHandle ph = Poco::Process::launch(moduleName, args, 0, &outPipe, 0);
    Poco::PipeInputStream istr(outPipe);
    Poco::StreamCopier::copyStream(istr, std::cout);
    rc = ph.wait();
  }
  catch (Poco::SystemException& exc)
  {
    logger().warning(exc.displayText());
  }
  return rc;
}

int Backtester::main(const vector<string>& args) {
#ifdef DEBUG
  logger().information("Debug mode activated");
#endif
#ifdef OS_LINUX
  logger().information("Opearting system: Linux");
#endif

  if ( !_helpRequested ) {
    /*
     *quantrade::DataSubsystem& database = getSubsystem<quantrade::DataSubsystem>();
     *logger().information("Connected to database: " + toStr(database.name()));
     *database.test();
     */

    string prog = config().getString("mod.backtest.script", "backtest.py");
    vector<string> args;
    args.clear();
    args.push_back("--tickers");
    args.push_back(config().getString("mod.backtest.tickers"));
    args.push_back("--algorithm");
    args.push_back(config().getString("mod.backtest.algo", "DualMA"));
    args.push_back("--level");
    args.push_back(config().getString("mod.backtest.level", "critical"));
    args.push_back("--delta");
    args.push_back(config().getString("mod.backtest.delta", "1"));
    args.push_back("--start");
    args.push_back(config().getString("mod.backtest.start", "1/1/2006"));
    args.push_back("--end");
    args.push_back(config().getString("mod.backtest.end", "1/12/2008"));
    int rc = runLocalModule(prog, args);
    if ( rc != 0 )
      logger().error("** Forking " + prog + " failed: " + toStr(rc));
  }
  uninitialize();
  return Application::EXIT_OK;
}
