#include <iostream>
#include "../utils.h"
#include "Test.h"

using namespace std;


//TODO: Distributed modules
int Test::runLocalModule(string moduleName, vector<string> args) {
  int rc(0);
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

int Test::main(const vector<string>& args) {
#ifdef DEBUG
  logger().information("Debug mode activated");
#endif
#ifdef OS_LINUX
  logger().information("Opearting system: Linux");
#endif

  //std::string tmp;
  //cin >> tmp;
  //logger().information("Received: " + tmp);
  if ( !_helpRequested ) {
    // Read config from properti file:
    // Handling a json order
    string command = "{\"name\": \"google\", \"days\": 2, \"deps\": false}";
    quantrade::DataSubsystem& database = getSubsystem<quantrade::DataSubsystem>();
    logger().information("Connected to database: " + toStr(database.name()));
    database.test();

    // Dependancies won't be handle at this time
    
    // Download (data submodule)
    vector<string> args;
    args.push_back("-t");
    args.push_back("google");
    args.push_back("-i");
    args.push_back("3");
    string prog = config().getString("mod.pipeline.file", "pipeline.py");
    int rc = runLocalModule(prog, args);
    if ( rc != 0 )
      logger().error("** Forking failed: " + toStr(rc));

    // Compute (compute submodule)
    args.clear();
    args.push_back("--target");
    args.push_back("archos");
    rc = runLocalModule("./statAndPlot.R", args);
    if ( rc != 0 )
      logger().error("** Forking failed: " + toStr(rc));
  }
  uninitialize();
  return Application::EXIT_OK;
}
